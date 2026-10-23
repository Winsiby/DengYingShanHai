param([string]$Prefix="d2",[int]$BootSec=18,[int]$Steps=10,[int]$StepMs=5000)
$ErrorActionPreference="Stop"
$root="D:\灯影山海"
$exe=Join-Path $root "Builds\FormalMain-Development-20261022-RunD1\Windows\DengYingShanHai\Binaries\Win64\DengYingShanHai.exe"
if(-not (Test-Path $exe)){ throw "missing exe $exe" }
$audit=Join-Path $root "Saved\Audit-2026-10-22-FourAct"
Get-Process DengYingShanHai,UnrealEditor,UnrealEditor-Cmd -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 3
$d=Split-Path $exe
$p=Start-Process -FilePath $exe -WorkingDirectory $d -ArgumentList '-windowed','-resx=1600','-resy=1000' -PassThru
Write-Output ("START " + $p.Id)
Start-Sleep -Seconds 8
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\close_dialog.ps1" | Out-Null
Start-Sleep -Seconds $BootSec
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\foreground_retry.ps1" -TargetPid $p.Id | Out-Null
& "C:\dy_build\cap6.ps1" $p.Id (Join-Path $audit ($Prefix+"-menu.png")) | Out-Null
& "C:\dy_build\keys.ps1" $p.Id "0D" | Out-Null
Start-Sleep -Seconds 6
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\foreground_retry.ps1" -TargetPid $p.Id | Out-Null
& "C:\dy_build\keys.ps1" $p.Id "0D" | Out-Null
Start-Sleep -Seconds 5
& "C:\dy_build\cap6.ps1" $p.Id (Join-Path $audit ($Prefix+"-enter.png")) | Out-Null
Write-Output "ENTERED"
for($i=1;$i -le $Steps;$i++){
  & powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\foreground_retry.ps1" -TargetPid $p.Id | Out-Null
  & "C:\dy_build\walk.ps1" $p.Id "57" $StepMs | Out-Null
  $name=$Prefix + ("-w{0:d2}.png" -f $i)
  & "C:\dy_build\cap6.ps1" $p.Id (Join-Path $audit $name) | Out-Null
  Write-Output ("SHOT " + $name)
}
Write-Output "CAPTURE-DONE"
