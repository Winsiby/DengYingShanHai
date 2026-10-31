param([switch]$RunClipOnly)
$ErrorActionPreference='Stop'
$out=Join-Path $PSScriptRoot $(if($RunClipOnly){'Sam-Run-Original'}else{'Sam-Original'})
if(Test-Path -LiteralPath $out){throw 'Preserve previous original downloads'}
New-Item -ItemType Directory -Path $out | Out-Null
$items=if($RunClipOnly){@(
 @{Slug='run-sam-3d-person-animated-fa008c06';File='sam-run.glb';Clip='Run';DurationClaim=1.333;SpeedClaim=4.5}
)}else{@(
 @{Slug='idle-standing-sam-3d-person-animated-1f9f1217';File='sam-idle.glb';Clip='Idle';DurationClaim=6.0;SpeedClaim=0.0},
 @{Slug='brisk-walk-sam-3d-person-animated-bed03fa4';File='sam-walk.glb';Clip='Walk';DurationClaim=1.733;SpeedClaim=1.7}
)}
$records=@()
foreach($item in $items){
 $page='https://www.innerscene.com/tools/library/3d-parts/'+$item.Slug
 $url='https://www.innerscene.com/api/library/'+$item.Slug+'/download'
 $html=(Invoke-WebRequest -Uri $page -UseBasicParsing).Content
 if($html -notmatch 'Public domain \(CC0\)' -or $html -notmatch [regex]::Escape('/api/library/'+$item.Slug+'/download') -or $html -notmatch 'MakeHuman/MPFB CC0'){throw 'Current original page no longer confirms specific free CC0 asset'}
 $path=Join-Path $out $item.File
 Invoke-WebRequest -Uri $url -OutFile $path
 $file=Get-Item -LiteralPath $path
 if($file.Length -lt 1MB -or $file.Length -gt 60MB){throw 'Unexpected source download size'}
 $stream=[IO.File]::OpenRead($path)
 try{
  $reader=[IO.BinaryReader]::new($stream)
  if($reader.ReadUInt32() -ne 0x46546c67 -or $reader.ReadUInt32() -ne 2 -or $reader.ReadUInt32() -ne $file.Length){throw 'Downloaded file is not a complete GLB v2'}
 }finally{$stream.Dispose()}
 $records+=[ordered]@{File=$item.File;Page=$page;Download=$url;Bytes=$file.Length;SHA256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash;License='CC0-1.0';Author='Innerscene, adapted from MakeHuman/MPFB CC0 assets';ClipClaim=$item.Clip;DurationSecondsClaim=$item.DurationClaim;InPlaceSpeedMpsClaim=$item.SpeedClaim;ClaimsAreNotMeasured=$true;RetrievedAt=(Get-Date).ToString('o')}
}
$record=[ordered]@{Schema='DYPlayerSourceDownload.v1';Files=$records;Terms='https://www.innerscene.com/tools/library/terms';MakeHumanLicense='https://static.makehumancommunity.org/about/license.html';PaidAssets=$false;NativeImported=$false;ArtAccepted=$false;OriginalGameChanged=$false}
[IO.File]::WriteAllText((Join-Path $out 'DOWNLOAD.json'),($record|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
$record|ConvertTo-Json -Depth 8
