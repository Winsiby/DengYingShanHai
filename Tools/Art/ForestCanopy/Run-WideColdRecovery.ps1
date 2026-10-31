$ErrorActionPreference='Stop'
. ([ScriptBlock]::Create([IO.File]::ReadAllText('C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ReleaseEntry-20261014\Common.ps1',[Text.Encoding]::UTF8)))
$audit=Join-Path $taskRoot 'Saved\Audit-2026-10-14-ArtAppearance'
$failed=Join-Path $audit 'ForestCanopyWideMapCreate-Run1'
$prior=ReadJson (Join-Path $audit 'ForestCanopyWideAssetVerify-Run1\AFTER-425.json')
if($prior.Count -ne 425){throw 'Exact pre-map product baseline required'}
CheckRows $prior
$proofs=@(
 @('Editor-EXIT.json','66CA4A6DC6C635EF296099B9F7B38C10FEC68F2F0D24BC8B3DD3C51642BEB64B'),
 @('DISK-DELTA.json','CF86784E690CB89C3662947D1315F2BBC29D9F41BF3F62DCE326B4E791DC9D5A'),
 @('Session.log','0583AB7FB7DA42B9BA706EBB18C4AA7502EBA6C5F3954F0CE2C164EB19756664')
)
foreach($proof in $proofs){if((Hash (Join-Path $failed $proof[0])) -cne $proof[1]){throw 'Exact original failed native evidence required'}}
if(Test-Path -LiteralPath (Join-Path $failed 'RESULT.json')){throw 'Original crash produced no Python result; never fabricate one'}
$map='Content\DengYingShanHai\Dev\ForestCanopyWide\Maps\LV_ForestCanopyWideLab.umap'
if((Hash (Safe $map)) -cne 'FE49571ED7EB5F0E36C8BD5D55B149651B94901D22572D36FACEA0829727336A'){throw 'Exact already-saved, unaccepted new map required'}
SetMatch @(@($prior.Relative|ForEach-Object {$_.Replace('/','\')})+$map) (Products)
$frozen=Rows (Products)
GuardProcesses
$out=Join-Path $audit 'ForestCanopyWideMapColdRecovery-Run1'
if(Test-Path -LiteralPath $out){throw 'Preserve previous evidence'}
$scriptSource=Join-Path $PSScriptRoot 'verify_saved_wide_map.py'
$review=ReadJson (Join-Path $PSScriptRoot 'RECOVERY-REVIEWED.json')
if((Get-Item -LiteralPath $scriptSource).Length -ne $review.Bytes -or (Hash $scriptSource) -cne $review.SHA256){throw 'Reviewed independent read-only verifier bytes required'}
New-Item -ItemType Directory -Path $out|Out-Null
$script=Join-Path $out 'verify_saved_wide_map.py'
[IO.File]::Copy($scriptSource,$script,$false)
[IO.File]::Copy($PSCommandPath,(Join-Path $out 'Run-WideColdRecovery.ps1'),$false)
WriteNew (Join-Path $out 'BEFORE.json') $frozen
$envs=@{DY_ART_FROZEN=(Join-Path $out 'BEFORE.json');DY_CANOPY_MAP_PHASE='verify';DY_CANOPY_MAP_OUT=(Join-Path $out 'RESULT.json');DY_STAGE_MAP_COMPOSE_OBSERVER=(Join-Path (Split-Path $PSScriptRoot) 'StageComposition\compose_stage.py')}
$arguments='"C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject" "-ExecutePythonScript='+$script+'" -unattended -nosplash -NoSound "-abslog='+(Join-Path $out 'Session.log')+'"'
$code=Native 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' $arguments $out 'Editor' $envs
CheckRows $frozen
SetMatch @($frozen.Relative|ForEach-Object {$_.Replace('/','\')}) (Products)
WriteNew (Join-Path $out 'DISK-DELTA.json') ([ordered]@{ActualExit=$code;All426ProductsUnchanged=$true;NewFiles=@()})
if($null -eq $code -or $code -ne 0){throw 'Actual zero native exit required'}
$result=ReadJson (Join-Path $out 'RESULT.json')
if(-not $result.success -or $result.saved.Count){$result.error|Write-Output;throw 'Independent full cold-read result and zero saves required'}
WriteNew (Join-Path $out 'AFTER-426.json') (Rows (Products))
WriteNew (Join-Path $out 'COMPLETION.json') ([ordered]@{ActualExit=$code;ColdVerified=$true;Products=426;Saved=@();AllProductsUnchanged=$true;PriorCreationActualExit=3;PriorCrashEvidencePreserved=$true;MapOverwritten=$false;Packaged=$false;ArtAccepted=$false;GitWrites=$false;GoalComplete=$false})
