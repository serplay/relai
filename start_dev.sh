#!/bin/bash

# Development startup script for RelAI MongoDB project

echo "🚀 Starting RelAI Development Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if MongoDB connection string is set
if [ -z "$MONGODB_CONNECTION_STRING" ]; then
    echo "⚠️  Warning: MONGODB_CONNECTION_STRING not set"
    echo "   Please set it in your environment or .env file"
fi

# Start the FastAPI server
echo "🌐 Starting FastAPI server..."
echo "   Server will be available at: http://localhost:8000"
echo "   API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py 