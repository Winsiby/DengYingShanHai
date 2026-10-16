param(
 [Parameter(Mandatory=$true)][string]$AuthorSHA,
 [ValidateSet('Narrow','Wide')][string]$Variant='Narrow',
 [ValidateRange(1,99)][int]$Run=1
)
$ErrorActionPreference='Stop'
. ([ScriptBlock]::Create([IO.File]::ReadAllText('C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ReleaseEntry-20261014\Common.ps1',[Text.Encoding]::UTF8)))
GuardProcesses
if(@(Get-Process -Name blender -ErrorAction SilentlyContinue).Count){throw 'Preserve other Blender process'}
$script=Join-Path $PSScriptRoot $(if($Variant -eq 'Wide'){'build_canopy_wide.py'}else{'build_canopy.py'})
if((Hash $script) -cne $AuthorSHA){throw 'Exact reviewed author source required'}
$out=Join-Path $PSScriptRoot ('SourceNative-Run'+$Run)
$source=Join-Path $PSScriptRoot ('Source-Run'+$Run)
if((Test-Path -LiteralPath $out) -or (Test-Path -LiteralPath $source)){throw 'Preserve prior source and evidence'}
New-Item -ItemType Directory -Path $out|Out-Null
[IO.File]::Copy($script,(Join-Path $out 'build_canopy.py'),$false)
[IO.File]::Copy($PSCommandPath,(Join-Path $out 'Run-Source.ps1'),$false)
$blender='C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ArtProduction-20261014\Tooling\Portable-Run1\blender-4.5.14-windows-x64\blender.exe'
$arguments='--background --factory-startup --disable-autoexec --python-exit-code 1 --python "'+$script+'" -- --out "'+$source+'"'
$code=Native $blender $arguments $out 'Blender' @{}
if($null -eq $code -or $code -ne 0){throw 'Actual source generation failed; preserve failed evidence'}
if((Hash $script) -cne $AuthorSHA){throw 'Author changed during run'}
$record=ReadJson (Join-Path $source 'SOURCE.json')
if($record.schema -cne 'ForestCanopySource.v1' -or $record.author_tool.sha256 -cne $AuthorSHA -or $record.scope.native_verified -or $record.scope.art_accepted -or $record.scope.D_writes){throw 'Real bounded local-only source record required'}
WriteNew (Join-Path $out 'COMPLETION.json') ([ordered]@{ActualExit=$code;Source=$source;FBX=$record.fbx;SourceMesh=$record.source_mesh|Select-Object vertices,triangles,bounds_cm,material_triangle_counts;ActualRenderedPreviews=$record.previews;NativeVerified=$false;ArtAccepted=$false;GoalComplete=$false})
Write-Output (Join-Path $source 'SOURCE.json')
