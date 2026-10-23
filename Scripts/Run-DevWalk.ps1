param([int]$TargetPid, [string]$Prefix="d4", [int]$Steps=8, [int]$StepMs=4500)
$ErrorActionPreference="Stop"
$audit="D:\灯影山海\Saved\Audit-2026-10-22-FourAct"
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\foreground_retry.ps1" -TargetPid $TargetPid | Out-Null
& "C:\dy_build\keys.ps1" $TargetPid "0D" | Out-Null
Start-Sleep -Seconds 7
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\cap_pw.ps1" -TargetPid $TargetPid -OutPath (Join-Path $audit ($Prefix+"-enter.png")) | Out-Null
Write-Output "ENTER-CAPTURED"
for($i=1;$i -le $Steps;$i++){
  & powershell -NoProfile -ExecutionPolicy Bypass -File "C:\dy_build\foreground_retry.ps1" -TargetPid $TargetPid | Out-Null
  & "C:\dy_build\walk.ps1" $TargetPid "57" $StepMs | Out-Null
  $name=$Prefix + ("-w{0:d2}.png" -f $i)
  & "C:\dy_build\cap_pw.ps1" -TargetPid $TargetPid -OutPath (Join-Path $audit $name) | Out-Null
  Write-Output ("SHOT " + $name)
}
Write-Output "WALK-DONE"
