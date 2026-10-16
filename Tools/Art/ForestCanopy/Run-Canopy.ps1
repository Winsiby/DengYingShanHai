param(
 [Parameter(Mandatory=$true)][ValidateSet('AssetCreate','AssetVerify','MapCreate','MapVerify','Capture')][string]$Kind,
 [Parameter(Mandatory=$true)][string]$Baseline,
 [Parameter(Mandatory=$true)][string]$Reviewed,
 [string]$Created,
 [ValidateSet('1','2.4')][string]$DiameterFactor='1',
 [ValidateRange(1,99)][int]$Run=1
)
$ErrorActionPreference='Stop'
. ([ScriptBlock]::Create([IO.File]::ReadAllText('C:\Users\lenovo\.codex\visualizations\2026\09\30\01a0f245-1d70-7ba1-9b69-e6db6a9b7948\ReleaseEntry-20261014\Common.ps1',[Text.Encoding]::UTF8)))
$auditRoot=Join-Path $taskRoot 'Saved\Audit-2026-10-14-ArtAppearance'
if(-not [IO.Path]::IsPathRooted($Baseline) -or -not [IO.Path]::GetFullPath($Baseline).StartsWith($auditRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Explicit bounded baseline required'}
$frozen=ReadJson $Baseline
if($frozen.Count -lt 419){throw 'Current 419 or later product baseline required'}
CheckRows $frozen
$recoverSavedMap=$false
if($Kind -eq 'MapVerify' -and $Created){
 $knownCreate=Join-Path $auditRoot 'ForestCanopyMapCreate-Run1\RESULT.json'
 if([IO.Path]::GetFullPath($Created) -ieq $knownCreate -and -not (ReadJson $Created).success){
  $proofs=@(
   @('RESULT.json','0BA3DD5B9C3562E1CFA83B395E2CF3772BFC01325330A2A2EDB5342E7C9F9BAE'),
   @('DISK-DELTA.json','9D0D92C97864AA164CDC53DDFA2FD938217DD18F873386D8C2D15C365F5F1949'),
   @('Editor-EXIT.json','94C52227B48DC1219DD763526640FEA123A33B00C0AC6DCB1753CE50E57AAA84')
  )
  foreach($proof in $proofs){if((Hash (Join-Path (Split-Path $Created) $proof[0])) -cne $proof[1]){throw 'Exact preserved save-as diagnostic proof required'}}
  $originalBefore=ReadJson (Join-Path (Split-Path $Created) 'BEFORE.json')
  CheckRows $originalBefore
  if($frozen.Count -ne 422 -or $originalBefore.Count -ne 422){throw 'Exact prior 422 products required'}
  SetMatch @($frozen.Relative) @($originalBefore.Relative)
  $onlyNew='Content\DengYingShanHai\Dev\ForestCanopy\Maps\LV_ForestCanopyLab.umap'
  if((Hash (Safe $onlyNew)) -cne '28C92B049D46F431ADC1F7FA8227967AA790D2CC204FEF8A24684F303986E53F'){throw 'Exact already-written unaccepted map required'}
  SetMatch @(@($frozen.Relative|ForEach-Object {$_.Replace('/','\')})+$onlyNew) (Products)
  $frozen=Rows (Products)
  $recoverSavedMap=$true
 }
}
SetMatch @($frozen.Relative|ForEach-Object {$_.Replace('/','\')}) (Products)
GuardProcesses
$review=ReadJson $Reviewed
if($review.SourceTarget -cne 'Assets\Sources\DengYingArt\ForestCanopy-20261016'){throw 'Exact new source destination required'}
foreach($row in @($review.Sources)+@($review.Tools)){
 if(-not [IO.Path]::IsPathRooted($row.Source) -or (Get-Item -LiteralPath $row.Source).Length -ne $row.Bytes -or (Hash $row.Source) -cne $row.SHA256){throw ('Reviewed local bytes mismatch '+$row.Source)}
}
$out=Join-Path $auditRoot ('ForestCanopy'+$Kind+'-Run'+$Run)
if(Test-Path -LiteralPath $out){throw 'Preserve prior evidence'}
if($Kind -eq 'MapVerify'){
 if(-not $Created -or -not [IO.Path]::IsPathRooted($Created) -or -not [IO.Path]::GetFullPath($Created).StartsWith($auditRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Explicit own map-create report required'}
 $creation=ReadJson $Created
 if(-not $creation.success -and -not $recoverSavedMap){throw 'Successful create or exact independently checked save-as diagnostic required'}
}
$sourceDir=Safe $review.SourceTarget
if(-not (Test-Path -LiteralPath $sourceDir)){
 if($Kind -ne 'AssetCreate'){throw 'Published reviewed sources required'}
 New-Item -ItemType Directory -Path $sourceDir|Out-Null
 foreach($row in $review.Sources){
  if([IO.Path]::GetFileName($row.Name) -cne $row.Name){throw 'Flat exact source filename required'}
  [IO.File]::Copy($row.Source,(Join-Path $sourceDir $row.Name),$false)
 }
}
SetMatch @($review.Sources.Name) @(Get-ChildItem -LiteralPath $sourceDir -File|ForEach-Object Name)
function CheckCanopySources {
 foreach($row in $review.Sources){$p=Join-Path $sourceDir $row.Name;if((Get-Item -LiteralPath $p).Length -ne $row.Bytes -or (Hash $p) -cne $row.SHA256){throw 'Published source bytes mismatch'}}
}
CheckCanopySources
New-Item -ItemType Directory -Path $out|Out-Null
$scriptName=if($Kind.StartsWith('Asset')){'native_canopy.py'}elseif($Kind.StartsWith('Map')){'candidate_map.py'}else{'capture_canopy.py'}
$scriptSource=Join-Path $PSScriptRoot $scriptName
if(@($review.Tools|Where-Object {$_.Source -ceq $scriptSource}).Count -ne 1){throw 'Exact reviewed native script required'}
$script=Join-Path $out $scriptName
[IO.File]::Copy($scriptSource,$script,$false)
[IO.File]::Copy($PSCommandPath,(Join-Path $out 'Run-Canopy.ps1'),$false)
[IO.File]::Copy($Reviewed,(Join-Path $out 'REVIEWED.json'),$false)
WriteNew (Join-Path $out 'BEFORE.json') $frozen
$fbx=@($review.Sources|Where-Object {$_.Name -ceq 'forest-branch-leafed.fbx'})
$meta=@($review.Sources|Where-Object {$_.Name -ceq 'SOURCE.json'})
if($fbx.Count -ne 1 -or $meta.Count -ne 1){throw 'One FBX and source metadata required'}
$envs=@{
 DY_FOREST_CANOPY_PHASE=$(if($Kind -eq 'AssetCreate'){'create'}else{'verify'});
 DY_FOREST_CANOPY_OUT=(Join-Path $out 'RESULT.json');
 DY_FOREST_CANOPY_SOURCE_SHA=$fbx[0].SHA256;
 DY_FOREST_CANOPY_META_SHA=$meta[0].SHA256;
 DY_CANOPY_MAP_PHASE=$(if($Kind -eq 'MapCreate'){'create'}else{'verify'});
 DY_CANOPY_MAP_OUT=(Join-Path $out 'RESULT.json');
 DY_CANOPY_MAP_CREATED=$Created;
 DY_ART_FROZEN=(Join-Path $out 'BEFORE.json');
 DY_STAGE_MAP_COMPOSE_OBSERVER=(Join-Path (Split-Path $PSScriptRoot) 'StageComposition\compose_stage.py');
 DY_FOREST_CAPTURE_OUT=$out;
 DY_CANOPY_DIAMETER_FACTOR=$DiameterFactor
}
$arguments='"C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject" "-ExecutePythonScript='+$script+'" -unattended -nosplash -NoSound "-abslog='+(Join-Path $out 'Session.log')+'"'
$code=Native 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' $arguments $out 'Editor' $envs
CheckRows $frozen
CheckCanopySources
$prior=@($frozen.Relative|ForEach-Object {$_.Replace('/','\')})
$new=@((Products)|Where-Object {$_ -notin $prior})
WriteNew (Join-Path $out 'DISK-DELTA.json') ([ordered]@{ActualExit=$code;FrozenCount=$frozen.Count;FrozenUnchanged=$true;NewFiles=$new})
if($null -eq $code -or $code -ne 0){throw 'Actual zero native exit required'}
$report=ReadJson (Join-Path $out 'RESULT.json')
if(-not $report.success){$report.error|Write-Output;throw 'Native canopy operation failed; preserve evidence'}
$expected=@(if($Kind -eq 'AssetCreate'){
 'Content\DengYingShanHai\Dev\ForestCanopy\Meshes\SM_DY_ForestBranch_Leafed.uasset'
 'Content\DengYingShanHai\Dev\ForestCanopy\Materials\M_DY_ForestLeaf.uasset'
 'Content\DengYingShanHai\Dev\ForestCanopy\Presentation\BP_DYForestCanopy_Leafed.uasset'
}elseif($Kind -eq 'MapCreate'){
 'Content\DengYingShanHai\Dev\ForestCanopy\Maps\LV_ForestCanopyLab.umap'
})
SetMatch $expected $new
if($Kind -eq 'Capture' -and (-not $report.actual_pie_ended -or $report.saved.Count -or $report.captures.Count -lt 5 -or -not $report.geometry_grid.count)){throw 'Actual causal captures, pure geometry grid, EndPIE and zero saves required'}
WriteNew (Join-Path $out ('AFTER-'+((Products).Count)+'.json')) (Rows (Products))
WriteNew (Join-Path $out 'COMPLETION.json') ([ordered]@{ActualExit=$code;PriorProductsUnchanged=$true;Products=(Products).Count;Saved=$report.saved;Captures=$report.captures.Count;VisualReviewPending=($Kind -eq 'Capture');ColdReadAfterRejectedPostSaveAssumption=$recoverSavedMap;FailedCreateEvidenceUnchanged=$true;OldMapsChanged=$false;OldLaunchersOrPackagesChanged=$false;GitWrites=$false;ArtGoalComplete=$false;GoalComplete=$false})
Write-Output (Join-Path $out 'RESULT.json')
