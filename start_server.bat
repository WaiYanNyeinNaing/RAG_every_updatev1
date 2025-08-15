@echo off
REM Transparency Tool for Product Launch - Windows Startup Script

echo ============================================================
echo Transparency Tool for Product Launch (AI Agents)
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo Python is installed
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    if exist ".env.sample" (
        echo Creating .env from .env.sample...
        copy .env.sample .env
        echo Please edit .env with your Azure credentials
    ) else (
        echo Please create .env file with your Azure credentials
    )
    pause
    exit /b 1
)

echo Found .env file
echo.

REM Kill any existing process on port 7861
echo Checking for existing processes on port 7861...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :7861 ^| findstr LISTENING') do (
    echo Stopping existing process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo Port 7861 is ready
echo.

REM Check for RAG storage
if exist "rag_storage" (
    echo Found existing RAG storage directory
) else (
    echo No existing RAG storage found
)

echo.
echo ============================================================
echo Starting server at http://127.0.0.1:7861
echo ============================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python transparency_tool_product_launch.py

pause