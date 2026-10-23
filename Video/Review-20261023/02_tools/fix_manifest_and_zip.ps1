$ErrorActionPreference='Continue'
$win='C:\UEProjects\DengYingShanHai\Builds\Upload-20261024\Windows'
$m=Join-Path $win 'Manifest_NonUFSFiles_Win64.txt'
$lines=Get-Content -LiteralPath $m
$kept=$lines | Where-Object { $_ -notmatch 'd3d12SDKLayers' }
Set-Content -LiteralPath $m -Value $kept -Encoding ascii
Write-Output ('MANIFEST_LINES ' + $lines.Count + ' -> ' + $kept.Count)
$hit=Select-String -LiteralPath $m -Pattern 'SDKLayers' -SimpleMatch
Write-Output ('REMAINING_HITS=' + [int]($hit | Measure-Object).Count)
$exe=Join-Path $win 'DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe'
$env:DY_CAMPAIGN_AUTOPLAY='1'
$p=Start-Process -FilePath $exe -ArgumentList '-nosplash' -PassThru
for($i=0;$i -lt 60;$i++){ Start-Sleep -Seconds 1; $p.Refresh(); if($p.MainWindowHandle -ne 0){ break } }
Start-Sleep -Seconds 20
$p.Refresh()
Write-Output ('WINDOW=' + ($p.MainWindowHandle -ne 0) + ' ALIVE=' + (-not $p.HasExited) + ' RESPONDING=' + $p.Responding)
if(-not $p.HasExited){ $p.Kill() }
$out='C:\UEProjects\DengYingShanHai\Builds\Upload-20261024\DengYingShanHai_Upload_20261024.zip'
if(Test-Path $out){ Remove-Item $out -Force }
Push-Location 'C:\UEProjects\DengYingShanHai\Builds\Upload-20261024'
& 'C:\Windows\System32\tar.exe' -a -c -f $out Windows '上传说明.txt'
Pop-Location
$f=Get-Item $out
Write-Output ('ZIP_BYTES=' + $f.Length)
