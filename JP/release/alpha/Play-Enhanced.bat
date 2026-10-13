@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Alpha.ps1" -Edition Enhanced -UnlimitedSprites
if errorlevel 1 pause
