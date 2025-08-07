@echo off
echo Simple RAG System Setup for Windows
echo ===================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Checking if Ollama is installed...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed
    echo Please install Ollama from https://ollama.ai
    echo After installation, run this script again
    pause
    exit /b 1
)

echo Starting Ollama service...
start /B ollama serve

echo Waiting for Ollama to start...
timeout /t 5 /nobreak >nul

echo Pulling Llama2 model...
ollama pull llama2
if errorlevel 1 (
    echo Failed to pull Llama2 model
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo You can now run: python rag_system.py
echo.
pause 