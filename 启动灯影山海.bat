@echo off
rem DengYingShanHai - public formal entry (Shipping Run167)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-FormalShipping.ps1"
if errorlevel 1 pause
