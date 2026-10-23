$ErrorActionPreference='Continue'
$src='C:\UEProjects\DengYingShanHai\Builds\FormalMain-Shipping-20261023-Run167\Windows'
$dst='C:\UEProjects\DengYingShanHai\Builds\Upload-20261024\Windows'
if(Test-Path (Split-Path $dst)){ Remove-Item (Split-Path $dst) -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
& robocopy $src $dst /E /NFL /NDL /NJH /NJS /NP | Out-Null
$removed=@()
foreach($f in @("$dst\DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.pdb","$dst\DengYingShanHai\Binaries\Win64\D3D12\x64\d3d12SDKLayers.dll","$dst\Manifest_DebugFiles_Win64.txt")){
  if(Test-Path $f){ Remove-Item $f -Force; $removed += (Split-Path $f -Leaf) }
}
Write-Output ('REMOVED=' + ($removed -join ','))
$sum=(Get-ChildItem $dst -Recurse -File | Measure-Object -Property Length -Sum)
Write-Output ('FILES=' + $sum.Count + ' BYTES=' + $sum.Sum)
$exe=Join-Path $dst 'DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe'
$env:DY_CAMPAIGN_AUTOPLAY='1'
$p=Start-Process -FilePath $exe -ArgumentList '-nosplash' -PassThru
for($i=0;$i -lt 60;$i++){ Start-Sleep -Seconds 1; $p.Refresh(); if($p.MainWindowHandle -ne 0){ break } }
Write-Output ('WINDOW=' + $p.MainWindowHandle + ' after=' + $i)
Start-Sleep -Seconds 30
$p.Refresh()
Write-Output ('ALIVE=' + (-not $p.HasExited) + ' RESPONDING=' + $p.Responding)
$log=Join-Path $env:LOCALAPPDATA 'DengYingShanHai\Saved\CampaignProbe.log'
if(Test-Path $log){ Get-Content $log -Tail 3 | ForEach-Object { Write-Output ('PROBE ' + $_) } } else { Write-Output 'PROBE=none' }
if(-not $p.HasExited){ $p.Kill(); Write-Output 'KILLED' }
