#!/bin/bash

echo "==================================="
echo "University Wallet System"
echo "Starting Flask Webhook Server"
echo "==================================="
echo ""

# Get script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    
    echo "Please run setup.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with your IntaSend API keys"
    echo "You can copy .env.example and fill in your credentials"
    exit 1
fi

echo "Activating virtual environment..."
source venv/Scripts/activate

echo ""
echo "Starting server..."
echo "Server will run on http://localhost:5000
echo "Webhook endpoint: http://localhost:5000/webhook/intasend"
echo "To expose via ngrok, open a new terminal and run:"
echo "  ngrok http 5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
