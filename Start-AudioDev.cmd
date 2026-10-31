@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Audio Dev
set "DY_AUDIO_SCRIPT=%~dp0Scripts\Start-AudioDev.ps1"
if not exist "%DY_AUDIO_SCRIPT%" (
    echo ERROR: Audio launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_AUDIO_SCRIPT%" %*
set "DY_AUDIO_EXIT=%ERRORLEVEL%"
if not "%DY_AUDIO_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_AUDIO_EXIT%
