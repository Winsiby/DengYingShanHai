@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Alignment Dev
set "DY_ALIGNMENT_SCRIPT=%~dp0Scripts\Start-AlignmentDev-Run1.ps1"
if not exist "%DY_ALIGNMENT_SCRIPT%" (
    echo ERROR: Alignment launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_ALIGNMENT_SCRIPT%" %*
set "DY_ALIGNMENT_EXIT=%ERRORLEVEL%"
if not "%DY_ALIGNMENT_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_ALIGNMENT_EXIT%
