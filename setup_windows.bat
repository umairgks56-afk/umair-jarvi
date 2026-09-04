@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo        JARVIS Windows Setup
echo ========================================
echo.
where py >nul 2>nul
if %errorlevel% neq 0 (
  echo Python launcher was not found.
  echo Please install Python 3.11 or newer, then run this file again.
  pause
  exit /b 1
)
py -3 -c "import sys; print(sys.version)" || goto :error
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -3 -m venv .venv || goto :error
)
call ".venv\Scripts\activate.bat"
echo Installing JARVIS dependencies...
python -m pip install --upgrade pip || goto :error
python -m pip install -r agent\requirements.txt || goto :error
where ollama >nul 2>nul
if %errorlevel% neq 0 (
  echo.
  echo Ollama was not found. Install Ollama from the official Ollama website,
  echo then run setup_windows.bat again.
  echo.
  pause
  exit /b 1
)
echo Checking Ollama...
ollama list >nul 2>nul
if %errorlevel% neq 0 (
  echo Starting Ollama...
  start "Ollama" ollama serve
  timeout /t 5 /nobreak >nul
)
echo Pulling local AI model: llama3.2
ollama pull llama3.2 || goto :error
echo Installing Playwright Chromium...
python -m playwright install chromium || goto :error
if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul
if not exist "agent\data" mkdir "agent\data"
echo.
echo JARVIS setup completed successfully.
echo Starting JARVIS API and voice assistant...
start "JARVIS API" cmd /k "cd /d %~dp0agent && ..\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8765"
timeout /t 3 /nobreak >nul
start "JARVIS Voice" cmd /k "cd /d %~dp0agent && ..\.venv\Scripts\python.exe voice\loop.py"
echo.
echo JARVIS is starting. Keep the two JARVIS windows open.
pause
exit /b 0
:error
echo.
echo Setup failed. Read the message above and run this file again after fixing it.
pause
exit /b 1
