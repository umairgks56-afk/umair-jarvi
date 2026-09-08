@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo JARVIS is not installed. Run INSTALL_JARVIS.bat first.
  pause
  exit /b 1
)

wscript.exe "%~dp0ENABLE_JARVIS_STARTUP.vbs"
echo.
echo JARVIS will now start automatically when you sign in to Windows.
pause
exit /b 0
