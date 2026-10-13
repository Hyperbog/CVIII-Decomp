@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Build-And-Play.ps1" %*
if errorlevel 1 (
 echo.
 echo Private build or launch failed. Read the error above and check your CVIII-Alpha logs.
 pause
)
