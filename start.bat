@echo off
REM ============================================================================
REM START SCRIPT - University of Malakand AI Assistant
REM Just double-click this file to start everything!
REM ============================================================================

color 0A
title University of Malakand AI Assistant

echo ================================================================================
echo.
echo            UNIVERSITY OF MALAKAND AI ASSISTANT
echo.
echo ================================================================================
echo.

REM Check if Ollama is installed
echo [1/4] Checking Ollama installation...
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Ollama not found!
    echo.
    echo Please install Ollama from: https://ollama.com/download
    echo.
    pause
    exit /b 1
)
echo Ollama found.
echo.

REM Check which model is set (default: mistral, for CPU)
echo [2/4] Checking Ollama model (set OLLAMA_MODEL env var to override, default: mistral)...
if "%OLLAMA_MODEL%"=="" set OLLAMA_MODEL=mistral
ollama list | findstr /I "%OLLAMA_MODEL%" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Model %OLLAMA_MODEL% not found. Downloading (this can take a few minutes)...
    ollama pull %OLLAMA_MODEL%
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download model!
        pause
        exit /b 1
    )
)
echo Model %OLLAMA_MODEL% ready.
echo.

REM Start Ollama server
echo [3/4] Starting Ollama server...
start /B ollama serve
timeout /t 5 /nobreak >nul
echo Ollama server started.
echo.

REM Check Python
echo [4/4] Starting AI Assistant...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found.
echo.
echo ================================================================================
echo.
echo LAUNCHING AI ASSISTANT...
echo.
echo    Please wait 30-60 seconds for initialization...
echo.
echo ================================================================================
echo.

REM Start the Flask app
python app.py

REM If we get here, app stopped
echo.
echo ================================================================================
echo    Application stopped.
echo ================================================================================
echo.
pause
