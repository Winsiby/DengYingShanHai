@echo off
setlocal
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-FrameBeamDev.ps1" %*
set "DY_FRAMEBEAM_EXIT=%ERRORLEVEL%"
if not "%DY_FRAMEBEAM_EXIT%"=="0" pause
exit /b %DY_FRAMEBEAM_EXIT%
