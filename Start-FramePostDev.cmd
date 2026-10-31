@echo off
setlocal
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-FramePostDev.ps1" %*
set "DY_FRAMEPOST_EXIT=%ERRORLEVEL%"
if not "%DY_FRAMEPOST_EXIT%"=="0" pause
exit /b %DY_FRAMEPOST_EXIT%
