@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-Alpha.ps1" -Edition Original
if errorlevel 1 pause
