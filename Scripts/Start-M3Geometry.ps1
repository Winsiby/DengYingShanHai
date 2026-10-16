# Launch a geometry-only Dev/M3 sandbox, not a P03 finale. Do not change defaults.
param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$projectPath = 'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject'
$editorPath = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$map = '/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe'
$mapFile = 'C:\UEProjects\DengYingShanHai\Content\DengYingShanHai\Dev\M3\Maps\LV_M3GeometryProbe.umap'
$arguments = @("`"$projectPath`"", $map, '-game', '-windowed', '-ResX=1600', '-ResY=900')
if ($DryRun) { "`"$editorPath`" $($arguments -join ' ')"; return }
foreach ($requiredPath in @($projectPath, $editorPath, $mapFile)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) { throw "Missing required file: $requiredPath" }
}
Write-Host 'M3 GEOMETRY ONLY: E / A-D / E / R retain the M2 sandbox meaning.'
Write-Host 'A = local staff -Z, B = +Z. Markers are NOT shadows or puzzle success.'
Start-Process -FilePath $editorPath -ArgumentList $arguments -WindowStyle Hidden
