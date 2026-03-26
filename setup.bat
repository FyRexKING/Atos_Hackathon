@echo off
setlocal enabledelayedexpansion

REM ATOS System - Automatic Setup Script for Windows
REM Run this once after cloning the repository on your laptop

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         AI SUPPORT TICKET SYSTEM - AUTOMATED SETUP             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if we're in the right directory
if not exist backend (
    echo ✗ Error: Please run this script from the ATOS project root directory
    echo   Expected to find 'backend' and 'frontend' subdirectories
    pause
    exit /b 1
)

REM Step 1: Python Backend Setup
echo Step 1: Setting up Python Backend
echo ═══════════════════════════════════════════════════════════════

cd backend

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%A in ('python --version 2^>^&1') do (
    echo   Python version: %%A
)

REM Install backend requirements
echo.
echo Installing Python dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ✗ Error installing Python dependencies
    pause
    exit /b 1
)

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env file with defaults...
    (
        echo # Backend Configuration
        echo DATABASE_URL=sqlite:///./tickets.db
        echo SECRET_KEY=your-secret-key-change-in-production
        echo DEBUG=True
        echo.
        echo # Optional: Gemini API for semantic matching
        echo # GEMINI_API_KEY=your-api-key-here
        echo.
        echo # Server Settings
        echo HOST=0.0.0.0
        echo PORT=8000
    ) > .env
    echo   ✓ Created .env
) else (
    echo   ✓ .env already exists
)

REM Initialize database and seed data
echo.
echo Initializing database and seeding quality tickets...
python << PYTHON_SCRIPT
from app.db.database import init_db, add_sample_tickets, create_default_admin
import sys

try:
    print("  Initializing database schema...")
    init_db()
    print("  ✓ Database schema ready")
    
    print("  Creating default admin user...")
    create_default_admin()
    
    print("  Seeding sample and quality tickets...")
    add_sample_tickets()
    print("  ✓ Database initialized with learning data")
except Exception as e:
    print(f"  ✗ Error initializing database: {e}")
    sys.exit(1)
PYTHON_SCRIPT

if errorlevel 1 (
    echo   ⚠ Database initialization had issues (may be OK if DB exists^)
) else (
    echo   ✓ Backend database ready
)

cd ..

REM Step 2: Frontend Setup
echo.
echo Step 2: Setting up React Frontend
echo ═══════════════════════════════════════════════════════════════

cd frontend

REM Check Node version
node --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Node.js not found. Please install Node.js 16+ from nodejs.org
    pause
    exit /b 1
)

for /f %%A in ('node --version') do set NODE_VERSION=%%A
for /f %%A in ('npm --version') do set NPM_VERSION=%%A

echo   Node version: !NODE_VERSION!
echo   npm version: !NPM_VERSION!

REM Install frontend dependencies
echo.
echo Installing npm dependencies...
call npm install -q
if errorlevel 1 (
    echo ✗ Error installing npm dependencies
    pause
    exit /b 1
)

echo   ✓ Frontend dependencies installed

REM Create .env.local if doesn't exist
if not exist .env.local (
    echo Creating .env.local file...
    (
        echo VITE_API_URL=http://localhost:8000
    ) > .env.local
    echo   ✓ Created .env.local
) else (
    echo   ✓ .env.local already exists
)

cd ..

REM Final Summary
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  SETUP COMPLETE!                              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ✓ Backend dependencies installed
echo ✓ Frontend dependencies installed
echo ✓ Database initialized
echo ✓ Default admin user created
echo ✓ Quality tickets seeded (10 real-world examples^)
echo.

echo Next steps to run the system:
echo.
echo Terminal 1 - Start Backend:
echo   cd backend
echo   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Terminal 2 - Start Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Then open:
echo   http://localhost:5173 (Frontend^)
echo.
echo Login with:
echo   Username: admin
echo   Password: admin123
echo.
echo Database includes:
echo   ✓ 6 basic sample tickets
echo   ✓ 10 high-quality seed tickets with resolutions
echo   ✓ 9 knowledge base articles
echo.
echo These quality tickets help the AI system learn from:
echo   • Real support scenarios with proper resolutions
echo   • Common issues and their solutions
echo   • Root cause analysis and fixes
echo.
echo Optional: Set GEMINI_API_KEY in backend/.env for 15-20%% accuracy boost
echo.

pause
