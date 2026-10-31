# Independent Editor-only Dev preview. Never launch as -game or a packaged finale.
param(
    [ValidateRange(0.25,30)][double]$DropSeconds=2,
    [ValidateRange(0.25,60)][double]$GrowthSeconds=6,
    [ValidateRange(0,30)][double]$FinalHoldSeconds=6,
    [ValidatePattern('^Run[1-9][0-9]*$')][string]$Run,
    [switch]$DryRun
)
$ErrorActionPreference='Stop'
$invocationRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$projectRoot='C:\UEProjects\DengYingShanHai'
$junction=Get-Item -LiteralPath $projectRoot
$junctionTarget=[string](@($junction.Target)[0])
if($junction.LinkType -ne 'Junction'){throw 'English project path is not the expected junction'}
$physicalRoot=(Resolve-Path -LiteralPath $junctionTarget).Path
if($invocationRoot.TrimEnd('\') -ne $physicalRoot.TrimEnd('\') -and $invocationRoot.TrimEnd('\') -ne $projectRoot){throw 'English project junction does not target the launcher workspace'}
$editor='C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$project=Join-Path $projectRoot 'DengYingShanHai.uproject'
$script=Join-Path $projectRoot 'Scripts\Preview-P03Continuous.py'
$map=Join-Path $projectRoot 'Content\DengYingShanHai\Dev\M3\Maps\LV_M3GeometryProbe.umap'
$audit=Join-Path $projectRoot 'Saved\Audit-2026-10-04-P03ContinuousPreview'
foreach($required in @($editor,$project,$script,$map)){if(-not(Test-Path -LiteralPath $required -PathType Leaf)){throw "Missing required preview file: $required"}}
if(-not $Run){
    $number=1
    while((Test-Path -LiteralPath (Join-Path $audit "Run$number")) -or (Test-Path -LiteralPath (Join-Path $audit "Preview-Run$number.log"))){$number++}
    $Run="Run$number"
}
$output=Join-Path $audit $Run
$log=Join-Path $audit ("Preview-$Run.log")
if((Test-Path -LiteralPath $output) -or (Test-Path -LiteralPath $log)){throw 'Existing evidence path: refuse overwrite'}
$arguments=@('"'+$project+'"','-ExecutePythonScript="'+$script+'"','-nosplash','-log','-abslog="'+$log+'"')
$report=[ordered]@{Run=$Run;Output=$output;Log=$log;DropSeconds=$DropSeconds;GrowthSeconds=$GrowthSeconds;FinalHoldSeconds=$FinalHoldSeconds;TemporaryPreviewValues=$true;FormalSecondsApproved=$false;EditorOnly=$true}
if($DryRun){$report.Command='"'+$editor+'" '+($arguments -join ' ');$report|ConvertTo-Json -Depth 4;return}
if(Get-Process -Name UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue){throw 'Close existing UE windows before running the isolated preview'}
$names=@('DY_FOREST_PREVIEW_OUT','DY_FOREST_COMPOSITION_OUT','DY_BRANCH_REFINEMENT_OUT','DY_P03_CONTINUOUS_OUT','DY_P03_DROP_SECONDS','DY_P03_GROWTH_SECONDS','DY_P03_FINAL_HOLD_SECONDS')
$previous=@{};foreach($name in $names){$previous[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
try{
    foreach($name in $names){if(Test-Path -LiteralPath ('Env:'+$name)){Remove-Item -LiteralPath ('Env:'+$name)}}
    [Environment]::SetEnvironmentVariable('DY_P03_CONTINUOUS_OUT',$output,'Process')
    $invariant=[Globalization.CultureInfo]::InvariantCulture
    [Environment]::SetEnvironmentVariable('DY_P03_DROP_SECONDS',$DropSeconds.ToString($invariant),'Process')
    [Environment]::SetEnvironmentVariable('DY_P03_GROWTH_SECONDS',$GrowthSeconds.ToString($invariant),'Process')
    [Environment]::SetEnvironmentVariable('DY_P03_FINAL_HOLD_SECONDS',$FinalHoldSeconds.ToString($invariant),'Process')
    Write-Host 'DEV CONTINUOUS PREVIEW ONLY: automatic Resolve fixture -> actual A contact -> real branch shadows.'
    Write-Host 'Keep the mouse and keyboard still. Temporary preview seconds are not final game timing.'
    Write-Host 'The diagnostic restores temporary objects and closes when finished. Existing M2 and launchers are unchanged.'
    $process=Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
    $report.ProcessId=$process.Id
    $report|ConvertTo-Json -Depth 4
}finally{
    foreach($name in $names){
        if($null -eq $previous[$name]){if(Test-Path -LiteralPath ('Env:'+$name)){Remove-Item -LiteralPath ('Env:'+$name)}}
        else{[Environment]::SetEnvironmentVariable($name,$previous[$name],'Process')}
    }
}
