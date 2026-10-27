@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-NEStudio.ps1" -Launch
exit /b %ERRORLEVEL%
