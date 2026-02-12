#!/bin/bash
# Quick start script for standalone backend

echo "=========================================="
echo "RedFlags Standalone Backend - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    echo "   Get your key from: https://aistudio.google.com/app/apikey"
    echo ""
    read -p "Press Enter after adding your API key..."
fi

# Check if requirements are installed
echo "Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "✓ Dependencies installed"
echo ""
echo "Starting backend server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
python app.py
