#!/bin/bash

# Launch RAG-Anything with detailed progress tracking

echo "🚀 Starting RAG-Anything with Detailed Progress Tracking..."
echo "📊 You will see real-time status for:"
echo "  - Document Parsing (MinerU stages)"
echo "  - Entity Extraction"
echo "  - Relation Extraction"
echo "  - Graph Building"
echo "  - Embedding Creation"
echo "  - Indexing"
echo ""
echo "📂 Access at: http://localhost:7860"
echo ""

# Activate virtual environment
source venv_rag_anything/bin/activate

# Run the enhanced UI
python gradio_ui_with_progress.py