param([ValidateRange(1,99)][int]$Run=1,[switch]$RunComparison)
$ErrorActionPreference='Stop'
$blender='C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ArtProduction-20261014\Tooling\Portable-Run1\blender-4.5.14-windows-x64\blender.exe'
$out=Join-Path $PSScriptRoot ($(if($RunComparison){'Sam-RunPreview-Run'}else{'Sam-Preview-Run'})+$Run)
if(Test-Path -LiteralPath $out){throw 'Preserve prior preview evidence'}
if(@(Get-Process -Name blender -ErrorAction SilentlyContinue).Count){throw 'Preserve existing Blender session'}
New-Item -ItemType Directory -Path $out | Out-Null
$script=Join-Path $PSScriptRoot 'preview_sam.py'
$scriptHash=(Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash
[IO.File]::Copy($script,(Join-Path $out 'preview_sam.py'),$false)
[IO.File]::Copy($PSCommandPath,(Join-Path $out 'Run-SamPreview.ps1'),$false)
$arguments=@('--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--python',$script,'--','--source',$(if($RunComparison){$PSScriptRoot}else{Join-Path $PSScriptRoot 'Sam-Original'}),'--out',$out)
if($RunComparison){$arguments+='--run-comparison'}
& $blender @arguments 2>&1 | Tee-Object -FilePath (Join-Path $out 'Blender.log')
$nativeExit=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $out 'NATIVE-EXIT.json'),([ordered]@{ActualNativeExit=$nativeExit;ScriptSHA256=$scriptHash;CompletedAt=(Get-Date).ToString('o')}|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
if($nativeExit -ne 0){throw 'Actual source preview failed; preserve evidence'}
if((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -cne $scriptHash){throw 'Preview source changed during native run'}
$report=Get-Content -LiteralPath (Join-Path $out 'SOURCE_CHECK.json') -Raw | ConvertFrom-Json
if(@($report.source_files).Count -ne 2 -or @($report.source_files.blender.captures).Count -ne 7){throw 'Seven actual source renders required'}
$report | Select-Object schema,skeletons_identical,geometry_identical,actual_native_UE_import,art_accepted | ConvertTo-Json
