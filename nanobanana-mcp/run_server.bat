@echo off
REM Run script for Nanobanana MCP Server (Windows)

echo Starting Nanobanana MCP Server...

REM Check if virtual environment exists
if not exist nanobanana_env (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call nanobanana_env\Scripts\activate.bat

REM Check if .env file exists
if not exist .env (
    echo .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Run the server
echo Running MCP server...
python src\server.py

pause