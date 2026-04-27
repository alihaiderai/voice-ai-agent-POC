@echo off
echo ========================================
echo Voice AI Platform - Quick Start
echo ========================================
echo.
echo This script will setup and start both backend and frontend
echo.

REM Check if backend venv exists
if not exist "backend\venv" (
    echo Backend not setup yet. Running setup...
    cd backend
    call setup.bat
    if errorlevel 1 (
        echo Backend setup failed!
        cd ..
        pause
        exit /b 1
    )
    cd ..
)

REM Check if .env exists
if not exist "backend\.env" (
    echo.
    echo ========================================
    echo ERROR: Configuration Missing
    echo ========================================
    echo.
    echo Please create backend\.env file with your OpenAI API key
    echo.
    echo Steps:
    echo 1. Copy backend\.env.example to backend\.env
    echo 2. Edit backend\.env and add: OPENAI_API_KEY=sk-your-key-here
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo Frontend not setup yet. Running setup...
    cd frontend
    call setup.bat
    if errorlevel 1 (
        echo Frontend setup failed!
        cd ..
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo ========================================
echo Starting Services
echo ========================================
echo.

REM Start backend
echo Starting backend server...
cd backend
start "Voice AI Backend" cmd /k "venv\Scripts\activate && python main.py"
cd ..

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend
echo Starting frontend...
cd frontend
start "Voice AI Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo Voice AI Platform is Running!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two command windows have opened:
echo - Voice AI Backend (keep open)
echo - Voice AI Frontend (keep open)
echo.
echo Open your browser to: http://localhost:3000
echo.
echo Close both command windows to stop the services
echo.
pause
