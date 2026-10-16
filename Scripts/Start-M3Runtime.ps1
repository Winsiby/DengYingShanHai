<#
  Start-M3Runtime.ps1
  Third-act standalone packaged runtime launcher (stage 2B, revision R2).

  Fixed package: D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows
  Fixed map:    /Game/DengYingShanHai/Dev/M3/Maps/LV_M3RuntimeCandidate
  Runs the packaged game EXE directly. No Editor, no Python, no .uproject,
  no "latest directory" lookup, no fallback to older packages.

  Modes: normal Play, and -DryRun (read-only, returns before any write).

  R2 corrections (per CODEX-REVIEW-2B-R1):
    1. READY is decided by a testable pure function. Fatal failures are
       detected FIRST and recorded, and never become Ready or a timeout.
    2. Default Run auto-selects the next unused Session-Run<N>; an explicit
       Run must be a positive integer and never overwrites an existing session.
    3. One consistent failure exit prints full evidence (reason, PID, log path,
       real game exit code when available) before returning non-zero.
    4. No ExecutionPolicy flag anywhere; the plain -NoProfile -File call works.

  Approved stage 2B write whitelist:
    Start-M3Runtime.cmd + Scripts\Start-M3Runtime.ps1

  2026-10-09 runtime correction: share the live log with the UE writer.
  Preserve read errors in failure evidence; READY and exit rules are unchanged.
#>
[CmdletBinding()]
param(
  # Strict positive integer. OMITTED means "auto-select the next unused
  # Session-Run<N>". An explicitly supplied value <= 0 is rejected in BOTH
  # DryRun and Play, so -DryRun -Run 0 and -DryRun -Run -1 can never be
  # silently treated as auto-selection.
  [int]$Run = 0,
  [switch]$DryRun
)

# R3: one gate shared by DryRun and Play. $PSBoundParameters is the binder's
# own record of what the caller actually supplied, so "-Run 0" and "-Run -1"
# are distinguishable from omitting -Run entirely.
$RunWasExplicitlyGiven = $PSBoundParameters.ContainsKey('Run')

# NOTE: $ErrorActionPreference stays 'Continue' on purpose. R1 used 'Stop',
# which made Write-Error terminate the script before its own documented exit
# codes and evidence could be emitted. Every failure path now prints evidence
# and returns explicitly.
$ErrorActionPreference = 'Continue'

# --- Fixed identities ------------------------------------------------------
$PackageWindows = 'D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows'
$InnerExe       = Join-Path $PackageWindows 'DengYingShanHai\Binaries\Win64\DengYingShanHai.exe'
$TargetMap      = 'LV_M3RuntimeCandidate'
$MapPackagePath = '/Game/DengYingShanHai/Dev/M3/Maps/LV_M3RuntimeCandidate'
$GameModeClass  = 'BP_DYP03RuntimeGameMode_C'

# Approved single argv for this new Dev entry only.
$OnePassProjectionArg = '-ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"'

$AuditSessionRoot = 'D:\灯影山海\Saved\Audit-2026-10-07-WB-P03Launcher'
$StartupObservationSeconds = 120

$RequiredIdentities = @(
  @{ Label='bootstrap';   Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai.exe';                                Bytes=171520;    SHA256='46301CB8E69CAAA5030C008CD2B989A51E72C8BB9507A3955D105118F750B9BB' },
  @{ Label='innerExe';    Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\Binaries\Win64\DengYingShanHai.exe'; Bytes=332700160; SHA256='EF5A3DD45E0932380C0E57E3A085E119478FD09EA51026BD74188214FAAF1309' },
  @{ Label='projectPak';  Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\Content\Paks\DengYingShanHai-Windows.pak';  Bytes=11229703;  SHA256='2BF32EFA5243C7FA1F5CF43C010F3DCF5996A2CBECAC89B056A9936850220CE3' },
  @{ Label='projectUcas'; Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\Content\Paks\DengYingShanHai-Windows.ucas'; Bytes=213561168; SHA256='9CD77315D604E47D8E37CF32836D51E1A4A82A3889086ABD537E64C17FCC5A2E' },
  @{ Label='projectUtoc'; Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\Content\Paks\DengYingShanHai-Windows.utoc'; Bytes=194288;    SHA256='5DDFAAB037FA5EF245D41B0E5D988A9882EF7E9FE023C945CF879104527EABEB' },
  @{ Label='globalUcas';  Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\Content\Paks\global.ucas';                 Bytes=3220896;   SHA256='5657C0469BA3F605CF6DB603B6E69A3A2FB4FB43E3F3D4EFF26BC380E83F137C' },
  @{ Label='globalUtoc';  Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\Content\Paks\global.utoc';                 Bytes=794;       SHA256='F20C346A14656CFBBEA39A624389B7A9233539F1B51459B6DE8F83E3341D9297' },
  @{ Label='fontLicense'; Path='D:\灯影山海\Builds\M3Runtime-20261007-Run1\Windows\DengYingShanHai\LICENSES\SourceHanSans\LICENSE.txt';       Bytes=4463;      SHA256='FCAC737E761EC63DBFBDCE11030A1780161920D80315EDBA9C8BEFF1C2BAC5A2' }
)

# ======================================================================
# Pure, testable helpers (no process, no IO, no state)
# ======================================================================

# Selects the run number. Explicit positive integer wins; 0 means next unused.
function Select-RunNumber {
  param([int]$Requested, [int[]]$UsedNumbers, [int]$MaxProbe = 1000)
  if ($Requested -gt 0) { return $Requested }
  for ($i = 1; $i -le $MaxProbe; $i++) {
    if ($UsedNumbers -notcontains $i) { return $i }
  }
  return 0
}

# Core READY / fatal decision over one log text. Pure.
# R3: the map test is anchored on the FROZEN full package path, not on a
# basename. Real engine output (see existing LiveMap-Run3.log) is:
#   LogWorld: Bringing World /Game/.../LV_M3RuntimeCandidate.LV_M3RuntimeCandidate up for play ...
#   LogGlobalStatus: UEngine::LoadMap Load map complete /Game/.../LV_M3RuntimeCandidate
# so the world line carries the package plus the .Object form, and the
# completion line carries the bare package. Both are accepted; a same-named
# map in another folder, or a _OLD variant, is not.
function Test-TargetMapPath {
  param([string]$ObservedUrl, [string]$TargetPackagePath, [string]$TargetMapName)
  if ([string]::IsNullOrWhiteSpace($ObservedUrl)) { return $false }
  # Strip any URL options / query part explicitly.
  $url = $ObservedUrl.Trim()
  $q = $url.IndexOf('?')
  if ($q -ge 0) { $url = $url.Substring(0, $q) }
  $url = $url.TrimEnd('/')
  if ($url -eq $TargetPackagePath) { return $true }
  # The package-qualified object form: <package>.<ObjectName>
  if ($url -eq ($TargetPackagePath + '.' + $TargetMapName)) { return $true }
  return $false
}

function Get-StartupDecision {
  param(
    [string]$LogText,
    [string]$TargetPackagePath,
    [string]$TargetMapName,
    [string]$GameModeName
  )
  $text = if ($null -eq $LogText) { '' } else { $LogText }

  # --- 1. Fatal first. A fatal error can never become Ready or a timeout. ---
  $fatal = $false; $fatalReason = ''
  if ($text -match 'Fatal error') {
    $fatal = $true; $fatalReason = 'Fatal error'
    if ($text -match 'Fatal error:\s*\[?([^\]\r\n]{0,200})') { $fatalReason = "Fatal error: $($Matches[1].Trim())" }
  } elseif ($text -match '=== Critical error ===') {
    $fatal = $true; $fatalReason = '=== Critical error ==='
  } elseif ($text -match 'Unhandled Exception') {
    $fatal = $true; $fatalReason = 'Unhandled Exception'
  } elseif ($text -match 'GPU crash|DXGI_ERROR_DEVICE_REMOVED') {
    $fatal = $true; $fatalReason = 'graphics device failure marker'
  }
  if ($fatal) {
    return [ordered]@{ Ready=$false; Fatal=$true; Reason=$fatalReason; GameClass=$false; WorldUp=$false; LoadComplete=$false }
  }

  # --- 2. Game class: scan every marker, like World and complete -----------
  # R4: a single-match test let an unrelated first class line reject the run
  # before the real target class was seen. Scan all reported classes and accept
  # only when the FROZEN target class is among them; reject only when class
  # markers exist and none of them is the target. No wider class set.
  $gameClass = $false
  $sawGameClass = $false
  $classNames = @()
  foreach ($m in [regex]::Matches($text, "Game class is '([^']+)'")) {
    $sawGameClass = $true
    $reported = $m.Groups[1].Value
    $classNames += $reported
    $leaf = $reported
    if ($leaf -match '/Script/') { $leaf = ($leaf -split '/Script/')[-1] }
    $leaf = ($leaf -split '\.')[-1]
    if ($leaf -eq $GameModeName) { $gameClass = $true }
  }
  if ($sawGameClass -and -not $gameClass) {
    return [ordered]@{ Ready=$false; Fatal=$false; Reason=("GameMode mismatch: reported class(es) '" + ($classNames -join "', '") + "' do not include the frozen target"); GameClass=$false; WorldUp=$false; LoadComplete=$false }
  }

  # --- 3. Scan the ACTUAL target world line (not the first unrelated one) --
  # Iterate every match so an earlier Engine Entry "Bringing World" line
  # cannot satisfy or break the target check.
  $worldUp = $false
  $sawAnyWorldLine = $false
  $worldUrls = @()
  foreach ($m in [regex]::Matches($text, 'Bringing World\s+(\S+)\s+up for play')) {
    $sawAnyWorldLine = $true
    $worldUrls += $m.Groups[1].Value
    if (Test-TargetMapPath -ObservedUrl $m.Groups[1].Value -TargetPackagePath $TargetPackagePath -TargetMapName $TargetMapName) {
      $worldUp = $true
    }
  }
  if ($sawAnyWorldLine -and -not $worldUp) {
    return [ordered]@{ Ready=$false; Fatal=$false; Reason=("World mismatch: up-for-play URL(s) '" + ($worldUrls -join "', '") + "' are not the frozen target"); GameClass=$gameClass; WorldUp=$false; LoadComplete=$false }
  }

  # --- 4. Exact target load-complete --------------------------------------
  $loadComplete = $false
  $sawComplete = $false
  $completeUrls = @()
  foreach ($m in [regex]::Matches($text, 'Load map complete\s+(\S+)')) {
    $sawComplete = $true
    $completeUrls += $m.Groups[1].Value
    if (Test-TargetMapPath -ObservedUrl $m.Groups[1].Value -TargetPackagePath $TargetPackagePath -TargetMapName $TargetMapName) {
      $loadComplete = $true
    }
  }
  if ($sawComplete -and -not $loadComplete) {
    return [ordered]@{ Ready=$false; Fatal=$false; Reason=("Load-complete mismatch: '" + ($completeUrls -join "', '") + "' is not the frozen target"); GameClass=$gameClass; WorldUp=$worldUp; LoadComplete=$false }
  }

  $ready = ($gameClass -and $worldUp -and $loadComplete)
  $reason = if ($ready) { 'all exact startup markers present in the same log for the frozen target map' }
            elseif (-not $gameClass) { 'Game class marker not seen yet' }
            elseif (-not $worldUp)    { 'target world up-for-play not seen yet' }
            else                     { 'target load map complete not seen yet' }
  return [ordered]@{ Ready=$ready; Fatal=$false; Reason=$reason; GameClass=$gameClass; WorldUp=$worldUp; LoadComplete=$loadComplete }
}

# Read one live-log snapshot without excluding the UE process's write handle.
# IO errors propagate to the caller; a failed read is never a valid empty log.
function Read-SharedGameLog {
  param([string]$Path)
  $stream = [System.IO.File]::Open($Path,
    [System.IO.FileMode]::Open,
    [System.IO.FileAccess]::Read,
    [System.IO.FileShare]::ReadWrite)
  $reader = $null
  try {
    $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8, $true)
    return $reader.ReadToEnd()
  } finally {
    if ($null -ne $reader) { $reader.Dispose() }
    else { $stream.Dispose() }
  }
}

# Full failure evidence printed before every non-zero return.
function Format-FailureEvidence {
  param([string]$Kind, [string]$Reason, $Proc, [string]$LogPath, [string]$Detail)
  $lines = @()
  $lines += '--- FAILURE EVIDENCE ---'
  $lines += ("KIND        : {0}" -f $Kind)
  $lines += ("REASON      : {0}" -f $Reason)
  if ($null -ne $Proc) {
    $lines += ("PID         : {0}" -f $Proc.Id)
    try { $lines += ("HAS_EXITED  : {0}" -f $Proc.HasExited) } catch { }
    if ($Proc.HasExited) {
      try {
        $ec = $Proc.ExitCode
        if ($null -eq $ec) { $lines += 'GAME_EXITCODE : (unavailable, null - not coerced)' }
        else { $lines += ("GAME_EXITCODE : {0}" -f $ec) }
      } catch { $lines += 'GAME_EXITCODE : (read failed - not coerced)' }
    }
  } else {
    $lines += 'PID         : (process not started)'
  }
  if ($LogPath) { $lines += ("LOG         : {0}" -f $LogPath) } else { $lines += 'LOG         : (none)' }
  if ($Detail) {
    foreach ($d in ($Detail -split "`r?`n")) { if ($d) { $lines += ("DETAIL      : {0}" -f $d) } }
  }
  $lines += '--------------------------'
  return ($lines -join "`r`n")
}

function Get-Sha256Upper([string]$Path) {
  $sha = [System.Security.Cryptography.SHA256]::Create()
  try {
    $fs = [System.IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($sha.ComputeHash($fs))).Replace('-', '') }
    finally { $fs.Dispose() }
  } finally { $sha.Dispose() }
}

function Test-PackageIdentity {
  $problems = @()
  foreach ($item in $RequiredIdentities) {
    if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf)) { $problems += ("MISSING  {0}  {1}" -f $item.Label, $item.Path); continue }
    $actualBytes = (Get-Item -LiteralPath $item.Path).Length
    if ($actualBytes -ne [long]$item.Bytes) { $problems += ("BYTES    {0}  expected {1} actual {2}" -f $item.Label, $item.Bytes, $actualBytes); continue }
    $actualSha = Get-Sha256Upper $item.Path
    if ($actualSha -ne $item.SHA256.ToUpperInvariant()) { $problems += ("SHA256   {0}  expected {1} actual {2}" -f $item.Label, $item.SHA256.ToUpperInvariant(), $actualSha) }
  }
  return $problems
}

# Reads the used session numbers under a given root. Pure w.r.t. the caller's
# choice of root, so the isolated fixture can exercise the real reader without
# touching the real session directory.
# R4 control contract for one observation step. Pure: it takes the current
# decision, whether the process is still alive, and the freshly read log text,
# and returns what the launcher is allowed to conclude.
#   Alive + Ready markers  -> Ready is allowed (announce only if alive)
#   Exited + markers       -> NOT ready; classify Fatal first, else EarlyExit
#   Exited + final Fatal  -> Fatal wins even if earlier markers were complete
# No process, file or state access happens here.
function Get-ObservationOutcome {
  param(
    [bool]$IsAlive,
    [string]$LogText,
    [string]$TargetPackagePath,
    [string]$TargetMapName,
    [string]$GameModeName
  )
  # Always re-read the log text as it is right now. After an exit this is the
  # FINAL log, so a Fatal written just before exiting is not lost.
  $d = Get-StartupDecision -LogText $LogText -TargetPackagePath $TargetPackagePath -TargetMapName $TargetMapName -GameModeName $GameModeName
  if (-not $IsAlive) {
    # Process already gone: never announce Ready, whatever the markers say.
    if ($d.Fatal) {
      return [ordered]@{ Outcome='Fatal'; Ready=$false; Reason=$d.Reason; Decision=$d }
    }
    return [ordered]@{ Outcome='EarlyExit'; Ready=$false; Reason=('process exited before READY (' + $d.Reason + ')'); Decision=$d }
  }
  if ($d.Fatal) { return [ordered]@{ Outcome='Fatal'; Ready=$false; Reason=$d.Reason; Decision=$d } }
  if ($d.Ready) { return [ordered]@{ Outcome='Ready'; Ready=$true; Reason=$d.Reason; Decision=$d } }
  return [ordered]@{ Outcome='Waiting'; Ready=$false; Reason=$d.Reason; Decision=$d }
}

function Get-UsedRunNumbersFrom {
  param([string]$Root)
  $used = @()
  if (Test-Path -LiteralPath $Root) {
    $used = @(Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -match '^Session-Run(\d+)$' } |
      ForEach-Object { [int]$Matches[1] })
  }
  return $used
}

function Get-UsedRunNumbers {
  return (Get-UsedRunNumbersFrom -Root $AuditSessionRoot)
}

function Get-LaunchPlan {
  param([int]$EffectiveRun)
  $sessionDir = Join-Path $AuditSessionRoot ("Session-Run{0}" -f $EffectiveRun)
  $sessionLog = Join-Path $sessionDir ("Game-Run{0}.log" -f $EffectiveRun)
  [ordered]@{
    Run                       = $EffectiveRun
    RunWasExplicit            = $RunWasExplicitlyGiven
    DryRun                    = [bool]$DryRun
    PackageWindows            = $PackageWindows
    InnerExe                  = $InnerExe
    WorkingDirectory          = $PackageWindows
    MapPackagePath            = $MapPackagePath
    TargetMap                 = $TargetMap
    GameModeClass             = $GameModeClass
    ForceDPCVarsArg           = $OnePassProjectionArg
    SessionLogDirectoryPlan   = $sessionDir
    SessionLogPlan            = $sessionLog
    AbsLogArgPlan             = ('-abslog="{0}"' -f $sessionLog)
    # R3: the plan states the exact three argv that WOULD be used, so the
    # caller can record the final Arguments string. A plan is not Ready.
    ArgvPlan                  = @($MapPackagePath, $OnePassProjectionArg, ('-abslog="{0}"' -f $sessionLog))
    FinalArgumentsPlan        = ((@($MapPackagePath, $OnePassProjectionArg, ('-abslog="{0}"' -f $sessionLog))) -join ' ')
    StartupObservationSeconds = $StartupObservationSeconds
    RhiThreadPolicy           = 'normal RHI and RHI thread; no NullRHI, no D3D11, no norhithread'
  }
}

# ======================================================================
# DryRun: returns BEFORE any write, child process or configuration change.
# Plan output, not Ready. Creates no file, directory or log.
# ======================================================================
if ($DryRun) {
  # R3: the explicit-Run gate runs BEFORE any auto-selection, so -DryRun
  # -Run 0 and -DryRun -Run -1 are rejected here exactly as in Play.
  if ($RunWasExplicitlyGiven -and $Run -le 0) {
    Write-Output '=== DRY RUN (read-only; PLAN only, not Ready) ==='
    Write-Output (Format-FailureEvidence -Kind 'RunNumber' -Reason ("-Run was explicitly supplied but must be a positive integer; got {0}" -f $Run) -Proc $null -LogPath $null -Detail 'Omit -Run entirely to let the launcher auto-select the next unused session number.')
    Write-Output 'RESULT = NoLaunchPlan (invalid explicit Run; nothing started, nothing written)'
    exit 5
  }
  $used = Get-UsedRunNumbers
  $effectiveRun = Select-RunNumber -Requested $(if ($RunWasExplicitlyGiven) { $Run } else { 0 }) -UsedNumbers $used
  Write-Output '=== DRY RUN (read-only; PLAN only, not Ready) ==='
  if ($effectiveRun -le 0) {
    Write-Output 'RESULT = Plan (no unused run number available)'
    Write-Output (Format-FailureEvidence -Kind 'RunNumber' -Reason 'no unused Session-Run<N> available' -Proc $null -LogPath $null -Detail $null)
    exit 5
  }
  $plan = Get-LaunchPlan -EffectiveRun $effectiveRun
  # R3: an explicit Run that is already taken must be reported as a refusal,
  # not as a valid plan -- and DryRun must not create or touch anything.
  if ($RunWasExplicitlyGiven -and (Test-Path -LiteralPath $plan.SessionLogDirectoryPlan)) {
    Write-Output ('PLAN.Run                       = {0}' -f $plan.Run)
    Write-Output ('PLAN.RunWasExplicit            = {0}' -f $plan.RunWasExplicit)
    Write-Output (Format-FailureEvidence -Kind 'SessionConflict' -Reason ("explicit -Run {0} already exists; refusing to overwrite" -f $effectiveRun) -Proc $null -LogPath $plan.SessionLogPlan -Detail $plan.SessionLogDirectoryPlan)
    Write-Output 'RESULT = NoLaunchPlan (session conflict; nothing started, nothing written)'
    exit 5
  }
  Write-Output ('PLAN.Run                       = {0}' -f $plan.Run)
  Write-Output ('PLAN.RunWasExplicit            = {0}' -f $plan.RunWasExplicit)
  Write-Output ('PLAN.UsedRunNumbers            = {0}' -f ((($used | Sort-Object) -join ',')))
  Write-Output ('PLAN.NextRunSelection          = {0}' -f $(if ($Run -gt 0) { 'explicit positive integer used as-is' } else { 'next unused Session-Run<N> chosen read-only' }))
  Write-Output ('PLAN.PackageWindows            = {0}' -f $plan.PackageWindows)
  Write-Output ('PLAN.InnerExe                  = {0}' -f $plan.InnerExe)
  Write-Output ('PLAN.WorkingDirectory          = {0}' -f $plan.WorkingDirectory)
  Write-Output ('PLAN.MapPackagePath            = {0}' -f $plan.MapPackagePath)
  Write-Output ('PLAN.TargetMap                 = {0}' -f $plan.TargetMap)
  Write-Output ('PLAN.GameModeClass             = {0}' -f $plan.GameModeClass)
  Write-Output ('PLAN.ForceDPCVarsArg           = {0}' -f $plan.ForceDPCVarsArg)
  Write-Output ('PLAN.SessionLogDirectoryPlan   = {0}' -f $plan.SessionLogDirectoryPlan)
  Write-Output ('PLAN.SessionLogPlan            = {0}' -f $plan.SessionLogPlan)
  Write-Output ('PLAN.AbsLogArgPlan             = {0}' -f $plan.AbsLogArgPlan)
  Write-Output 'PLAN.ArgvPlan (exactly the three argv that WOULD be used; a plan is NOT Ready):'
  foreach ($a in $plan.ArgvPlan) { Write-Output ('PLAN.Argv                      = {0}' -f $a) }
  Write-Output ('PLAN.FinalArgumentsPlan       = {0}' -f $plan.FinalArgumentsPlan)
  Write-Output ('PLAN.StartupObservationSeconds = {0}' -f $plan.StartupObservationSeconds)
  Write-Output ('PLAN.RhiThreadPolicy           = {0}' -f $plan.RhiThreadPolicy)
  Write-Output 'PLAN.ReadyMarkersRequired (all three, same log, exact):'
  Write-Output ("PLAN.ReadyMarker               = Game class is '{0}'" -f $plan.GameModeClass)
  Write-Output ("PLAN.ReadyMarker               = Bringing World <...{0}...> up for play" -f $plan.TargetMap)
  Write-Output ("PLAN.ReadyMarker               = Load map complete <...{0}...>" -f $plan.TargetMap)
  Write-Output 'PLAN.FatalPolicy               = fatal markers are checked FIRST and never become Ready or timeout'
  Write-Output 'IDENTITY CHECK (read-only):'
  $problems = Test-PackageIdentity
  if ($problems.Count -eq 0) {
    Write-Output ('IDENTITY.AllMatch              = True ({0} items)' -f $RequiredIdentities.Count)
    foreach ($item in $RequiredIdentities) {
      Write-Output ('IDENTITY.OK                    = {0} | {1} | {2} bytes' -f $item.Label, (Split-Path $item.Path -Leaf), (Get-Item -LiteralPath $item.Path).Length)
    }
    Write-Output 'RESULT = Plan'
    exit 0
  }
  Write-Output (Format-FailureEvidence -Kind 'Identity' -Reason 'package identity does not match the frozen bindings' -Proc $null -LogPath $null -Detail ($problems -join "`r`n"))
  Write-Output 'RESULT = Plan (identity mismatch; refusing to launch)'
  exit 3
}

# ======================================================================
# Real Play
# ======================================================================
Write-Output '=== RUNTIME LAUNCH (third act packaged candidate) ==='

if ($RunWasExplicitlyGiven -and $Run -le 0) {
  Write-Output (Format-FailureEvidence -Kind 'RunNumber' -Reason ("-Run was explicitly supplied but must be a positive integer; got {0}" -f $Run) -Proc $null -LogPath $null -Detail 'Omit -Run entirely to let the launcher auto-select the next unused session number.')
  exit 5
}
$used = Get-UsedRunNumbers
$effectiveRun = Select-RunNumber -Requested $(if ($RunWasExplicitlyGiven) { $Run } else { 0 }) -UsedNumbers $used
if ($effectiveRun -le 0) {
  Write-Output (Format-FailureEvidence -Kind 'RunNumber' -Reason 'no unused Session-Run<N> available' -Proc $null -LogPath $null -Detail ("Used: " + (($used | Sort-Object) -join ',')))
  exit 5
}
$plan = Get-LaunchPlan -EffectiveRun $effectiveRun
$sessionDir = $plan.SessionLogDirectoryPlan
$logPath    = $plan.SessionLogPlan

Write-Output ('RUN     : {0}  (explicit={1})' -f $plan.Run, $plan.RunWasExplicit)
Write-Output ('PACKAGE : {0}' -f $PackageWindows)
Write-Output ('EXE     : {0}' -f $InnerExe)
Write-Output ('MAP     : {0}' -f $plan.MapPackagePath)
Write-Output ('RHI     : normal RHI / RHI thread (no NullRHI, no norhithread)')

# R3: an explicit Run must never overwrite an existing session.
if ($RunWasExplicitlyGiven -and (Test-Path -LiteralPath $sessionDir)) {
  Write-Output (Format-FailureEvidence -Kind 'SessionConflict' -Reason ("explicit -Run {0} already exists; refusing to overwrite" -f $effectiveRun) -Proc $null -LogPath $null -Detail $sessionDir)
  exit 5
}
# R3 fail-closed: the auto-selected leaf must also be absent. Never use -Force,
# never clean an old directory, and treat any creation error as fatal so the
# game can never start without its session directory.
if (Test-Path -LiteralPath $sessionDir) {
  Write-Output (Format-FailureEvidence -Kind 'SessionConflict' -Reason ("selected session directory already exists; refusing to reuse or overwrite" -f '') -Proc $null -LogPath $null -Detail $sessionDir)
  exit 5
}

if (-not (Test-Path -LiteralPath $InnerExe -PathType Leaf)) {
  Write-Output (Format-FailureEvidence -Kind 'MissingExe' -Reason 'inner executable not found' -Proc $null -LogPath $null -Detail $InnerExe)
  exit 4
}

Write-Output 'VERIFYING PACKAGE IDENTITY (8 items)...'
$problems = Test-PackageIdentity
if ($problems.Count -gt 0) {
  Write-Output (Format-FailureEvidence -Kind 'Identity' -Reason 'package identity does not match the frozen bindings; refusing to launch' -Proc $null -LogPath $null -Detail ($problems -join "`r`n"))
  exit 3
}
Write-Output 'IDENTITY: all 8 items match the frozen bindings.'

# R3 fail-closed directory creation: no -Force, terminating error action, and
# a try/catch so a failure prints full evidence and returns non-zero WITHOUT
# ever reaching the game start below.
$dirCreated = $false
try {
  $null = New-Item -ItemType Directory -Path $sessionDir -ErrorAction Stop
  $dirCreated = $true
} catch {
  Write-Output (Format-FailureEvidence -Kind 'SessionDirFailed' -Reason ('could not create the session directory; refusing to start the game: ' + $_.Exception.Message) -Proc $null -LogPath $logPath -Detail $sessionDir)
  exit 5
}
if (-not $dirCreated -or -not (Test-Path -LiteralPath $sessionDir)) {
  Write-Output (Format-FailureEvidence -Kind 'SessionDirFailed' -Reason 'session directory is absent after creation; refusing to start the game' -Proc $null -LogPath $logPath -Detail $sessionDir)
  exit 5
}
Write-Output ('SESSDIR: created {0}' -f $sessionDir)

$argv = @($plan.MapPackagePath, $OnePassProjectionArg, ('-abslog="{0}"' -f $logPath))
Write-Output ('ARGV    : {0}' -f ($argv -join ' '))

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName         = $InnerExe
$psi.Arguments        = ($argv -join ' ')
$psi.WorkingDirectory = $PackageWindows
$psi.UseShellExecute  = $false

Write-Output 'STARTING GAME PROCESS (visible window)...'
$proc = $null
$startedUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
try {
  $proc = New-Object System.Diagnostics.Process
  $proc.StartInfo = $psi
  $null = $proc.Start()
} catch {
  Write-Output (Format-FailureEvidence -Kind 'StartFailed' -Reason ('process start threw: ' + $_.Exception.Message) -Proc $null -LogPath $logPath -Detail $null)
  exit 4
}
Write-Output ('PID     : {0}' -f $proc.Id)
Write-Output ('START_UTC: {0}' -f $startedUtc)
Write-Output ('LOG     : {0}' -f $logPath)

# --- Startup observation -------------------------------------------------
# R4 order per observation step: read the CURRENT log, classify, and only
# announce Ready while the process is still alive. Once the process has exited
# the log is read one final time so a Fatal written just before exiting is
# classified as Fatal rather than reported as a bare EarlyExit.
$deadline = (Get-Date).AddSeconds($StartupObservationSeconds)
$outcome = [ordered]@{ Outcome='Waiting'; Ready=$false; Reason='no observation yet'; Decision=$null }
$alive = $true
$announcedReady = $false
$lastLogReadError = $null

while ($true) {
  $text = ''
  if (Test-Path -LiteralPath $logPath) {
    try {
      $text = Read-SharedGameLog -Path $logPath
      $lastLogReadError = $null
    } catch {
      $lastLogReadError = $_.Exception.Message
      $text = ''
    }
  }
  $alive = -not $proc.HasExited
  $outcome = Get-ObservationOutcome -IsAlive $alive -LogText $text `
    -TargetPackagePath $MapPackagePath -TargetMapName $TargetMap -GameModeName $GameModeClass
  if ($outcome.Outcome -ne 'Waiting') { break }
  if (-not $alive) { break }
  if ((Get-Date) -ge $deadline) { break }
  Start-Sleep -Milliseconds 500
}

# If we stopped because the process is gone, take one more final read so the
# classification uses the log exactly as it ended.
if (-not $alive) {
  $finalText = ''
  if (Test-Path -LiteralPath $logPath) {
    try {
      $finalText = Read-SharedGameLog -Path $logPath
      $lastLogReadError = $null
    } catch {
      $lastLogReadError = $_.Exception.Message
      $finalText = ''
    }
  }
  $outcome = Get-ObservationOutcome -IsAlive $false -LogText $finalText `
    -TargetPackagePath $MapPackagePath -TargetMapName $TargetMap -GameModeName $GameModeClass
  $text = $finalText
}

$decision = $outcome.Decision
if ($null -eq $decision) {
  $decision = [ordered]@{ Ready=$false; Fatal=$false; Reason='no decision'; GameClass=$false; WorldUp=$false; LoadComplete=$false }
}

$observedUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
Write-Output ('OBSERVED_UTC     : {0}' -f $observedUtc)
Write-Output ('OUTCOME          : {0}' -f $outcome.Outcome)
Write-Output ('PROCESS_ALIVE    : {0}' -f $alive)
Write-Output ('DECISION.Ready   : {0}' -f $decision.Ready)
Write-Output ('DECISION.Fatal   : {0}' -f $decision.Fatal)
Write-Output ('DECISION.Reason  : {0}' -f $decision.Reason)
Write-Output ('MARKER.GameClass : {0}' -f $decision.GameClass)
Write-Output ('MARKER.WorldUp   : {0}' -f $decision.WorldUp)
Write-Output ('MARKER.LoadCompl : {0}' -f $decision.LoadComplete)

if ($outcome.Outcome -eq 'Fatal') {
  Write-Output (Format-FailureEvidence -Kind 'Fatal' -Reason $outcome.Reason -Proc $proc -LogPath $logPath -Detail $null)
  Write-Output 'Not killing the process and not starting a second instance.'
  exit 9
}
if ($outcome.Outcome -eq 'EarlyExit') {
  Write-Output (Format-FailureEvidence -Kind 'EarlyExit' -Reason $outcome.Reason -Proc $proc -LogPath $logPath -Detail $lastLogReadError)
  exit 6
}
if ($outcome.Outcome -ne 'Ready') {
  $timeoutDetail = 'The game may still be running. Not killing it and not starting a second instance; close it yourself if needed.'
  if ($lastLogReadError) { $timeoutDetail += "`r`nLast log read failed: " + $lastLogReadError }
  Write-Output (Format-FailureEvidence -Kind 'StartupTimeout' -Reason ("READY not observed within {0}s ({1})" -f $StartupObservationSeconds, $outcome.Reason) -Proc $proc -LogPath $logPath -Detail $timeoutDetail)
  exit 7
}

# R4: Ready is announced only after confirming the process is still alive.
if (-not $alive) {
  Write-Output (Format-FailureEvidence -Kind 'EarlyExit' -Reason 'process is no longer alive; refusing to announce READY' -Proc $proc -LogPath $logPath -Detail $null)
  exit 6
}
$announcedReady = $true
Write-Output 'READY. All three exact startup markers observed in the same new log while the process is alive.'
Write-Output 'READY_IS_ONLY_MAP_START_EVIDENCE: it does not prove GPU stability or level completion.'
Write-Output 'The game window stays visible. Close it normally to finish.'

$proc.WaitForExit()
$realExit = $proc.ExitCode
if ($null -eq $realExit) {
  Write-Output (Format-FailureEvidence -Kind 'NoGameExitCode' -Reason 'game exit code unavailable (null); not coerced to 0' -Proc $proc -LogPath $logPath -Detail $null)
  exit 8
}
Write-Output ('GAME_EXITCODE     : {0}' -f $realExit)
exit $realExit
