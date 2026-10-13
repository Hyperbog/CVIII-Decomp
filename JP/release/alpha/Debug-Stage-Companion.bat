@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 with Tkinter is required.
  pause
  exit /b 1
)
python "%~dp0jp_password_debug_menu_0593.py"
if errorlevel 1 pause
