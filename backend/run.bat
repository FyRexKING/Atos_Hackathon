@echo off
REM Startup script for AI Support Ticket System Backend (Windows)

echo.
echo ================================================================
echo   AI Support Ticket System - Backend Setup and Startup
echo ================================================================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [1/3] Installing dependencies...
pip install -r requirements.txt

REM Create database directory
if not exist ".data" mkdir .data

REM Start server
echo.
echo [2/3] Setup complete!
echo.
echo [3/3] Starting FastAPI server...
echo.
echo.
echo ================================================================
echo   API: http://localhost:8000
echo   Docs: http://localhost:8000/docs (Swagger UI)
echo   Alternative Docs: http://localhost:8000/redoc
echo ================================================================
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
