@echo off
echo Setting up Python environment and running the app...

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist .env (
    echo Creating .env file...
    echo GEMINI_API_KEY=your_api_key_here > .env
    echo Please update the GEMINI_API_KEY in the .env file with your actual API key.
    pause
    exit /b 1
)

:: Start the FastAPI server
echo Starting the FastAPI server...
python AgenticMCPUse.py

:: Keep the window open if there's an error
if errorlevel 1 (
    echo Server failed to start.
    pause
) 