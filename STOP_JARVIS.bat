@echo off
setlocal
cd /d "%~dp0"
title JARVIS - Stop
color 0C

echo Stopping JARVIS background services...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$procs=Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -and (($_.CommandLine -match 'uvicorn api:app') -or ($_.CommandLine -match 'voice\.loop')) -and ($_.CommandLine -match 'agent') }; $procs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

echo.
echo JARVIS services stopped.
echo You can start them again with START_JARVIS.bat.
timeout /t 2 /nobreak >nul
exit /b 0
