@echo off
REM Independent Editor-only Dev continuous preview. Does not change the game.
setlocal
set "DY_CONTINUOUS_SCRIPT=%~dp0Scripts\Start-M3Continuous.ps1"
if not exist "%DY_CONTINUOUS_SCRIPT%" (
    echo ERROR: missing continuous preview launcher.
    pause
    exit /b 1
)
powershell.exe -NoProfile -File "%DY_CONTINUOUS_SCRIPT%" %*
if errorlevel 1 (
    echo Preview launch failed. Send the error to Codex.
    pause
    exit /b 1
)
endlocal
