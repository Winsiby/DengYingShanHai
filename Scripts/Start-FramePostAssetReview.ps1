param([switch]$DryRun,[switch]$PreviewTest)
$ErrorActionPreference='Stop'
$taskRoot='D:\灯影山海'
$taskProject='C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject'
$taskEditor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskAudit=Join-Path $taskRoot 'Saved\Audit-2026-10-12-FramePostAsset'
$taskScript=Join-Path $PSScriptRoot 'Open-FramePostAsset.py'
foreach($taskRequired in @($taskProject,$taskEditor,$taskScript,(Join-Path $taskAudit 'OWN-ASSETS.json'))){
    if(-not (Test-Path -LiteralPath $taskRequired -PathType Leaf)){throw ('Missing exact review dependency: '+$taskRequired)}
}
if(-not $PreviewTest){
    if([IO.Path]::GetFullPath($PSCommandPath) -ne (Join-Path $taskRoot 'Scripts\Start-FramePostAssetReview.ps1') -or [IO.Path]::GetFullPath($taskScript) -ne (Join-Path $taskRoot 'Scripts\Open-FramePostAsset.py')){throw 'Normal review must use exact published helpers'}
    $taskFinal=Get-Content -LiteralPath (Join-Path $taskAudit 'FINAL.json') -Raw|ConvertFrom-Json
    if($taskFinal.Status -ne 'PASS-DEV-ASSET-ADMISSION-ONLY'){throw 'Final asset admission is not ready'}
    $taskManifest=Get-Content -LiteralPath (Join-Path $taskAudit 'AFTER.json') -Raw|ConvertFrom-Json
    foreach($taskRelative in @('Scripts\Open-FramePostAsset.py','Scripts\Start-FramePostAssetReview.ps1','Start-FramePostAssetReview.cmd')){
        $taskRecord=@($taskManifest|Where-Object {$_.Relative -eq $taskRelative})
        if($taskRecord.Count -ne 1 -or (Get-FileHash -LiteralPath (Join-Path $taskRoot $taskRelative)).Hash -ne $taskRecord[0].SHA256){throw ('Review helper changed: '+$taskRelative)}
    }
}
$taskAssets=Get-Content -LiteralPath (Join-Path $taskAudit 'OWN-ASSETS.json') -Raw|ConvertFrom-Json
$taskAssetNames=@('Meshes\SM_DY_FramePost_Source','Materials\M_DY_FramePost_Master','Materials\MI_DY_FramePost_Wood','Materials\MI_DY_FramePost_Base','Textures\T_DY_FramePost_BaseColor','Textures\T_DY_FramePost_NormalDX','Textures\T_DY_FramePost_ARM')
$taskAssetExpected=@($taskAssetNames|ForEach-Object{'Content\DengYingShanHai\Dev\FramePostAsset\'+$_+'.uasset'})
if($taskAssets.Count -ne 7 -or @($taskAssets.Relative|Select-Object -Unique).Count -ne 7 -or @(Compare-Object ($taskAssetExpected|Sort-Object) ($taskAssets.Relative|Sort-Object)).Count){throw 'Require exact seven unique admitted Dev asset names'}
foreach($taskRow in $taskAssets){
    if(-not $PreviewTest){
        $taskFinalAsset=@($taskManifest|Where-Object {$_.Relative -eq $taskRow.Relative})
        if($taskFinalAsset.Count -ne 1 -or $taskFinalAsset[0].SHA256 -ne $taskRow.SHA256){throw 'Assets must be cross-bound to final frozen product manifest'}
    }
    if((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskRow.Relative)).Hash -ne $taskRow.SHA256){throw ('Dev asset changed: '+$taskRow.Relative)}
}
if($DryRun){
    [pscustomobject]@{Mode='Native mesh viewer, NOT GAME';Editor=$taskEditor;Project=$taskProject;Assets=$taskAssets.Count;RealRHI=$true;ScaleChanged=$false;WritesOnDryRun=$false;NoWriteConfigChild=$true;PreviewTest=[bool]$PreviewTest}|ConvertTo-Json
    exit 0
}
if(@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai -ErrorAction SilentlyContinue).Count){throw 'Please close your current UE/game window normally; no process will be killed'}
$taskStamp=Get-Date -Format 'yyyyMMdd-HHmmss-ffff'
$taskOut=Join-Path $taskAudit ('review-'+$taskStamp)
if(Test-Path -LiteralPath $taskOut){throw 'Preserve prior review session'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
$env:DY_POST_REVIEW_OUT=Join-Path $taskOut 'Result.json'
$taskArgs=@(('"'+$taskProject+'"'),('"-ExecutePythonScript='+$taskScript+'"'),'-nowrite','-nosplash',('"-abslog='+(Join-Path $taskOut 'Session.log')+'"'))
[pscustomobject]@{Arguments=$taskArgs;ScriptSHA256=(Get-FileHash -LiteralPath $taskScript).Hash;Game=$false;NullRHI=$false;PreviewTest=[bool]$PreviewTest}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $taskOut 'LAUNCH.json') -Encoding utf8
$taskProcess=Start-Process -FilePath $taskEditor -ArgumentList $taskArgs -PassThru -WindowStyle Normal -RedirectStandardOutput (Join-Path $taskOut 'Stdout.log') -RedirectStandardError (Join-Path $taskOut 'Stderr.log')
$taskNativeHandle=$taskProcess.Handle
if($taskNativeHandle -eq [IntPtr]::Zero){throw 'Native process handle unavailable; preserve launch logs'}
Write-Output ('Native mesh review opened. PID='+$taskProcess.Id+'; session='+$taskOut)
$taskProcess.WaitForExit()
$taskNativeExitCode=$taskProcess.ExitCode
[pscustomobject]@{PID=$taskProcess.Id;ExitCode=$taskNativeExitCode;HandleAcquiredBeforeWait=$true;CompletedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'EXIT.json') -Encoding utf8
if($null -eq $taskNativeExitCode){throw 'Editor exit code unavailable; do not infer success from null'}
if($taskNativeExitCode -ne 0){throw 'Editor review exited abnormally; preserve logs'}
$taskResult=Get-Content -LiteralPath $env:DY_POST_REVIEW_OUT -Raw|ConvertFrom-Json
if(-not $taskResult.success){throw 'Native mesh viewer did not open; inspect actual Result.json'}
