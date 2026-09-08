@echo off
setlocal
cd /d "%~dp0"

wscript.exe "%~dp0DISABLE_JARVIS_STARTUP.vbs"
echo.
echo JARVIS automatic startup disabled.
pause
exit /b 0
