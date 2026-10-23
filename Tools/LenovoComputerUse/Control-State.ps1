param([switch]$Stop, [switch]$Resume)
$ErrorActionPreference = 'Stop'
if ($Stop -eq $Resume) { throw 'Choose exactly one of -Stop or -Resume' }
$workspacePath = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$statePath = Join-Path $workspacePath 'Saved\LenovoComputerUse'
$markerPath = Join-Path $statePath 'STOP'
if ($Stop) {
    New-Item -ItemType Directory -Path $statePath -Force | Out-Null
    New-Item -ItemType File -Path $markerPath -Force | Out-Null
    Write-Host 'Lenovo Computer Use STOPPED.'
} elseif (Test-Path -LiteralPath $markerPath) {
    Remove-Item -LiteralPath $markerPath
    Write-Host 'Lenovo Computer Use resumed by the user.'
}
