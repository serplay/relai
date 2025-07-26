#!/bin/bash

# Script to start the Temporal worker for RelAI

echo "Starting RelAI Temporal Worker..."
echo "Make sure Temporal server is running on localhost:7233"
echo "You can start Temporal server with: temporal server start-dev"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Using virtual environment..."
    PYTHON_CMD=".venv/bin/python"
elif [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="python"
else
    echo "No virtual environment found, using system Python3..."
    PYTHON_CMD="python3"
fi

# Install dependencies if needed
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Start the worker
echo "Starting Temporal worker..."
$PYTHON_CMD -m temporal_workflows.worker
