@echo off
REM Double-click in Explorer. Player mode by default; never auto-adjust answers.
setlocal
title DengYingShanHai - M3 Dev Candidate
set "DY_P03_CANDIDATE_SCRIPT=%~dp0Scripts\Start-M3Candidate.ps1"
if not exist "%DY_P03_CANDIDATE_SCRIPT%" (
    echo ERROR: missing candidate launcher.
    pause
    exit /b 1
)
echo Starting the isolated M3 Dev play session. Please wait for READY.
echo Keep this console for launch status. UE will open visibly in Play mode.
powershell.exe -NoProfile -File "%DY_P03_CANDIDATE_SCRIPT%" %*
if errorlevel 1 (
    echo Candidate session failed. Send the error and log path to Codex.
    echo Nothing was killed or rolled back. Close the isolated UE without saving.
    pause
    exit /b 1
)
endlocal
