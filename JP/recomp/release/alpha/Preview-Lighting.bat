@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Build-Lighting-Preview.ps1" %*
if errorlevel 1 (
 echo Lighting preview build failed. Inspect the error above.
 pause
)
