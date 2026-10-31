[CmdletBinding()]
param([ValidateSet('Package','EditorGame')][string]$Mode='Package',[ValidatePattern('^Run[1-9][0-9]*$')][string]$Run,[switch]$DryRun)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$taskRoot='D:\灯影山海';$taskAlias='C:\UEProjects\DengYingShanHai'
$taskMap='/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab'
$taskPackageRoot=Join-Path $taskRoot 'Builds\FrameBeamTopUV-20261013-Run1\Windows'
$taskEvidence=Join-Path $taskRoot 'Saved\Audit-2026-10-13-FrameBeamTopUVDev'
$taskPlay=Join-Path $taskRoot 'Saved\Audit-2026-10-13-FrameBeamTopUVPlay'
try{
    $taskInvocationRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    if($taskInvocationRoot -ne $taskRoot -and $taskInvocationRoot -ne $taskAlias){throw '请从 D:\灯影山海 打开正式入口，不运行其它位置副本。'}
    if($Mode -eq 'Package'){
        $identity=Get-Content -LiteralPath (Join-Path $taskPackageRoot 'FRAME-BEAM-TOPUV-DEV-BUILD.json') -Raw -Encoding UTF8|ConvertFrom-Json
        if($identity.Succeeded -isnot [bool] -or $identity.Succeeded -ne $true -or $identity.Status -ne 'PASS-BUILD-COOK-STAGE-ARCHIVE-AND-CONTAINERS' -or $identity.Map -ne $taskMap -or $identity.ArchiveRoot -ne $taskPackageRoot -or $identity.Configuration -ne 'Development' -or $identity.Platform -ne 'Win64' -or $identity.Target -ne 'Game' -or $identity.Engine -ne '5.8.3' -or $identity.NativeRegressionSucceeded -ne 158 -or $identity.ManifestDependencyCount -ne 42 -or $identity.IoStoreChunksVerified -le 0 -or $identity.GlobalChunksVerified -ne 1 -or $null -eq $identity.UATActualExit -or $identity.UATActualExit -ne 0){throw '固定横梁包身份与本轮实际编译、依赖或容器验证不符。'}
        $packageBefore=Get-Content -LiteralPath (Join-Path $taskEvidence 'BEFORE.json') -Raw -Encoding UTF8|ConvertFrom-Json
        $packageSource=@($identity.SourceProducts)
        $expectedPackageSource=@($packageBefore.Files.Relative)+@('Scripts\Create-FrameBeamTopUVDev.py','Content\DengYingShanHai\Dev\FrameBeamTopUV\Maps\LV_FrameBeamTopUVLab.umap')
        if(@($packageBefore.Files).Count -ne 348 -or @($packageBefore.Files.Relative|Sort-Object -Unique).Count -ne 348 -or $packageSource.Count -ne 350 -or @($packageSource.Relative|Sort-Object -Unique).Count -ne 350 -or @(Compare-Object @($expectedPackageSource|Sort-Object) @($packageSource.Relative|Sort-Object) -CaseSensitive).Count){throw '固定包350产品记录与348原始基线不一致。'}
        $packageMap=@($packageSource|Where-Object {$_.Relative -ceq 'Content\DengYingShanHai\Dev\FrameBeamTopUV\Maps\LV_FrameBeamTopUVLab.umap'})
        if($packageMap.Count -ne 1 -or $packageMap[0].SHA256 -cne $identity.SourceMapSHA256){throw '固定包地图来源与包身份不一致。'}
        $container=Get-Content -LiteralPath (Join-Path $taskEvidence 'PackageContainer-Run1\RESULT.json') -Raw -Encoding UTF8|ConvertFrom-Json
        foreach($flag in @('SourceProtectionVerified','ActualIoStorePayloadHashVerified')){if($container.$flag -isnot [bool] -or $container.$flag -ne $true){throw '最终容器验收未完成，拒绝提前生成的包身份。'}}
        if($container.Status -ne $identity.Status -or $container.NativeOperations -ne 3 -or $null -eq $container.ActualUATExit -or $container.ActualUATExit -ne 0 -or $container.ManifestDependencyCount -ne 42 -or $container.IoStoreChunksVerified -ne $identity.IoStoreChunksVerified -or $container.GlobalChunksVerified -ne $identity.GlobalChunksVerified -or $container.MainBytesRead -ne $identity.MainBytesRead -or $container.GlobalBytesRead -ne $identity.GlobalBytesRead){throw '最终容器结果与固定包身份不一致。'}
        $artifacts=Get-Content -LiteralPath (Join-Path $taskEvidence 'PackageContainer-Run1\ARTIFACTS.json') -Raw -Encoding UTF8|ConvertFrom-Json
        if($artifacts.Count -lt 9 -or @($artifacts.Relative|Select-Object -Unique).Count -ne $artifacts.Count -or @($artifacts|Where-Object {$_.Relative -ceq 'FRAME-BEAM-TOPUV-DEV-BUILD.json'}).Count -ne 1){throw '固定包完整清单缺失、重复或未绑定身份。'}
        foreach($row in $artifacts){
            if([string]::IsNullOrWhiteSpace($row.Relative) -or [IO.Path]::IsPathRooted($row.Relative) -or ($row.Relative -split '[\\/]') -contains '..' -or $row.Relative.Replace('/','\') -ieq 'Docs\LICENSES.md'){throw '非法或受限归档路径。'}
            $file=Join-Path $taskPackageRoot $row.Relative
            if(-not(Test-Path -LiteralPath $file -PathType Leaf) -or (Get-Item -LiteralPath $file).Length -ne $row.Bytes -or (Get-FileHash -LiteralPath $file).Hash -ne $row.SHA256){throw ('固定包缺失或变化：'+$row.Relative)}
        }
        $actualNames=@(Get-ChildItem -LiteralPath $taskPackageRoot -File -Recurse|ForEach-Object {$_.FullName.Substring($taskPackageRoot.Length+1)}|Sort-Object)
        if(@(Compare-Object @($artifacts.Relative|Sort-Object) $actualNames -CaseSensitive).Count -or $container.ArtifactFileCount -ne $artifacts.Count -or $container.ArtifactBytes -ne ($artifacts|Measure-Object Bytes -Sum).Sum){throw '固定包实际文件集合与完整清单不一致。'}
        foreach($required in @('FRAME-BEAM-TOPUV-DEV-BUILD.json','DengYingShanHai\Binaries\Win64\DengYingShanHai.exe','DengYingShanHai\Content\Paks\DengYingShanHai-Windows.pak','DengYingShanHai\Content\Paks\DengYingShanHai-Windows.utoc','DengYingShanHai\Content\Paks\DengYingShanHai-Windows.ucas','DengYingShanHai\Content\Paks\global.utoc','DengYingShanHai\Content\Paks\global.ucas')){if(@($artifacts|Where-Object {$_.Relative -ceq $required}).Count -ne 1){throw ('固定包必需文件缺失或重复：'+$required)}}
        $taskExecutable=Join-Path $taskPackageRoot 'DengYingShanHai\Binaries\Win64\DengYingShanHai.exe'
        if((Get-FileHash -LiteralPath $taskExecutable).Hash -ne $identity.NativeExeSHA256){throw '运行文件与包身份不一致。'}
        # The sealed package is self-contained; later source/docs edits cannot
        # silently redirect it to a live editor or another "latest" package.
        $taskPrefix=@($taskMap)
    }else{
        $junction=Get-Item -LiteralPath $taskAlias
        if($junction.LinkType -ne 'Junction' -or [string](@($junction.Target)[0]) -ne $taskRoot){throw '工程英文入口不是当前D盘工程。'}
        $frozen=Get-Content -LiteralPath (Join-Path $taskEvidence 'AFTER-CREATE.json') -Raw -Encoding UTF8|ConvertFrom-Json
        if($frozen.Count -ne 350 -or @($frozen.Relative|Sort-Object -Unique).Count -ne 350){throw 'EditorGame 的完整工程基线无效。'}
        foreach($row in $frozen){if([string]::IsNullOrWhiteSpace($row.Relative) -or [IO.Path]::IsPathRooted($row.Relative) -or ($row.Relative -split '[\\/]') -contains '..' -or $row.Relative.Replace('/','\') -ieq 'Docs\LICENSES.md'){throw '工程基线路径非法或受限。'}}
        $before=Get-Content -LiteralPath (Join-Path $taskEvidence 'BEFORE.json') -Raw -Encoding UTF8|ConvertFrom-Json
        if(@($before.Files).Count -ne 348 -or @($before.Files.Relative|Sort-Object -Unique).Count -ne 348){throw 'EditorGame 的348原始基线无效。'}
        $expectedBaseline=@($before.Files.Relative)+@('Scripts\Create-FrameBeamTopUVDev.py','Content\DengYingShanHai\Dev\FrameBeamTopUV\Maps\LV_FrameBeamTopUVLab.umap')
        if($expectedBaseline.Count -ne 350 -or @(Compare-Object @($expectedBaseline|Sort-Object) @($frozen.Relative|Sort-Object) -CaseSensitive).Count){throw 'EditorGame 基线集合与独立原始记录不一致。'}
        $sourceNames=@(foreach($dir in @('Source','Content','Config')){Get-ChildItem -LiteralPath (Join-Path $taskRoot $dir) -File -Recurse|ForEach-Object {$_.FullName.Substring($taskRoot.Length+1)}})+@('DengYingShanHai.uproject')
        $pinnedNames=@($frozen|Where-Object {$_.Relative -match '^(Source|Content|Config)\\' -or $_.Relative -eq 'DengYingShanHai.uproject'}|ForEach-Object {$_.Relative})
        if(@(Compare-Object @($sourceNames|Sort-Object) @($pinnedNames|Sort-Object) -CaseSensitive).Count){throw 'EditorGame 的源码、资产与配置文件集合已改变。'}
        foreach($row in $frozen){if($row.Relative -match '^(Source|Content|Config)\\' -or $row.Relative -eq 'DengYingShanHai.uproject'){
            if([IO.Path]::IsPathRooted($row.Relative) -or ($row.Relative -split '[\\/]') -contains '..'){throw '工程清单路径非法。'}
            if((Get-FileHash -LiteralPath (Join-Path $taskRoot $row.Relative)).Hash -ne $row.SHA256){throw '实时工程已改变；请使用固定Package或重新验证EditorGame。'}
        }}
        $taskExecutable='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
        foreach($file in @($taskExecutable,(Join-Path $taskRoot 'Binaries\Win64\UnrealEditor-DengYingShanHai.dll'))){if(-not(Test-Path -LiteralPath $file -PathType Leaf)){throw 'EditorGame显式环境缺失。'}}
        $taskPrefix=@('"C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject"',$taskMap,'-game')
    }
    if(-not $Run){$number=1;while(Test-Path -LiteralPath (Join-Path $taskPlay ('Run'+$number))){$number++};$Run='Run'+$number}
    $taskOut=Join-Path $taskPlay $Run
    if(Test-Path -LiteralPath $taskOut){throw '运行编号已有记录，未覆盖；请省略-Run或指定新编号。'}
    $taskArgs=$taskPrefix+@('-windowed','-ResX=1280','-ResY=800','-nosplash','-nowrite',('-abslog="'+(Join-Path $taskOut 'Session.log')+'"'),'-ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"')
    $report=[ordered]@{Status='PREFLIGHT-ONLY';Mode=$Mode;Map=$taskMap;Executable=$taskExecutable;Arguments=$taskArgs;PackageRoot=$taskPackageRoot;Run=$Run;PID=$null;ActualProcessExitCode=$null;NativeHandleCaptured=$false;FirstFrameVerified=$false;FullGameplayVerified=$false;PythonExecuted=$false;OtherProcessesTerminated=$false;GlobalSettingsChanged=$false;Log=(Join-Path $taskOut 'Session.log')}
    if($DryRun){$report|ConvertTo-Json -Depth 6;exit 0}
    if(@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai -ErrorAction SilentlyContinue).Count){throw '请先正常关闭已有UE或游戏窗口，未终止任何进程。'}
    New-Item -ItemType Directory -Path $taskOut|Out-Null
    Write-Host '正在打开独立横梁顶面UV候选Dev：开始复演 → 三幕 → 落杖成林 → 重新复演。'
    Write-Host '沿用 E、A/D、R 与跨幕解除；仅替换B摆放的横梁顶面UV候选，不改变位置、材质、玩法；不是正式美术采纳。'
    Write-Host ('本次记录：'+$taskOut)
    $process=Start-Process -FilePath $taskExecutable -ArgumentList $taskArgs -PassThru -WindowStyle Normal
    $handle=$process.Handle;if($handle -eq [IntPtr]::Zero){throw '进程句柄不可用，窗口保留，请正常关闭。'}
    $report.PID=$process.Id;$report.NativeHandleCaptured=$true;$report.Status='PROCESS-STARTED'
    $report|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskOut 'Launch.json') -Encoding UTF8
    $process.WaitForExit();$actual=$process.ExitCode
    $report.ActualProcessExitCode=$actual;$report.Status='PROCESS-EXITED'
    $report|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $taskOut 'Exit.json') -Encoding UTF8
    if($null -eq $actual){throw '退出码为空，不能视为正常退出。'}
    exit $actual
}catch{Write-Host ('无法启动或运行：'+$_.Exception.Message) -ForegroundColor Red;exit 1}
