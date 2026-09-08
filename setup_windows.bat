@echo off
setlocal
cd /d "%~dp0"
call "%~dp0INSTALL_JARVIS.bat"
exit /b %errorlevel%
