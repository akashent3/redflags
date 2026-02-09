#!/bin/bash
# Quick start script for standalone frontend

echo "==========================================="
echo "RedFlags Standalone Frontend - Quick Start"
echo "==========================================="
echo ""

# Check if backend is running
echo "Checking if backend is running..."
curl -s http://localhost:8000/api/health > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Backend not running!"
    echo "   Start backend first: cd ../backend && ./start.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ Backend is running"
fi

echo ""
echo "Starting frontend server on http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""
echo "Open in browser: http://localhost:8080"
echo ""

# Start the server
python3 -m http.server 8080
