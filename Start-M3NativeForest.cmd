@echo off
REM Independent unsaved Editor/PIE native forest preview. Not the game finale.
setlocal
set "DY_NATIVE_FOREST_SCRIPT=%~dp0Scripts\Start-M3NativeForest.ps1"
if not exist "%DY_NATIVE_FOREST_SCRIPT%" (
    echo ERROR: missing native preview launcher.
    pause
    exit /b 1
)
powershell.exe -NoProfile -File "%DY_NATIVE_FOREST_SCRIPT%" %*
if errorlevel 1 (
    echo Native preview launch failed. Send the error to Codex.
    pause
    exit /b 1
)
endlocal
