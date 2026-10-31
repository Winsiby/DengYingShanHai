[CmdletBinding()]
param([switch]$DryRun, [ValidatePattern('^Run[1-9][0-9]*$')][string]$Run)
$ErrorActionPreference = 'Stop'
$taskAlias = 'C:\UEProjects\DengYingShanHai'
$taskActual = 'D:\' + (-join [char[]]@(0x706F,0x5F71,0x5C71,0x6D77))
$taskJunction = Get-Item -LiteralPath $taskAlias
if ($taskJunction.LinkType -ne 'Junction' -or [string](@($taskJunction.Target)[0]) -ne $taskActual) {
    throw 'Unexpected project junction. No game was launched.'
}
$taskInvocationRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if ($taskInvocationRoot -ne $taskActual -and $taskInvocationRoot -ne $taskAlias) { throw 'Use the current D-drive project.' }
$taskEditor = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskProject = Join-Path $taskAlias 'DengYingShanHai.uproject'
$taskScript = Join-Path $taskAlias 'Scripts\Watch-P03RuntimeTest.py'
$taskAudit = Join-Path $taskAlias 'Saved\Audit-2026-10-09-M3VisibleAutoTest'
foreach ($taskPath in @($taskEditor, $taskProject, $taskScript,
    (Join-Path $taskAlias 'Binaries\Win64\UnrealEditor-DengYingShanHai.dll'),
    (Join-Path $taskAlias 'Content\DengYingShanHai\Dev\M3\Maps\LV_M3RuntimeCandidate.umap'))) {
    if (-not (Test-Path -LiteralPath $taskPath -PathType Leaf)) { throw ('Missing: ' + $taskPath) }
}
if (-not $Run) {
    $taskNumber = 1
    while (Test-Path -LiteralPath (Join-Path $taskAudit ('Run' + $taskNumber))) { $taskNumber++ }
    $Run = 'Run' + $taskNumber
}
$taskOutput = Join-Path $taskAudit $Run
if (Test-Path -LiteralPath $taskOutput) { throw 'Existing run evidence is preserved. Choose a new run.' }
$taskLog = Join-Path $taskOutput 'Session.log'
$taskArguments = @(
    ('"' + $taskProject + '"'),
    ('-ExecutePythonScript="' + $taskScript + '"'),
    '-nosplash',
    ('-abslog="' + $taskLog + '"'),
    '-ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"'
)
$taskReport = [ordered]@{
    Mode = 'VisibleEditorAutomaticTest'; Run = $Run; Output = $taskOutput
    Editor = $taskEditor; Arguments = $taskArguments; WindowStyle = 'Normal'
    EditorOnly = $true; PackageTested = $false; PhysicalKeysVerified = $false
    ProductDataChanged = $false; ProcessId = $null; ActualProcessExitCode = $null
    FinalPictureRetained = $true
}
if ($DryRun) { $taskReport | ConvertTo-Json -Depth 5; return }
$taskLiveUE = @(Get-Process -Name UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue)
if ($taskLiveUE.Count -gt 0) {
    throw 'Close existing UE Editor sessions first. They were left untouched.'
}
New-Item -ItemType Directory -Path $taskOutput | Out-Null

function Read-TaskEvents {
    $taskEventPath = Join-Path $taskOutput 'Events.jsonl'
    if (-not (Test-Path -LiteralPath $taskEventPath)) { return @() }
    $taskFile = $null
    $taskReader = $null
    try {
        $taskFile = [IO.FileStream]::new($taskEventPath, [IO.FileMode]::Open, [IO.FileAccess]::Read,
            [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
        $taskReader = [IO.StreamReader]::new($taskFile, [Text.Encoding]::UTF8)
        $taskText = $taskReader.ReadToEnd()
        foreach ($taskLine in ($taskText -split "`n")) {
            if ([string]::IsNullOrWhiteSpace($taskLine)) { continue }
            try { $taskLine | ConvertFrom-Json -ErrorAction Stop } catch { }
        }
    } finally {
        if ($null -ne $taskReader) { $taskReader.Dispose() }
        elseif ($null -ne $taskFile) { $taskFile.Dispose() }
    }
}

$taskPreviousOutput = [Environment]::GetEnvironmentVariable('DY_P03_VISIBLE_TEST_OUT', 'Process')
try {
    [Environment]::SetEnvironmentVariable('DY_P03_VISIBLE_TEST_OUT', $taskOutput, 'Process')
    Write-Host 'Opening the visible UE Editor test. Wait for the actual game viewport.'
    Write-Host 'Watch two automatic runs: light -> puppet -> hold -> drop -> forest -> reset -> replay.'
    Write-Host 'Do not press gameplay keys during the automatic test. The final picture stays open.'
    Write-Host ('Evidence: ' + $taskOutput)
    $taskProcess = Start-Process -FilePath $taskEditor -ArgumentList $taskArguments -WindowStyle Normal -PassThru `
        -RedirectStandardOutput (Join-Path $taskOutput 'Stdout.log') -RedirectStandardError (Join-Path $taskOutput 'Stderr.log')
    $taskReport.ProcessId = $taskProcess.Id
    $taskClock = [Diagnostics.Stopwatch]::StartNew()
    $taskReady = $false
    $taskLastStep = ''
    while ($true) {
        $taskEvents = @(Read-TaskEvents)
        if (-not $taskReady -and @($taskEvents | Where-Object { $_.event -eq 'Ready' }).Count -gt 0) {
            $taskReady = $true
            Write-Host 'READY: the real PIE world and Chinese overlay are active. An 8-second countdown precedes the test.'
        }
        $taskStep = $taskEvents | Where-Object { $_.event -eq 'Step' } | Select-Object -Last 1
        if ($null -ne $taskStep) {
            $taskSignature = [string]$taskStep.attempt + ':' + [string]$taskStep.state
            if ($taskSignature -ne $taskLastStep) {
                $taskLastStep = $taskSignature
                Write-Host ('Step: attempt ' + $taskStep.attempt + ' / ' + $taskStep.state)
            }
        }
        $taskResult = $taskEvents | Where-Object { $_.event -eq 'Result' } | Select-Object -Last 1
        if ($null -ne $taskResult) {
            $taskReport.Status = [string]$taskResult.status
            $taskReport.Ready = $taskReady
            $taskReport.CompletedAttempts = $taskResult.completed_attempts
            $taskReport.Result = Join-Path $taskOutput 'Result.json'
            $taskReport | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskOutput 'Launch.json') -Encoding UTF8
            if ($taskResult.status -ne 'PASS') { throw ('Automatic test ' + $taskResult.status + ': ' + $taskResult.error) }
            Write-Host 'PASS: two forests completed and reset cleanup passed. The final game picture remains open.'
            Write-Host 'Esc stops PIE; then close this test Editor without saving. The ordinary packaged launcher is unchanged.'
            Write-Host ('Result: ' + $taskReport.Result)
            break
        }
        $taskProcess.Refresh()
        if ($taskProcess.HasExited) {
            $taskReport.ActualProcessExitCode = $taskProcess.ExitCode
            throw ('Editor exited before a test result. ExitCode=' + $taskProcess.ExitCode)
        }
        if (-not $taskReady -and $taskClock.Elapsed.TotalSeconds -gt 125) { throw 'PIE/HUD startup timeout. Inspect the retained Editor and Session.log.' }
        if ($taskClock.Elapsed.TotalSeconds -gt 320) { throw 'Automatic test timeout. The Editor was retained for inspection.' }
        Start-Sleep -Milliseconds 250
    }
} catch {
    $taskReport.Status = 'LaunchOrTestError'
    $taskReport.Error = $_.Exception.Message
    $taskReport | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskOutput 'Launch-error.json') -Encoding UTF8
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host ('Log: ' + $taskLog)
    throw
} finally {
    [Environment]::SetEnvironmentVariable('DY_P03_VISIBLE_TEST_OUT', $taskPreviousOutput, 'Process')
}
