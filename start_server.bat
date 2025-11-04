@echo off
echo ===================================
echo University Wallet System
echo Starting Flask Webhook Server
echo ===================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file with your IntaSend API keys
    echo You can copy .env.example and fill in your credentials
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting server...
echo Server will run on http://localhost:5000
echo Webhook endpoint: http://localhost:5000/webhook/intasend
echo.
echo To expose via ngrok, open a new terminal and run:
echo   ngrok http 5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py
