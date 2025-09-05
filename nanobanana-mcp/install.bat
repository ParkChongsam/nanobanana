@echo off
REM Installation script for Nanobanana MCP Server (Windows)

echo Installing Nanobanana MCP Server...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv nanobanana_env

REM Activate virtual environment
echo Activating virtual environment...
call nanobanana_env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Copy environment file
echo Setting up environment...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
    echo Please edit .env file to configure your API keys
)

echo.
echo Installation completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file to configure your Google AI credentials
echo 2. Run the server with: python src\server.py
echo.
pause