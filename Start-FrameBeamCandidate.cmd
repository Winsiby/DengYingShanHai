@echo off
setlocal
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-FrameBeamCandidate.ps1" %*
set "DY_FRAMEBEAMCANDIDATE_EXIT=%ERRORLEVEL%"
if not "%DY_FRAMEBEAMCANDIDATE_EXIT%"=="0" pause
exit /b %DY_FRAMEBEAMCANDIDATE_EXIT%
