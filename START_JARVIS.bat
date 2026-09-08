@echo off
setlocal
cd /d "%~dp0"
title JARVIS
color 0A

echo ========================================
echo          JARVIS - UMAIR'S ASSISTANT
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup detected.
  echo Opening JARVIS installer...
  echo.
  call "%~dp0INSTALL_JARVIS.bat"
  if errorlevel 1 exit /b 1
)

if not exist "JARVIS_INSTALLED.flag" (
  echo Installation marker not found.
  echo Running the installer...
  echo.
  call "%~dp0INSTALL_JARVIS.bat"
  if errorlevel 1 exit /b 1
)

echo Starting JARVIS in background...
wscript.exe "%~dp0launch_jarvis.vbs"

echo JARVIS started.
echo Dashboard and voice assistant are running in the background.
timeout /t 2 /nobreak >nul
exit /b 0
