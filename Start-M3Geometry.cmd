@echo off
REM Geometry-only Dev/M3 launcher. Does not change default map or accepted M2.
setlocal
set "SCRIPT=%~dp0Scripts\Start-M3Geometry.ps1"
if not exist "%SCRIPT%" (
    echo ERROR: missing launcher script.
    pause
    exit /b 1
)
powershell -ExecutionPolicy Bypass -File "%SCRIPT%" %*
if errorlevel 1 (
    echo Launch failed. Send the error to Codex.
    pause
    exit /b 1
)
endlocal
