@echo off
echo 🤖 CucoV2 Quality Testing Tool
echo ==============================

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Installing required packages...
    pip install requests pandas matplotlib seaborn
)

REM Run the testing tool
echo 🚀 Starting quality testing tool...
python test_query.py %*

pause
