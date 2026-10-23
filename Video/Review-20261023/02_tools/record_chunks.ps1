param([int]$Chunks = 6, [int]$Seconds = 58, [string]$Dir = "D:\灯影山海\Video\Review-20261023\01_raw\run")
$ErrorActionPreference = "Continue"
if (!(Test-Path $Dir)) { New-Item -ItemType Directory -Path $Dir | Out-Null }
for ($i = 1; $i -le $Chunks; $i++) {
    $out = Join-Path $Dir ("chunk_{0:d2}.mp4" -f $i)
    Write-Output ("chunk " + $i + " start " + (Get-Date -Format "HH:mm:ss"))
    & powershell -NoProfile -ExecutionPolicy Bypass -File "D:\灯影山海\Video\Review-20261023\02_tools\capture.ps1" -Seconds $Seconds -Out $out *> $null
    Write-Output ("chunk " + $i + " done " + (Get-Date -Format "HH:mm:ss"))
}
