@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Start-FramePostAssetReview.ps1" %*
set "DY_POST_REVIEW_EXIT=%ERRORLEVEL%"
if not "%DY_POST_REVIEW_EXIT%"=="0" pause
exit /b %DY_POST_REVIEW_EXIT%
