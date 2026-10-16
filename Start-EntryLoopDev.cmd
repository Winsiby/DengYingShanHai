@echo off
setlocal
chcp 65001 >nul
title DengYingShanHai - Entry Loop Dev
set "DY_ENTRY_LOOP_SCRIPT=%~dp0Scripts\Start-EntryLoopDev.ps1"
if not exist "%DY_ENTRY_LOOP_SCRIPT%" (
    echo ERROR: Entry Loop launcher is missing. Nothing was started.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DY_ENTRY_LOOP_SCRIPT%" %*
set "DY_ENTRY_LOOP_EXIT=%ERRORLEVEL%"
if not "%DY_ENTRY_LOOP_EXIT%"=="0" (
    echo The game was not started or exited with an error. Read the message above.
    pause
)
endlocal & exit /b %DY_ENTRY_LOOP_EXIT%
