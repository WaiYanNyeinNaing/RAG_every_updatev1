#!/bin/bash

echo "🔧 Installing RAG-Anything with fixed dependencies..."
echo "This script ensures all packages work together without conflicts"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv_rag_anything" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv_rag_anything
fi

# Activate virtual environment
source venv_rag_anything/bin/activate

echo "🧹 Cleaning any conflicting packages..."
# Uninstall potentially conflicting packages first
pip uninstall -y matplotlib gradio lightrag-hku mineru 2>/dev/null

echo "📥 Installing core dependencies..."
# Install in specific order to avoid conflicts

# 1. Install numpy first (many packages depend on it)
pip install numpy>=2.0.0

# 2. Install matplotlib with specific version
pip install matplotlib==3.10.5

# 3. Install gradio with specific version
pip install gradio==5.41.0

# 4. Install MinerU
pip install mineru[core]==2.1.10

# 5. Install LightRAG
# Check if parent directory has LightRAG
if [ -d "../lightrag" ]; then
    echo "📦 Installing LightRAG from parent directory..."
    pip install -e ..
else
    echo "📦 Installing LightRAG from PyPI..."
    pip install lightrag-hku==1.4.5
fi

# 6. Install remaining dependencies
pip install -r requirements_fixed.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "🧪 Testing installations..."
python -c "import gradio; print(f'✅ Gradio {gradio.__version__}')"
python -c "import matplotlib; print(f'✅ Matplotlib {matplotlib.__version__}')"
python -c "import mineru; print('✅ MinerU installed')"
python -c "import lightrag; print('✅ LightRAG installed')"

echo ""
echo "🚀 You can now run:"
echo "   python gradio_ui.py          # For Azure/GPT-4"
echo "   python gradio_ui_gemini.py   # For Google Gemini"
echo ""