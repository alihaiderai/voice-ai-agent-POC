@echo off
echo ========================================
echo Voice AI Platform - Starting Backend
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and add your OpenAI API key
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting FastAPI server...
echo Backend will be available at: http://localhost:8000
echo Press Ctrl+C to stop
echo.

python main.py
