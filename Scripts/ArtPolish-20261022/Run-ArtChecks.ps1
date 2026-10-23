$ErrorActionPreference='Stop'
$artAudit='D:\灯影山海\Saved\Audit-2026-10-22-ArtPolish'
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if(@(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count){throw 'Existing editor detected.'}
Remove-Item Env:DY_SCRIPT -ErrorAction SilentlyContinue
Remove-Item Env:DY_VIEW -ErrorAction SilentlyContinue
$testLog=Join-Path $artAudit 'Automation-ArtPolish.log'
$testArgs=@('C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject','-ExecCmds="Automation RunTests DengYingShanHai"','-TestExit="Automation Test Queue Empty"','-unattended','-nosplash','-nullrhi','-nopause',('-AbsLog='+$testLog))
$p=Start-Process -FilePath $editor -ArgumentList $testArgs -WorkingDirectory 'D:\灯影山海' -WindowStyle Hidden -PassThru
$p.WaitForExit()
$exit=$p.ExitCode
$logText=Get-Content -LiteralPath $testLog -Raw
$success=([regex]::Matches($logText,'Result=\{Success\}')).Count
$failed=([regex]::Matches($logText,'Result=\{Fail')).Count
$result=[ordered]@{ActualExit=$exit;Success=$success;Failed=$failed;Log=$testLog}
$result|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $artAudit 'AUTOMATION.json') -Encoding UTF8
if($exit -ne 0 -or $failed -ne 0 -or $success -lt 176){throw 'Automation failed/incomplete.'}
Write-Output ('PASS automation '+$success+'/'+$failed)
