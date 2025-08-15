#!/bin/bash

# Transparency Tool for Product Launch - Server Startup Script

echo "============================================================"
echo "🚀 Transparency Tool for Product Launch (AI Agents)"
echo "============================================================"

# Kill any existing process on port 7861
echo "🔄 Checking for existing processes on port 7861..."
if lsof -Pi :7861 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Found existing process on port 7861"
    echo "🛑 Stopping existing process..."
    kill -9 $(lsof -t -i:7861) 2>/dev/null || true
    sleep 2
    echo "✅ Existing process stopped"
else
    echo "✅ Port 7861 is available"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your Azure credentials"
    echo "You can copy .env.sample to .env and update it"
    exit 1
fi

echo "✅ Found .env file"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 is installed: $(python3 --version)"

# Check for required Python packages
echo "📦 Checking required packages..."
python3 -c "import gradio" 2>/dev/null || {
    echo "Installing gradio..."
    pip install gradio
}

python3 -c "import openai" 2>/dev/null || {
    echo "Installing openai..."
    pip install openai
}

python3 -c "import PyPDF2" 2>/dev/null || {
    echo "Installing PyPDF2..."
    pip install PyPDF2
}

python3 -c "import dotenv" 2>/dev/null || {
    echo "Installing python-dotenv..."
    pip install python-dotenv
}

echo "✅ All required packages are installed"

# Check if RAG storage exists
if [ -d "rag_storage" ]; then
    echo "📚 Found existing RAG storage directory"
    doc_count=$(find rag_storage -name "*.json" | wc -l)
    echo "   Contains $doc_count JSON files"
else
    echo "📁 No existing RAG storage found (will be created when needed)"
fi

echo "============================================================"
echo "🌐 Starting server at http://127.0.0.1:7861"
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 transparency_tool_product_launch.py