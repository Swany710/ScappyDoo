@echo off
REM ScappyDoo Launcher Script for Windows
REM This script launches the ScappyDoo GUI application

echo ================================================
echo        🐕 ScappyDoo - Permit Scraper
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed!
    echo Please install Python 3 to use ScappyDoo.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo.
echo 🚀 Launching ScappyDoo...
echo The app will open in your default browser.
echo.
echo Press Ctrl+C to stop the application.
echo ================================================
echo.

REM Launch Streamlit
streamlit run app.py --server.headless=true

pause
