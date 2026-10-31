param([switch]$DryRun,[switch]$PreviewTest)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$taskRoot='D:\灯影山海'
$taskAudit=Join-Path $taskRoot 'Saved\Audit-2026-10-12-FrameBeamAsset'
$taskProject='C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject'
$taskEditor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskScript=Join-Path $PSScriptRoot 'Open-FrameBeamAsset.py'
foreach($taskFile in @($taskProject,$taskEditor,$taskScript,(Join-Path $taskAudit 'OWN-ASSET.json'),(Join-Path $taskAudit 'DEPENDENCIES.json'))){if(-not(Test-Path -LiteralPath $taskFile -PathType Leaf)){throw ('查看所需文件缺失：'+$taskFile)}}
$taskOwn=Get-Content -LiteralPath (Join-Path $taskAudit 'OWN-ASSET.json') -Raw -Encoding UTF8|ConvertFrom-Json
$taskDeps=Get-Content -LiteralPath (Join-Path $taskAudit 'DEPENDENCIES.json') -Raw -Encoding UTF8|ConvertFrom-Json
if($taskOwn.Status -ne 'PASS-ONLY-ONE-NEW-MESH' -or $taskOwn.File.Relative -ne 'Content\DengYingShanHai\Dev\FrameBeamAsset\Meshes\SM_DY_FrameBeam_Source.uasset' -or $taskDeps.Count -ne 5){throw '只能查看本轮已冻结的一份横梁和五份旧依赖'}
$taskDependencyExpected=@('Materials\MI_DY_FramePost_Wood','Materials\M_DY_FramePost_Master','Textures\T_DY_FramePost_BaseColor','Textures\T_DY_FramePost_NormalDX','Textures\T_DY_FramePost_ARM')|ForEach-Object {'Content\DengYingShanHai\Dev\FramePostAsset\'+$_+'.uasset'}
if(@($taskDeps.Relative|Select-Object -Unique).Count -ne 5 -or @(Compare-Object -CaseSensitive ($taskDependencyExpected|Sort-Object) ($taskDeps.Relative|Sort-Object)).Count){throw '五份依赖必须为唯一且精确的既有木材实例、父材质和三张纹理，不接受重复/替代'}
$taskRows=@($taskOwn.File)+@($taskDeps)
if(-not $PreviewTest){
    if([IO.Path]::GetFullPath($PSCommandPath) -ne (Join-Path $taskRoot 'Scripts\Start-FrameBeamAssetReview.ps1')){throw '请运行 D:\灯影山海 的正式查看入口'}
    $taskFinal=Get-Content -LiteralPath (Join-Path $taskAudit 'FINAL.json') -Raw -Encoding UTF8|ConvertFrom-Json
    $taskManifest=Get-Content -LiteralPath (Join-Path $taskAudit 'AFTER.json') -Raw -Encoding UTF8|ConvertFrom-Json
    if($taskFinal.Status -ne 'PASS-DEV-FRAME-BEAM-ASSET-ADMISSION-ONLY'){throw '横梁资产准入尚未完成'}
    foreach($taskRel in @('Scripts\Open-FrameBeamAsset.py','Scripts\Start-FrameBeamAssetReview.ps1','Start-FrameBeamAssetReview.cmd')){
        $taskFound=@($taskManifest|Where-Object {$_.Relative -eq $taskRel})
        if($taskFound.Count -ne 1 -or (Get-FileHash -LiteralPath (Join-Path $taskRoot $taskRel)).Hash -ne $taskFound[0].SHA256){throw '查看入口文件已变更，请重新核查'}
    }
    foreach($taskRow in $taskRows){$taskFrozen=@($taskManifest|Where-Object {$_.Relative -eq $taskRow.Relative});if($taskFrozen.Count -ne 1 -or $taskFrozen[0].SHA256 -ne $taskRow.SHA256){throw '查看资产未与最终清单一致绑定'}}
}
foreach($taskRow in $taskRows){
    if([IO.Path]::IsPathRooted($taskRow.Relative) -or ($taskRow.Relative -split '[\\/]') -contains '..' -or $taskRow.Relative -eq 'Docs\LICENSES.md'){throw '拒绝不合法或受限路径'}
    if((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskRow.Relative)).Hash -ne $taskRow.SHA256){throw '已验证资产或材质依赖已改变'}
}
if($DryRun){[pscustomobject]@{Status='PREFLIGHT-ONLY';Mode='Native mesh viewer, NOT GAME';Assets=1;FrozenDependencies=5;RealRHI=$true;ScaleChanged=$false;WritesOnDryRun=$false;NoWriteConfigChild=$true;PreviewTest=[bool]$PreviewTest}|ConvertTo-Json;exit 0}
if(@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai -ErrorAction SilentlyContinue).Count){throw '请先正常关闭已有UE或游戏窗口；不会强制结束进程'}
$taskOut=Join-Path $taskAudit ('review-'+(Get-Date -Format 'yyyyMMdd-HHmmss-ffff'))
if(Test-Path -LiteralPath $taskOut){throw '保留已有查看记录'}
New-Item -ItemType Directory -Path $taskOut|Out-Null
$env:DY_BEAM_REVIEW_OUT=Join-Path $taskOut 'Result.json'
$taskArgs=@(('"'+$taskProject+'"'),('"-ExecutePythonScript='+$taskScript+'"'),'-nowrite','-nosplash',('"-abslog='+(Join-Path $taskOut 'Session.log')+'"'))
[pscustomobject]@{Arguments=$taskArgs;ScriptSHA256=(Get-FileHash -LiteralPath $taskScript).Hash;Game=$false;NullRHI=$false;PreviewTest=[bool]$PreviewTest}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $taskOut 'LAUNCH.json') -Encoding UTF8
$taskProcess=Start-Process -FilePath $taskEditor -ArgumentList $taskArgs -PassThru -WindowStyle Normal -RedirectStandardOutput (Join-Path $taskOut 'Stdout.log') -RedirectStandardError (Join-Path $taskOut 'Stderr.log')
$taskHandle=$taskProcess.Handle
if($taskHandle -eq [IntPtr]::Zero){throw '实际编辑器句柄不可用，保留现有进程/日志'}
Write-Output ('已打开横梁原生查看器，不是游戏。PID='+$taskProcess.Id+'；记录：'+$taskOut)
$taskProcess.WaitForExit();$taskExit=$taskProcess.ExitCode
[pscustomobject]@{PID=$taskProcess.Id;ExitCode=$taskExit;HandleCapturedBeforeWait=$true;CompletedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskOut 'EXIT.json') -Encoding UTF8
if($null -eq $taskExit -or $taskExit -ne 0){throw '编辑器未提供实际正常退出码'}
$taskResult=Get-Content -LiteralPath $env:DY_BEAM_REVIEW_OUT -Raw -Encoding UTF8|ConvertFrom-Json
if(-not $taskResult.success){throw '原生横梁查看器没有成功打开，请保留日志排查'}
