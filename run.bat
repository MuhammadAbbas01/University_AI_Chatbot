@echo off
title University of Malakand AI Assistant
color 0A

echo ================================================================================
echo    University of Malakand AI Assistant
echo    Starting up...
echo ================================================================================
echo.

REM Switch to the correct drive AND directory
cd /d D:\Desktop\university-ai-assistant

REM Set UTF-8 so emoji in app.py don't crash the terminal
set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

REM Check Ollama is running
echo [1/3] Checking Ollama...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] Ollama is not running. Starting it now...
    start /B D:\Ollama\ollama.exe serve
    timeout /t 5 /nobreak >nul
    echo [+] Ollama started.
) else (
    echo [+] Ollama is already running.
)
echo.

REM Check Python venv
echo [2/3] Checking Python environment...
if not exist ".venv\Scripts\python.exe" (
    echo [!] ERROR: .venv not found at D:\Desktop\university-ai-assistant\.venv
    pause
    exit /b 1
)
echo [+] Python venv found.
echo.

REM Launch Flask app
echo [3/3] Launching Flask app...
echo.
echo    Access at: http://localhost:5000
echo    Admin at:  http://localhost:5000/admin
echo    Press Ctrl+C to stop.
echo ================================================================================
echo.

.venv\Scripts\python.exe -X utf8 app.py

echo.
echo [App stopped]
pause
