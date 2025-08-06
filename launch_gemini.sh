#!/bin/bash

# Launch RAG-Anything with Google Gemini 2.0 Flash

echo "🚀 Starting RAG-Anything with Google Gemini 2.0 Flash..."
echo "💎 Fast, cost-effective alternative to GPT-4"
echo ""
echo "💰 Cost Advantages:"
echo "  - 400x cheaper than GPT-4"
echo "  - 2x faster processing"
echo "  - Free tier: 1M tokens/month"
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    if [ -f .env ]; then
        export $(cat .env | grep GEMINI_API_KEY | xargs)
    fi
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not found!"
    echo ""
    echo "📝 Quick Setup:"
    echo "1. Get free API key: https://aistudio.google.com/apikey"
    echo "2. Add to .env file: GEMINI_API_KEY=your-key"
    echo "3. Run this script again"
    exit 1
fi

echo "✅ Gemini API key found"
echo "📂 Access at: http://localhost:7861"
echo ""

# Activate virtual environment if it exists
if [ -d "venv_gemini" ]; then
    source venv_gemini/bin/activate
elif [ -d "venv_rag_anything" ]; then
    source venv_rag_anything/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install google-generativeai if not installed
python -c "import google.generativeai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing Google Gemini SDK..."
    pip install google-generativeai
fi

# Run the Gemini UI
python gradio_ui_gemini.py