@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Stage Wings Dev
set "DY_STAGE_WINGS_SCRIPT=%~dp0Scripts\Start-StageWingsDev.ps1"
if not exist "%DY_STAGE_WINGS_SCRIPT%" (
    echo ERROR: Stage wings launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_STAGE_WINGS_SCRIPT%" %*
set "DY_STAGE_WINGS_EXIT=%ERRORLEVEL%"
if not "%DY_STAGE_WINGS_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_STAGE_WINGS_EXIT%
