# Independent Editor-only player candidate. -Verify is a separate diagnostic.
param([switch]$Verify,[switch]$DryRun,[ValidatePattern('^Run[1-9][0-9]*$')][string]$Run)
$ErrorActionPreference='Stop'
$projectRoot='C:\UEProjects\DengYingShanHai'
$junction=Get-Item -LiteralPath $projectRoot
$expected='D:\'+(-join [char[]]@(0x706F,0x5F71,0x5C71,0x6D77))
if($junction.LinkType -ne 'Junction' -or [string](@($junction.Target)[0]) -ne $expected){throw 'Wrong migrated project junction'}
$invocationRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if($invocationRoot -ne $expected -and $invocationRoot -ne $projectRoot){throw 'Use D project or English alias'}
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$project=Join-Path $projectRoot 'DengYingShanHai.uproject'
$scriptName=if($Verify){'Verify-P03DevCandidate.py'}else{'Play-P03DevCandidate.py'}
$script=Join-Path $projectRoot ('Scripts\'+$scriptName)
$audit=Join-Path $projectRoot 'Saved\Audit-2026-10-05-P03PlayableCandidate'
foreach($path in @($editor,$project,$script,(Join-Path $projectRoot 'Scripts\Preview-P03StaffDrop.py'),(Join-Path $projectRoot 'Content\DengYingShanHai\Dev\M3\Forest\BP_DYForestPresentation_Dev.uasset'),(Join-Path $projectRoot 'Content\DengYingShanHai\Dev\M3\Maps\LV_M3GeometryProbe.umap'))){if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "Missing: $path"}}
if(-not $Run){$n=1;while((Test-Path -LiteralPath (Join-Path $audit "Run$n")) -or (Test-Path -LiteralPath (Join-Path $audit "Session-Run$n.log"))){$n++};$Run="Run$n"}
$output=Join-Path $audit $Run
$log=Join-Path $audit ("Session-$Run.log")
if((Test-Path -LiteralPath $output) -or (Test-Path -LiteralPath $log)){throw 'Refuse overwrite existing evidence'}
# Parenthesize every concatenation: PowerShell otherwise flattens fragments.
$arguments=@(('"'+$project+'"'),('-ExecutePythonScript="'+$script+'"'),'-nosplash','-log',('-abslog="'+$log+'"'))
if($arguments.Count -ne 5){throw 'Incorrect argument count'}
$windowStyle=if($Verify){'Hidden'}else{'Normal'}
$report=[ordered]@{Run=$Run;Output=$output;Log=$log;Mode=$(if($Verify){'Verify'}else{'Play'});WindowStyle=$windowStyle;ArgumentCount=$arguments.Count;EditorOnly=$true;FormalTuning=$false}
if($DryRun){$report.Command='"'+$editor+'" '+($arguments -join ' ');$report|ConvertTo-Json;return}
function Read-SessionEvent([string]$Name){
    $events=Join-Path $output 'Events.jsonl'
    if(-not (Test-Path -LiteralPath $events -PathType Leaf)){return $null}
    # UE can still be writing the last UTF-8 line. Retry incomplete lines next poll.
    try{$lines=@(Get-Content -LiteralPath $events -Encoding UTF8 -ErrorAction Stop)}catch{return $null}
    foreach($line in $lines){
        try{$item=$line | ConvertFrom-Json -ErrorAction Stop}catch{continue}
        if($item.event -eq $Name){return $item}
    }
    return $null
}
function Show-SessionPaths {
    Write-Host ('Run: '+$Run)
    Write-Host ('Session log: '+$log)
    Write-Host ('Evidence: '+$output)
}
$ueProcesses=@(Get-CimInstance Win32_Process -Filter "name='UnrealEditor.exe' OR name='UnrealEditor-Cmd.exe'")
# Windows may retain a terminated object's PID while BOTH counts are zero.
# Unknown counts remain blocking. Never kill processes or bypass a live session.
$liveUE=@($ueProcesses | Where-Object {$null -eq $_.ThreadCount -or $null -eq $_.HandleCount -or $_.ThreadCount -gt 0 -or [long]$_.HandleCount -gt 0})
if($liveUE.Count){throw 'Close existing live UE sessions first; nothing was terminated'}
$report.IgnoredZeroThreadZeroHandlePids=@($ueProcesses | ForEach-Object ProcessId)
New-Item -ItemType Directory -Path $output | Out-Null
$previous=[Environment]::GetEnvironmentVariable('DY_P03_PLAYABLE_OUT','Process')
try{
    [Environment]::SetEnvironmentVariable('DY_P03_PLAYABLE_OUT',$output,'Process')
    Write-Host 'LOADING: waiting for the actual PIE session, not just the Editor process.'
    Write-Host 'Editor-only: do not save this temporary Dev session.'
    Show-SessionPaths
    $process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle $windowStyle -PassThru -RedirectStandardOutput (Join-Path $output 'Stdout.log') -RedirectStandardError (Join-Path $output 'Stderr.log')
    $report.ProcessId=$process.Id
    $clock=[Diagnostics.Stopwatch]::StartNew()
    $ready=$false
    while($true){
        if(-not $ready){
            $readyEvent=Read-SessionEvent 'Ready'
            if($readyEvent){
                $ready=$true
                $report.Status='Ready'
                $report.StartupSeconds=[math]::Round($clock.Elapsed.TotalSeconds,2)
                Write-Host 'READY: PIE is running. Native E/A/D and contextual R are unchanged.'
                if(-not $Verify){
                    Write-Host 'Use the game viewport in the visible Editor. Click it once if Windows changed foreground focus.'
                    Write-Host 'Shift+F1 releases the mouse; Esc stops PIE. Stopping PIE no longer closes the Editor.'
                    Write-Host 'There is NO player time limit. This console remains as a session status monitor.'
                }
            }
        }
        # Read Finished before process exit: Verify writes it immediately before QUIT.
        $finished=Read-SessionEvent 'Finished'
        if($finished){
            if($finished.error){throw ('UE script failed: '+$finished.error)}
            # A very short session can publish both events between our reads.
            if(-not $ready){$ready=$null -ne (Read-SessionEvent 'Ready')}
            if(-not $ready){throw 'Session ended before READY; no playable startup was confirmed'}
            $report.Status='Finished'
            $report.EditorRetained=(-not $Verify)
            Write-Host $(if($Verify){'VERIFY FINISHED: inspect VerificationSummary in Events.jsonl for test results.'}else{'PIE stopped; temporary session cleaned up. Editor stays open. Close it WITHOUT saving before relaunching.'})
            $report|ConvertTo-Json
            break
        }
        $process.Refresh()
        if($process.HasExited){
            # Finished may have been flushed between our event read and Refresh.
            if(Read-SessionEvent 'Finished'){continue}
            throw ('Editor exited before a complete session result. PID='+$process.Id+' ExitCode='+$process.ExitCode+' Ready='+$ready)
        }
        if(-not $ready -and $clock.Elapsed.TotalSeconds -gt 120){throw 'Startup timed out before READY. Editor was NOT terminated; inspect it and the session log.'}
        if($Verify -and $clock.Elapsed.TotalSeconds -gt 210){throw 'Verify timed out. Editor was NOT terminated; inspect the session log.'}
        Start-Sleep -Milliseconds 250
    }
}catch{
    Write-Host ('ERROR: '+$_.Exception.Message) -ForegroundColor Red
    Show-SessionPaths
    Write-Host ('Standard error: '+(Join-Path $output 'Stderr.log'))
    throw
}finally{[Environment]::SetEnvironmentVariable('DY_P03_PLAYABLE_OUT',$previous,'Process')}
