@echo off
setlocal
cd /d "%~dp0"
title JARVIS - Installation
color 0A

echo ========================================
echo          JARVIS INSTALLER
echo ========================================
echo.

echo Checking Python...
where py >nul 2>nul
if %errorlevel% neq 0 (
  echo Python launcher was not found.
  echo Please install Python 3.11 or newer, then run this installer again.
  pause
  exit /b 1
)
py -3 -c "import sys; print(sys.version)" || goto :error

if not exist ".venv\Scripts\python.exe" (
  echo Creating JARVIS virtual environment...
  py -3 -m venv .venv || goto :error
)
call ".venv\Scripts\activate.bat"

echo Installing JARVIS dependencies...
python -m pip install --upgrade pip || goto :error
python -m pip install -r agent\requirements.txt || goto :error

where ollama >nul 2>nul
if %errorlevel% neq 0 (
  echo.
  echo Ollama was not found.
  echo Install Ollama from the official Ollama website, then run this installer again.
  echo.
  pause
  exit /b 1
)

echo Checking Ollama service...
ollama list >nul 2>nul
if %errorlevel% neq 0 (
  echo Starting Ollama temporarily for model setup...
  start "Ollama" ollama serve
  timeout /t 5 /nobreak >nul
)

echo Installing local AI model: llama3.2
ollama pull llama3.2 || goto :error

echo Installing Playwright Chromium...
python -m playwright install chromium || goto :error

if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul
if not exist "agent\data" mkdir "agent\data"
if not exist "agent\data\browser-profile" mkdir "agent\data\browser-profile"
if not exist "agent\data\browser-screenshots" mkdir "agent\data\browser-screenshots"
if not exist "agent\data\research" mkdir "agent\data\research"

if not exist "JARVIS_INSTALLED.flag" (
  >"JARVIS_INSTALLED.flag" echo JARVIS installation completed.
)

echo.
echo ========================================
echo JARVIS installation completed.
echo ========================================
echo.
echo You can now use START_JARVIS.bat.
echo It will run JARVIS silently in the background.
echo.
pause
exit /b 0

:error
echo.
echo JARVIS installation failed. Read the error above.
echo Fix the issue and run INSTALL_JARVIS.bat again.
pause
exit /b 1
