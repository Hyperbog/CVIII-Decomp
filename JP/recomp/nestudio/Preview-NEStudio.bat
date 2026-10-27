@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Preview-NEStudio.ps1" %*
exit /b %ERRORLEVEL%
