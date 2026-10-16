[CmdletBinding()]
param([ValidateSet('Package','EditorGame')][string]$Mode='Package',[ValidatePattern('^Run[1-9][0-9]*$')][string]$Run,[switch]$DryRun)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$taskRoot='D:\灯影山海'
$taskAlias='C:\UEProjects\DengYingShanHai'
$taskMap='/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab'
$taskPackageRoot=Join-Path $taskRoot 'Builds\FramePostDev-20261012-Run1\Windows'
$taskEvidence=Join-Path $taskRoot 'Saved\Audit-2026-10-12-FramePostPlacementDev'
$taskPlay=Join-Path $taskRoot 'Saved\Audit-2026-10-12-FramePostPlay'
$taskProcess=$null
try{
    $taskInvocationRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    if($taskInvocationRoot -ne $taskRoot -and $taskInvocationRoot -ne $taskAlias){throw '请从 D:\灯影山海 打开此入口，不运行其他位置副本。'}
    if($Mode -eq 'Package'){
        $taskIdentityPath=Join-Path $taskPackageRoot 'FRAME-POST-DEV-BUILD.json'
        $taskIdentity=Get-Content -LiteralPath $taskIdentityPath -Raw -Encoding UTF8|ConvertFrom-Json
        if(-not $taskIdentity.Succeeded -or $taskIdentity.Status -ne 'PASS-BUILD-COOK-STAGE-ARCHIVE-AND-CONTAINERS' -or $taskIdentity.Map -ne $taskMap -or $taskIdentity.ArchiveRoot -ne $taskPackageRoot -or $taskIdentity.Configuration -ne 'Development' -or $taskIdentity.Platform -ne 'Win64' -or $taskIdentity.Target -ne 'Game' -or $taskIdentity.Engine -ne '5.8.3' -or $taskIdentity.NativeRegressionSucceeded -ne 155 -or $taskIdentity.ManifestDependencyCount -ne 41 -or $taskIdentity.IoStoreChunksVerified -ne 2027 -or $taskIdentity.GlobalChunksVerified -ne 1 -or $taskIdentity.UATActualExit -ne 0){throw '固定单柱包身份与实际打包、依赖或容器补验不符。'}
        $taskArtifacts=Get-Content -LiteralPath (Join-Path $taskEvidence 'PackageContainer-Run2\ARTIFACTS.json') -Raw -Encoding UTF8|ConvertFrom-Json
        if($taskArtifacts.Count -ne 50){throw '固定包的完整归档清单缺失。'}
        foreach($taskRow in $taskArtifacts){
            if([IO.Path]::IsPathRooted($taskRow.Relative) -or ($taskRow.Relative -split '[\\/]') -contains '..' -or $taskRow.Relative -eq 'Docs\LICENSES.md'){throw '归档清单存在非法路径。'}
            $taskFile=Join-Path $taskPackageRoot $taskRow.Relative
            if(-not(Test-Path -LiteralPath $taskFile -PathType Leaf) -or (Get-FileHash -LiteralPath $taskFile).Hash -ne $taskRow.SHA256){throw ('固定包文件缺失或变动：'+$taskRow.Relative)}
        }
        $taskExecutable=Join-Path $taskPackageRoot 'DengYingShanHai\Binaries\Win64\DengYingShanHai.exe'
        if((Get-FileHash -LiteralPath $taskExecutable).Hash -ne $taskIdentity.NativeExeSHA256){throw '固定包运行文件与身份不一致。'}
        # A historical package is self-contained: later source/Docs edits do not
        # invalidate its sealed binaries. Never silently fall back to live Editor.
        $taskPrefix=@($taskMap)
    }else{
        $taskJunction=Get-Item -LiteralPath $taskAlias
        if($taskJunction.LinkType -ne 'Junction' -or [string](@($taskJunction.Target)[0]) -ne $taskRoot){throw '工程英文路径不是当前D盘工程。'}
        $taskFrozen=Get-Content -LiteralPath (Join-Path $taskEvidence 'AFTER-CREATE.json') -Raw -Encoding UTF8|ConvertFrom-Json
        foreach($taskRow in $taskFrozen){
            if($taskRow.Relative -match '^(Source|Content|Config)\\' -or $taskRow.Relative -eq 'DengYingShanHai.uproject'){
                if((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskRow.Relative)).Hash -ne $taskRow.SHA256){throw '实时工程已变更，不再是本轮EditorGame样本；请打开固定Package或重新验收。'}
            }
        }
        $taskExecutable='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
        foreach($taskFile in @($taskExecutable,(Join-Path $taskRoot 'Binaries\Win64\UnrealEditor-DengYingShanHai.dll'))){if(-not(Test-Path -LiteralPath $taskFile -PathType Leaf)){throw '显式EditorGame环境未准备完成。'}}
        $taskPrefix=@('"C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject"',$taskMap,'-game')
    }
    if(-not $Run){$taskNumber=1;while(Test-Path -LiteralPath (Join-Path $taskPlay ('Run'+$taskNumber))){$taskNumber++};$Run='Run'+$taskNumber}
    $taskOut=Join-Path $taskPlay $Run
    if(Test-Path -LiteralPath $taskOut){throw '此运行编号已有记录，已保留；请省略-Run或使用新编号。'}
    $taskArgs=$taskPrefix+@('-windowed','-ResX=1280','-ResY=800','-nosplash','-nowrite',('-abslog="'+(Join-Path $taskOut 'Session.log')+'"'),'-ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"')
    $taskReport=[ordered]@{Status='PREFLIGHT-ONLY';Mode=$Mode;Map=$taskMap;Executable=$taskExecutable;Arguments=$taskArgs;PackageRoot=$taskPackageRoot;Run=$Run;PID=$null;ActualProcessExitCode=$null;NativeHandleCaptured=$false;FirstFrameVerified=$false;FullGameplayVerified=$false;PythonExecuted=$false;OtherProcessesTerminated=$false;GlobalSettingsChanged=$false;Log=(Join-Path $taskOut 'Session.log')}
    if($DryRun){$taskReport|ConvertTo-Json -Depth 6;exit 0}
    if(@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai -ErrorAction SilentlyContinue).Count){throw '请先正常关闭已有UE或灯影山海窗口；未终止任何进程。'}
    New-Item -ItemType Directory -Path $taskOut -Force|Out-Null
    Write-Host '正在打开独立单柱Dev样本：开始复演 → 三幕 → 落杖成林 → 重新复演。'
    Write-Host '沿用 E 操纵/放开、A/D 调整、R 复位；新幕会解除上幕操纵。'
    Write-Host '只新增右侧一根免费木柱，无碰撞、交互或新增投影；不是正式完整幕框。'
    Write-Host ('本次记录：'+$taskOut)
    $taskProcess=Start-Process -FilePath $taskExecutable -ArgumentList $taskArgs -PassThru -WindowStyle Normal
    $taskHandle=$taskProcess.Handle
    if($taskHandle -eq [IntPtr]::Zero){throw '无法取得实际进程句柄；已创建窗口保留，请正常关闭。'}
    $taskReport.PID=$taskProcess.Id;$taskReport.NativeHandleCaptured=$true;$taskReport.Status='PROCESS-STARTED'
    $taskReport|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskOut 'Launch.json') -Encoding UTF8
    $taskProcess.WaitForExit();$taskExit=$taskProcess.ExitCode
    $taskReport.ActualProcessExitCode=$taskExit;$taskReport.Status='PROCESS-EXITED'
    $taskReport|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskOut 'Exit.json') -Encoding UTF8
    if($null -eq $taskExit){throw '退出码为空，不能视为正常退出。'}
    exit $taskExit
}catch{Write-Host ('无法启动或运行：'+$_.Exception.Message) -ForegroundColor Red;exit 1}
