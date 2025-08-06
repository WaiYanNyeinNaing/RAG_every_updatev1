#!/bin/bash

# RAG-Anything Gradio UI Startup Script
# This script ensures proper environment setup and runs the Gradio UI

echo "=========================================="
echo "Starting RAG-Anything Gradio UI"
echo "=========================================="

# Change to the script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv_rag_anything" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv_rag_anything
    source venv_rag_anything/bin/activate
    pip install -r requirements.txt
    pip install -e ..
else
    echo "✓ Virtual environment found"
    source venv_rag_anything/bin/activate
fi

# Check required environment variables
echo ""
echo "Checking environment variables..."
if [ -f ".env" ]; then
    echo "✓ .env file found"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found! Please create one."
    exit 1
fi

# Kill any existing Gradio UI process
echo ""
echo "Checking for existing processes..."
if pgrep -f "gradio_ui.py" > /dev/null; then
    echo "Found existing Gradio UI process. Killing it..."
    pkill -f "gradio_ui.py"
    sleep 2
fi

# Start the Gradio UI
echo ""
echo "Starting Gradio UI..."
echo "=========================================="
echo "Access the UI at: http://localhost:7860"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run with real-time output
python gradio_ui.py