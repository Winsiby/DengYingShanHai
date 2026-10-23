$ErrorActionPreference='Stop'
$artAudit='D:\灯影山海\Saved\Audit-2026-10-22-ArtPolish'
$scriptDir='D:\灯影山海\Scripts\ArtPolish-20261022'
function SaveStage($stage,$status,$detail=''){[ordered]@{Stage=$stage;Status=$status;Detail=$detail;Utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $artAudit 'PIPELINE.json') -Encoding UTF8}
try{
 if(@(Get-Process UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue).Count){throw 'Existing editor detected.'}
 SaveStage 'FinalFixedViews' 'RUNNING'
 $env:DY_SCRIPT=Join-Path $scriptDir 'Capture-ArtReview.py';$env:DY_ART_PHASE='Final'
 $p=Start-Process -FilePath 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe' -ArgumentList @('C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject','-nosplash','-nop4','-nosound','-unattended','-RenderOffscreen',('-AbsLog='+$artAudit+'\Final-Capture-Editor.log')) -WorkingDirectory 'D:\灯影山海' -WindowStyle Hidden -PassThru
 $p.WaitForExit()
 $renderReport=Get-Content -LiteralPath (Join-Path $artAudit 'Final-capture.json') -Raw|ConvertFrom-Json
 if(-not $renderReport.ok){throw 'Final captures failed.'}
 Remove-Item Env:DY_SCRIPT -ErrorAction SilentlyContinue
 Remove-Item Env:DY_ART_PHASE -ErrorAction SilentlyContinue
 SaveStage 'NativeAutomation' 'RUNNING'
 & (Join-Path $scriptDir 'Run-ArtChecks.ps1')
 SaveStage 'ShippingBuild' 'RUNNING'
 & (Join-Path $scriptDir 'Build-ArtShipping.ps1')
 SaveStage 'BuildReadyForRuntimeVerification' 'PASS'
}catch{SaveStage 'Pipeline' 'FAILED' $_.Exception.Message;throw}
