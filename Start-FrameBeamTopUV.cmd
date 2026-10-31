@echo off
setlocal
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-FrameBeamTopUV.ps1" %*
set "DY_FRAMEBEAMTOPUV_EXIT=%ERRORLEVEL%"
if not "%DY_FRAMEBEAMTOPUV_EXIT%"=="0" pause
exit /b %DY_FRAMEBEAMTOPUV_EXIT%
