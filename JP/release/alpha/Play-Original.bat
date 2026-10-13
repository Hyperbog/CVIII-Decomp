@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Build-And-Play.ps1" -Edition Original
if errorlevel 1 pause
