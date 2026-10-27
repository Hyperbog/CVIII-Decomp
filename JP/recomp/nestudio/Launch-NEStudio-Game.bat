@echo off
setlocal
cd /d "%~dp0"
rem The game process inherits CVIII_NESTUDIO_SESSION from NEStudio's cmd.exe.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Launch-NEStudio-Game.ps1"
exit /b %ERRORLEVEL%
