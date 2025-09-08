#!/bin/bash

# CatalystAI Data Collector API Server Startup Script

echo "🚀 Starting CatalystAI Data Collector API Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if we're in the data-collector directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Please run this script from the data-collector directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r api_requirements.txt

# Install additional dependencies from main requirements
if [ -f "requirements.txt" ]; then
    echo "📥 Installing additional dependencies..."
    pip install -r requirements.txt
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation available at http://localhost:8000/docs"
echo "🔍 Health check available at http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
