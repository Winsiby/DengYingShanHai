@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Readability Dev
set "DY_READABILITY_SCRIPT=%~dp0Scripts\Start-ReadabilityDev.ps1"
if not exist "%DY_READABILITY_SCRIPT%" (
    echo ERROR: Readability launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_READABILITY_SCRIPT%" %*
set "DY_READABILITY_EXIT=%ERRORLEVEL%"
if not "%DY_READABILITY_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_READABILITY_EXIT%
