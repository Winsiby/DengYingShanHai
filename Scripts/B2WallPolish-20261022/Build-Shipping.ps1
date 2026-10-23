param()
$ErrorActionPreference='Stop'
$env:PSModulePath=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\Modules'
Import-Module (Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1') -Force
$root='D:\灯影山海'
$artAudit=Join-Path $root 'Saved\Audit-2026-10-22-B2WallPolish'
$buildAudit=Join-Path $artAudit 'Package-B2WallPolish'
$archiveBase=Join-Path $root 'Builds\FormalMain-Shipping-20261022-B2WallPolish'
$archive=Join-Path $archiveBase 'Windows'
$mapFile=Join-Path $root 'Content\DengYingShanHai\Maps\L_DY_Main.umap'
$sourceHash=(Get-FileHash -LiteralPath $mapFile -Algorithm SHA256).Hash
if(Test-Path -LiteralPath $archiveBase){throw 'Archive already exists; use a new version, never overwrite.'}
New-Item -ItemType Directory -Path $buildAudit -Force | Out-Null
$uat='C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\RunUAT.bat'
$uatArgs=@('BuildCookRun','-project=C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject','-noP4','-platform=Win64','-clientconfig=Shipping','-build','-cook','-stage','-pak','-iostore','-archive',('-archivedirectory='+$archiveBase),('-CookOutputDir='+$root+'\Saved\B2WallPolish-20261022-Cook\Windows'),('-stagingdirectory='+$root+'\Saved\B2WallPolish-20261022-Stage'),'-map=/Game/DengYingShanHai/Maps/L_DY_Main','-ubtargs="-NoUBA -MaxParallelActions=2"','-unattended','-utf8output')
[ordered]@{Executable=$uat;Arguments=$uatArgs;SourceMapSHA256=$sourceHash;StartedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $buildAudit 'COMMAND.json') -Encoding UTF8
try{
  & $uat @uatArgs 1> (Join-Path $buildAudit 'UAT-stdout.log') 2> (Join-Path $buildAudit 'UAT-stderr.log')
  $actualExit=$LASTEXITCODE
  [ordered]@{ActualExit=$actualExit;CompletedUtc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $buildAudit 'UAT-EXIT.json') -Encoding UTF8
  if($actualExit -ne 0){throw ('UAT failed '+$actualExit)}
  if((Get-FileHash -LiteralPath $mapFile -Algorithm SHA256).Hash -ne $sourceHash){throw 'Source map changed during cook.'}
  $nativeRelative='DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe'
  $native=Join-Path $archive $nativeRelative
  if(-not(Test-Path -LiteralPath $native)){throw 'Native executable missing.'}
  $ufs=Join-Path $archive 'Manifest_UFSFiles_Win64.txt'
  $ufsFiles=@(Get-Content -LiteralPath $ufs -Encoding UTF8|ForEach-Object{($_ -split "`t",2)[0]})
  $maps=@($ufsFiles|Where-Object{$_ -like '*.umap'})
  if(-not($maps -contains 'DengYingShanHai/Content/DengYingShanHai/Maps/L_DY_Main.umap')){throw 'Main map missing from manifest.'}
  if(-not @($ufsFiles|Where-Object{$_ -like '*ArtPolish_20261022*SM_DY_LanternFamily_Unit100*'}).Count){throw 'New lantern mesh missing from cook manifest.'}
  if($maps.Count -ne 2){throw 'Unexpected cooked map roots; candidate map must not cook.'}
  foreach($needed in @('*B2WallPolish_20261022*SM_DY_BranchCrown_A_Unit100*','*B2WallPolish_20261022*SM_DY_BranchCrown_B_Unit100*','*B2WallPolish_20261022*M_DY_WallBands*')){
    if(-not @($ufsFiles|Where-Object{$_ -like $needed}).Count){throw ('Required new art missing from cook: '+$needed)}
  }
  $rows=@(Get-ChildItem -LiteralPath $archive -Recurse -File|Sort-Object FullName|ForEach-Object{[ordered]@{Relative=$_.FullName.Substring($archive.Length+1);Bytes=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
  $bytes=($rows|ForEach-Object{[long]$_.Bytes}|Measure-Object -Sum).Sum
  $identity=[ordered]@{Status='PASS-BUILD-COOK-STAGE-ARCHIVE';Succeeded=$true;Map='/Game/DengYingShanHai/Maps/L_DY_Main';CookRoot='/Game/DengYingShanHai/Maps/L_DY_Main';Configuration='Shipping';Target='Game';Platform='Win64';Engine='5.8.3';ArchiveRoot=$archive;BuildAudit=$buildAudit;UATActualExit=$actualExit;CookedMaps=$maps;CookedMapCount=$maps.Count;NativeExecutable=$nativeRelative;NativeExeSHA256=(Get-FileHash -LiteralPath $native -Algorithm SHA256).Hash;SourceMapSHA256=$sourceHash;ArtifactFileCount=$rows.Count;ArtifactBytes=$bytes;CreatedUtc=[DateTime]::UtcNow.ToString('o');FirstFrameVerified=$false;GameplayVerified=$false;HumanVisualAcceptance=$false;ShippingBuilt=$true;LicenseRegisterRead=$true}
  $identity|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $archive 'RELEASE-ENTRY-BUILD.json') -Encoding UTF8
  $rows|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $buildAudit 'ARTIFACTS.json') -Encoding UTF8
  $identity|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $buildAudit 'RESULT.json') -Encoding UTF8
  Write-Output ('PASS package '+$archive+' files='+$rows.Count+' bytes='+$bytes)
}catch{
  [ordered]@{Status='FAILED';Error=$_.Exception.Message;ActualExit=$actualExit}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $buildAudit 'FAILED.json') -Encoding UTF8
  throw
}
