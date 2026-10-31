$ErrorActionPreference='Stop'
$dyRoot=Split-Path -Parent $PSScriptRoot
$dyTool=Join-Path $dyRoot 'Saved\ArtPolish-2026-10-25\Tools\Runtime-Launch.ps1'
Write-Host 'Art preview: Development RunD13. Final Shipping acceptance is pending.'
& $dyTool -Configuration Development -Attempt RunD13 -Mode Manual -Session ('UserPreview-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff')) -ResX 1280 -ResY 800 -Execute
