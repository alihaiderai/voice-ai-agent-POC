@echo off
echo ========================================
echo Voice AI Platform - Starting Frontend
echo ========================================
echo.

REM Check if node_modules exists
if not exist node_modules (
    echo ERROR: Dependencies not installed!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop
echo.

call npm run dev
