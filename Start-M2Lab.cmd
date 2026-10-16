@echo off
REM 《灯影山海》M2 Dev slice launcher (double-click entry).
REM Opens LV_M2PuzzleLab only. It does NOT change the global default map,
REM and does NOT modify any .uasset, spawn orientation or interaction radius.
REM For focus diagnostics, use instead:
REM   powershell -ExecutionPolicy Bypass -File .\Scripts\Start-M2Lab.ps1 -Debug
REM NOTE: comments are intentionally ASCII so this file is safe under any
REM system code page (GBK/UTF-8) without mojibake.

setlocal
set "SCRIPT=%~dp0Scripts\Start-M2Lab.ps1"

if not exist "%SCRIPT%" (
    echo ERROR: cannot find %SCRIPT%
    pause
    exit /b 1
)

powershell -ExecutionPolicy Bypass -File "%SCRIPT%" %*
if errorlevel 1 (
    echo.
    echo Launch failed. Please send the error above to the supervisor.
    pause
    exit /b 1
)
endlocal
