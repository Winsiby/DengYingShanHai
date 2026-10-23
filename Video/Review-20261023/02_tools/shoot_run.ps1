$ErrorActionPreference='Continue'
$root='C:\UEProjects\DengYingShanHai'
$exe=Join-Path $root 'Builds\FormalMain-Shipping-20261023-Run167\Windows\DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe'
if(-not (Test-Path $exe)){ throw 'exe missing' }
Get-Process -Name DengYingShanHai-Win64-Shipping -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3
$env:DY_CAMPAIGN_AUTOPLAY='1'
$p=Start-Process -FilePath $exe -ArgumentList '-nosplash' -PassThru
Write-Output ('LAUNCH pid=' + $p.Id)
$hwnd=[IntPtr]::Zero
for($i=0;$i -lt 90;$i++){
  Start-Sleep -Seconds 1
  $p.Refresh()
  if($p.MainWindowHandle -ne 0){ $hwnd=$p.MainWindowHandle; break }
}
if($hwnd -eq [IntPtr]::Zero){ Write-Output 'WINDOW=none'; exit 3 }
Write-Output ('WINDOW=ok after ' + $i + 's')
Stop-Process -Name ffmpeg -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$capOut=Join-Path $root 'Video\Review-20261023\01_raw\shots\run_20261024.mp4'
New-Item -ItemType Directory -Force -Path (Split-Path $capOut) | Out-Null
$cap=Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $root 'Video\Review-20261023\02_tools\capture.ps1'),'-Seconds','150','-Out',$capOut) -PassThru -WindowStyle Hidden
Write-Output ('CAPTURE pid=' + $cap.Id)
Start-Sleep -Seconds 8
& powershell -NoProfile -ExecutionPolicy Bypass -File 'C:\dy_build\keys.ps1' -pid_ $p.Id -keys '0D'
Start-Sleep -Seconds 5
& powershell -NoProfile -ExecutionPolicy Bypass -File 'C:\dy_build\walk.ps1' -pid_ $p.Id -key '57' -ms 18000
Write-Output 'INPUT=done'
$cap.WaitForExit()
Write-Output ('CAPTURE_EXIT=' + $cap.ExitCode)
Get-ChildItem -LiteralPath $capOut | Select-Object Name,Length
