@echo off
REM HiTec University Library - Quick Start Script for Windows

echo.
echo 🚀 HiTec University Library Management System
echo =============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo ✓ Python found: 
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt >nul 2>&1
echo ✓ Dependencies installed

REM Create database directory
if not exist "database" mkdir database

echo.
echo ✨ Starting HiTec University Library...
echo =============================================
echo.
echo 📍 Access the application at: http://localhost:5000
echo 🔐 Admin Panel: http://localhost:5000/admin/login
echo 👤 Default Admin: username=admin, password=admin123
echo.
echo ⚠️  Change the default password after first login!
echo.
echo =============================================
echo.

REM Run the application
python app.py

pause
