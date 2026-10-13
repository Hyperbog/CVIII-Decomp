@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Build-And-Play.ps1" -Edition Enhanced
if errorlevel 1 (
 echo Enhanced edition failed. Check the error above.
 pause
)
