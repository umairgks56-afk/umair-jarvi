@echo off
cd /d "%~dp0"
title JARVIS - Setup & Launcher
color 0A
echo.
echo ========================================
echo          JARVIS LAUNCHER
 echo ========================================
echo.
echo This window will stay open so you can see any error.
echo.
call "%~dp0setup_windows.bat"
echo.
echo ========================================
echo Launcher finished. Do not close this window
 echo if JARVIS windows are still starting.
echo ========================================
echo.
cmd /k
