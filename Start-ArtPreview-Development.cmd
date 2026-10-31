@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-ArtPreview-Development.ps1"
if errorlevel 1 pause
