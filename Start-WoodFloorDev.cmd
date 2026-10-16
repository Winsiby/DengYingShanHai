@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Wood Floor Dev
set "DY_WOOD_SCRIPT=%~dp0Scripts\Start-WoodFloorDev.ps1"
if not exist "%DY_WOOD_SCRIPT%" (
    echo ERROR: Wood floor launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_WOOD_SCRIPT%" %*
set "DY_WOOD_EXIT=%ERRORLEVEL%"
if not "%DY_WOOD_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_WOOD_EXIT%
