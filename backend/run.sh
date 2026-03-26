#!/bin/bash
# Startup script for AI Support Ticket System Backend

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  AI Support Ticket System - Backend Setup & Startup      ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Check Python version
python_version=$(python --version 2>&1)
echo "Python Version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create database directory if it doesn't exist
if [ ! -d ".data" ]; then
    mkdir -p .data
fi

# Start server
echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting FastAPI server..."
echo ""
echo "📍 API will be available at: http://localhost:8000"
echo "📖 Documentation at: http://localhost:8000/docs"
echo "📊 Alternative docs at: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
