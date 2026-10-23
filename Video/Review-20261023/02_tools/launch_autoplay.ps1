$ErrorActionPreference = "Stop"
$exe = "D:\灯影山海\Builds\FormalMain-Shipping-20261023-Run167\Windows\DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe"
$wd = Split-Path $exe -Parent
if (!(Test-Path $exe)) { throw "missing exe" }
$env:DY_CAMPAIGN_AUTOPLAY = "1"
Start-Process -FilePath $exe -WorkingDirectory $wd -ArgumentList "-windowed","-ResX=2560","-ResY=1440","-nosplash"
Write-Output "launched"
