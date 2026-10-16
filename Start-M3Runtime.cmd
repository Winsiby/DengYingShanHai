@echo off
REM ===========================================================================
REM Start-M3Runtime.cmd
REM Third-act standalone packaged runtime launcher (stage 2B).
REM
REM Double-click in Explorer: launches the already packaged RuntimeCandidate
REM directly. No Editor, no Python, no .uproject, no fallback to older builds.
REM
REM Locates Scripts\ relative to its OWN location, so it does not depend on
REM the caller's current directory. Forwards all arguments to the PowerShell
REM entry and preserves its real exit code.
REM
REM This file is intentionally pure ASCII with no BOM.
REM ===========================================================================

setlocal

REM --- Resolve this CMD's own directory (works from any caller cwd) --------
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "PS_SCRIPT=%SCRIPT_DIR%\Scripts\Start-M3Runtime.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] PowerShell entry not found:
    echo         "%PS_SCRIPT%"
    echo [ERROR] The package launcher cannot start.
    pause
    exit /b 9
)

REM --- Invoke Windows PowerShell 5.1 and capture its real exit code -------
set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS_EXE%" (
    echo [ERROR] Windows PowerShell 5.1 not found at "%PS_EXE%".
    pause
    exit /b 9
)

"%PS_EXE%" -NoProfile -File "%PS_SCRIPT%" %*
set "PS_EXIT=%ERRORLEVEL%"

if not "%PS_EXIT%"=="0" (
    echo.
    echo [FAILED] Start-M3Runtime.ps1 returned exit code %PS_EXIT%.
    echo [INFO] %PS_EXIT% = 3 identity mismatch, 4 inner EXE missing or start failed,
    echo        5 run number invalid, session conflict, or session dir failed,
    echo        6 exited before READY, 7 READY not observed in the startup window,
    echo        8 game exit code unavailable, 9 fatal error observed in the new log.
    pause
)

REM Preserve the real PowerShell exit code; do not fold failures into 1.
exit /b %PS_EXIT%
