@echo off
setlocal
cd /d "%~dp0"
title JARVIS - Stop

echo Stopping JARVIS background services...

powershell -NoProfile -ExecutionPolicy Bypass -Command "$names=@('python'); foreach($p in Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -match 'uvicorn api:app|voice.loop'}) { Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue }"

echo.
echo JARVIS services stopped.
echo You can start them again with START_JARVIS.bat.
timeout /t 2 /nobreak >nul
exit /b 0
