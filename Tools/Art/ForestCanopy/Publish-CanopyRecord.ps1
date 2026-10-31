$ErrorActionPreference='Stop'
. ([ScriptBlock]::Create([IO.File]::ReadAllText('C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ReleaseEntry-20261014\Common.ps1',[Text.Encoding]::UTF8)))
$audit=Join-Path $taskRoot 'Saved\Audit-2026-10-14-ArtAppearance'
$baseline=ReadJson (Join-Path $audit 'ForestCanopyWideCapture-Run1\AFTER-426.json')
if($baseline.Count -ne 426){throw '426 frozen products required'}
CheckRows $baseline
SetMatch @($baseline.Relative|ForEach-Object {$_.Replace('/','\')}) (Products)
GuardProcesses
$target=Safe 'Docs\FOREST_CANOPY_20261016.md'
if(Test-Path -LiteralPath $target){throw 'Never overwrite existing record'}
$out=Join-Path $audit 'ForestCanopyRecord-Publish1'
if(Test-Path -LiteralPath $out){throw 'Preserve existing publication evidence'}
$source=Join-Path $PSScriptRoot 'FOREST_CANOPY_20261016.md'
$expected=(Hash $source)
New-Item -ItemType Directory -Path $out|Out-Null
[IO.File]::Copy($PSCommandPath,(Join-Path $out 'Publish-CanopyRecord.ps1'),$false)
[IO.File]::Copy($source,(Join-Path $out 'FOREST_CANOPY_20261016.md'),$false)
WriteNew (Join-Path $out 'BEFORE.json') $baseline
[IO.File]::Copy($source,$target,$false)
if((Hash $target) -cne $expected){throw 'Publication byte mismatch'}
CheckRows $baseline
SetMatch @(@($baseline.Relative|ForEach-Object {$_.Replace('/','\')})+'Docs\FOREST_CANOPY_20261016.md') (Products)
WriteNew (Join-Path $out 'AFTER-427.json') (Rows (Products))
WriteNew (Join-Path $out 'COMPLETION.json') ([ordered]@{Products=427;Original426Unchanged=$true;Added='Docs/FOREST_CANOPY_20261016.md';SHA256=$expected;ArtAccepted=$false;GitWrites=$false;GoalComplete=$false})
Write-Output 'Published one new document; original 426 products unchanged; 427 total.'
