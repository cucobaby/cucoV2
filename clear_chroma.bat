@echo off
REM Quick ChromaDB Clear Tool - Windows Batch Script

echo 🔧 ChromaDB Clear Tool
echo ===================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo Please ensure Python is installed and in your PATH
    pause
    exit /b 1
)

REM Run the clear tool with arguments passed from command line
python clear_chroma_tool.py %*

pause
