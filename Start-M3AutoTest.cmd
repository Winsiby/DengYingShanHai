@echo off
setlocal
title DengYingShanHai - Watch M3 Automatic Test
set "DY_M3_AUTO_SCRIPT=%~dp0Scripts\Start-M3AutoTest.ps1"
if not exist "%DY_M3_AUTO_SCRIPT%" (
    echo ERROR: automatic test launcher is missing.
    pause
    exit /b 1
)
powershell.exe -NoProfile -File "%DY_M3_AUTO_SCRIPT%" %*
if errorlevel 1 (
    echo Test failed or was canceled. Inspect the displayed log path.
    pause
    exit /b 1
)
endlocal
