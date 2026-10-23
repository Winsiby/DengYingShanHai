param()
$ErrorActionPreference='Stop'
$env:PSModulePath=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\Modules'
$artAudit='D:\灯影山海\Saved\Audit-2026-10-22-ArtPolish'
$archive='D:\灯影山海\Builds\FormalMain-Shipping-20261022-ArtPolishA5\Windows'
$exe=Join-Path $archive 'DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe'
if(@(Get-Process UnrealEditor,UnrealEditor-Cmd,DengYingShanHai,DengYingShanHai-Win64-Shipping -ErrorAction SilentlyContinue).Count){throw 'Existing UE/game process detected; do not interrupt.'}
$sessionDir=Join-Path $artAudit 'Runtime-Isolated'
New-Item -ItemType Directory -Path $sessionDir -Force|Out-Null
$originalSave=Join-Path $env:LOCALAPPDATA 'DengYingShanHai\Saved\DYProgress.txt'
if(Test-Path -LiteralPath $originalSave){Copy-Item -LiteralPath $originalSave -Destination (Join-Path $artAudit 'Backup\DYProgress.txt')}
$env:DY_CAMPAIGN_AUTOPLAY='1';$env:DY_SFX_PROBE='1';$env:DY_ART_PROBE='1';$env:DY_ENTRY_PROBE='1';$env:DY_DEBUG_VIEW='1'
Remove-Item Env:DY_CHAPTER -ErrorAction SilentlyContinue
Remove-Item Env:DY_SCRIPT -ErrorAction SilentlyContinue
$arguments=@('-windowed','-ResX=1600','-ResY=1000','-nosplash',('-UserDir='+$sessionDir+'\'),('-abslog='+$sessionDir+'\Session.log'))
$p=Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $archive -WindowStyle Normal -PassThru
$handle=$p.Handle
[ordered]@{PID=$p.Id;Executable=$exe;Arguments=$arguments;HandleCaptured=($handle -ne [IntPtr]::Zero);Verification='assisted target-value autoplay; debug review camera; not independent playtest'}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $sessionDir 'Launch.json') -Encoding UTF8
$p.WaitForExit()
[ordered]@{PID=$p.Id;ActualExit=$p.ExitCode;CompletedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $sessionDir 'Exit.json') -Encoding UTF8
$p.Dispose()
