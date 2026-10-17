@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Controls.ps1" %*
if errorlevel 1 (
 echo Controls were not changed. Review the error above.
 pause
)
