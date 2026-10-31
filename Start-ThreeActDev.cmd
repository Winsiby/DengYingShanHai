@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Three Act Dev
set "DY_THREE_ACT_SCRIPT=%~dp0Scripts\Start-ThreeActDev.ps1"
if not exist "%DY_THREE_ACT_SCRIPT%" (
    echo ERROR: Three Act launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_THREE_ACT_SCRIPT%" %*
set "DY_THREE_ACT_EXIT=%ERRORLEVEL%"
if not "%DY_THREE_ACT_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_THREE_ACT_EXIT%
