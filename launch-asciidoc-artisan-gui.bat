@echo off
REM AsciiDoc Artisan GUI Launcher for Windows
REM Double-click this file to launch the application

echo === AsciiDoc Artisan GUI Launcher ===
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Launching AsciiDoc Artisan...
echo.

REM Launch the application
python src\main.py

echo.
echo Application closed.
pause
