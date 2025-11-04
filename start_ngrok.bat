@echo off
echo ============================================================
echo Starting ngrok tunnel for University Wallet System
echo ============================================================
echo.

REM Check if ngrok.exe exists
if not exist "ngrok.exe" (
    echo [ERROR] ngrok.exe not found!
    echo.
    echo Please extract ngrok.zip manually:
    echo 1. Right-click on ngrok.zip
    echo 2. Select "Extract All..."
    echo 3. Extract to this folder
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo Found ngrok.exe
echo.
echo Starting tunnel on port 5000...
echo.
echo NOTE: Your ngrok URL will be displayed below.
echo Copy the "Forwarding" URL and update it in IntaSend webhook settings.
echo.

ngrok.exe http 5000
