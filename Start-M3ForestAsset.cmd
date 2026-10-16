@echo off
REM Independent Editor/PIE preview loading the SAVED Dev forest Blueprint.
setlocal
set "DY_FOREST_ASSET_SCRIPT=%~dp0Scripts\Start-M3ForestAsset.ps1"
if not exist "%DY_FOREST_ASSET_SCRIPT%" (
    echo ERROR: missing saved forest preview launcher.
    pause
    exit /b 1
)
powershell.exe -NoProfile -File "%DY_FOREST_ASSET_SCRIPT%" %*
if errorlevel 1 (
    echo Saved forest preview launch failed. Send the error to Codex.
    pause
    exit /b 1
)
endlocal
