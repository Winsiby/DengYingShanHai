$ErrorActionPreference='Stop'
. ([ScriptBlock]::Create([IO.File]::ReadAllText('C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ReleaseEntry-20261014\Common.ps1',[Text.Encoding]::UTF8)))
$audit=Join-Path $taskRoot 'Saved\Audit-2026-10-14-ArtAppearance'
$baseline=ReadJson (Join-Path $audit 'ForestCanopyRecord-Publish1\AFTER-427.json')
if($baseline.Count -ne 427){throw '427 frozen products required'}
CheckRows $baseline
SetMatch @($baseline.Relative|ForEach-Object {$_.Replace('/','\')}) (Products)
$relative='Docs\FOREST_CANOPY_20261016.md'
$target=Safe $relative
$old=[IO.File]::ReadAllText($target,[Text.Encoding]::UTF8)
$source=Join-Path $PSScriptRoot 'FOREST_CANOPY_20261016.md'
$new=[IO.File]::ReadAllText($source,[Text.Encoding]::UTF8)
$before='复用原叶材质；未改旧425项以外的产品'
$after='复用原叶材质；创建前423项不变；新增两项后共425，独立冷读零Save'
if(-not $old.Contains($before) -or $old.Replace($before,$after) -cne $new){throw 'Only the exact asset-create baseline sentence may change'}
$out=Join-Path $audit 'ForestCanopyRecord-Correct1'
if(Test-Path -LiteralPath $out){throw 'Preserve evidence'}
New-Item -ItemType Directory -Path $out|Out-Null
[IO.File]::Copy($target,(Join-Path $out 'BEFORE.md'),$false)
[IO.File]::Copy($PSCommandPath,(Join-Path $out 'Correct-CanopyRecord.ps1'),$false)
[IO.File]::Copy($source,$target,$true)
CheckRows @($baseline|Where-Object {$_.Relative.Replace('/','\') -ine $relative})
SetMatch @($baseline.Relative|ForEach-Object {$_.Replace('/','\')}) (Products)
WriteNew (Join-Path $out 'AFTER-427.json') (Rows (Products))
WriteNew (Join-Path $out 'COMPLETION.json') ([ordered]@{Products=427;OriginalOther426Unchanged=$true;Changed=$relative;SHA256=(Hash $target);Reason='Correct the asset-create 423-to-425 chronology only';ArtAccepted=$false})
Write-Output 'Corrected one document sentence; other 426 products unchanged.'
