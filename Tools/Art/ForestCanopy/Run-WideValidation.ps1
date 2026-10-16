$ErrorActionPreference='Stop'
$entry=Join-Path $PSScriptRoot 'Run-Wide.ps1'
$review=Join-Path $PSScriptRoot 'REVIEWED-Wide1.json'
$audit='D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance'
$createdAssets=Join-Path $audit 'ForestCanopyWideAssetCreate-Run1\AFTER-425.json'
& $entry -Kind AssetVerify -Baseline $createdAssets -Reviewed $review -Run 1
if(-not $?){throw 'Stop after failed cold asset verification'}
$verifiedAssets=Join-Path $audit 'ForestCanopyWideAssetVerify-Run1\AFTER-425.json'
& $entry -Kind MapCreate -Baseline $verifiedAssets -Reviewed $review -Run 1
if(-not $?){throw 'Stop after failed first map save; never retry existing destination'}
$createdMap=Join-Path $audit 'ForestCanopyWideMapCreate-Run1\RESULT.json'
$mapBaseline=Join-Path $audit 'ForestCanopyWideMapCreate-Run1\AFTER-426.json'
& $entry -Kind MapVerify -Baseline $mapBaseline -Created $createdMap -Reviewed $review -Run 1
if(-not $?){throw 'Stop after failed cold map verification'}
$verifiedMap=Join-Path $audit 'ForestCanopyWideMapVerify-Run1\AFTER-426.json'
& $entry -Kind Capture -Baseline $verifiedMap -Reviewed $review -Run 1
if(-not $?){throw 'Stop after failed actual PIE capture'}
