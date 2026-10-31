@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Environment Dev
set "DY_ENV_SCRIPT=%~dp0Scripts\Start-EnvironmentDev.ps1"
if not exist "%DY_ENV_SCRIPT%" (
    echo ERROR: Environment launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_ENV_SCRIPT%" %*
set "DY_ENV_EXIT=%ERRORLEVEL%"
if not "%DY_ENV_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_ENV_EXIT%
