@echo off
setlocal
set "PSModulePath=%SystemRoot%\System32\WindowsPowerShell\v1.0\Modules"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -File "%~dp0Scripts\Start-ReleaseEntry.ps1" -Configuration Development
set "DY_RELEASE_ENTRY_EXIT=%ERRORLEVEL%"
if not "%DY_RELEASE_ENTRY_EXIT%"=="0" pause
exit /b %DY_RELEASE_ENTRY_EXIT%
