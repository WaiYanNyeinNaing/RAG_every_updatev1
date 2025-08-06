#!/bin/bash

echo "🔧 RAG-Anything Installation with Pillow Conflict Resolution"
echo "============================================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "📌 Python version: $python_version"

# Create virtual environment
if [ ! -d "venv_rag" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv_rag
fi

# Activate virtual environment
source venv_rag/bin/activate

echo ""
echo "🧹 Cleaning conflicting packages..."
pip uninstall -y pillow matplotlib gradio mineru 2>/dev/null

echo ""
echo "📥 Step 1: Installing Pillow (pinned version)..."
pip install Pillow==10.4.0

echo ""
echo "📥 Step 2: Installing numpy..."
pip install numpy>=2.0.0

echo ""
echo "📥 Step 3: Installing Gradio..."
pip install gradio==4.44.0 --no-deps
pip install gradio-client==1.3.0
# Install gradio dependencies without upgrading Pillow
pip install fastapi uvicorn httpx pydantic typing-extensions \
    orjson python-multipart ffmpy aiofiles jinja2 \
    semantic-version pyyaml importlib-resources --no-deps

echo ""
echo "📥 Step 4: Installing matplotlib..."
pip install matplotlib==3.7.2 --no-deps
# Install matplotlib dependencies
pip install cycler pyparsing python-dateutil kiwisolver \
    contourpy fonttools packaging --no-deps

echo ""
echo "📥 Step 5: Installing MinerU (special handling)..."
# Try to install mineru without strict Pillow requirement
pip install mineru --no-deps 2>/dev/null || {
    echo "⚠️ Standard MinerU installation failed, trying alternative..."
    # Install MinerU dependencies manually
    pip install click loguru pdfminer.six pypdf reportlab \
        opencv-python-headless pdfplumber \
        boto3 modelscope huggingface-hub \
        fast-langdetect httpx json-repair \
        pdftext pypdfium2 requests --no-deps
    
    # Try again
    pip install mineru --no-deps
}

echo ""
echo "📥 Step 6: Installing LightRAG..."
if [ -d "../lightrag" ]; then
    pip install -e .. --no-deps
else
    pip install lightrag-hku>=1.4.5 --no-deps
fi

echo ""
echo "📥 Step 7: Installing remaining dependencies..."
# Install other essential packages
pip install python-dotenv openai azure-identity azure-core \
    google-generativeai aiohttp tenacity tiktoken \
    networkx pydantic nest_asyncio pandas openpyxl \
    pypdf python-docx markdown tqdm \
    protobuf grpcio huggingface_hub

echo ""
echo "🧪 Testing installations..."
echo "----------------------------"

# Test imports
python3 -c "
import sys
errors = []

try:
    import PIL
    print(f'✅ Pillow {PIL.__version__}')
except ImportError as e:
    errors.append(f'❌ Pillow: {e}')

try:
    import gradio
    print(f'✅ Gradio {gradio.__version__}')
except ImportError as e:
    errors.append(f'❌ Gradio: {e}')

try:
    import matplotlib
    print(f'✅ Matplotlib {matplotlib.__version__}')
except ImportError as e:
    errors.append(f'❌ Matplotlib: {e}')

try:
    import mineru
    print('✅ MinerU installed')
except ImportError:
    print('⚠️ MinerU not found (may need manual installation)')

try:
    import lightrag
    print('✅ LightRAG installed')
except ImportError as e:
    errors.append(f'❌ LightRAG: {e}')

if errors:
    print('\n⚠️ Some packages failed:')
    for error in errors:
        print(error)
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Copy .env.sample or .env.gemini.sample to .env"
    echo "2. Add your API keys"
    echo "3. Run: python gradio_ui.py (Azure) or python gradio_ui_gemini.py (Gemini)"
else
    echo ""
    echo "⚠️ Some issues detected. Manual fixes may be needed."
    echo ""
    echo "Try these commands:"
    echo "  pip install --upgrade pip setuptools wheel"
    echo "  pip install Pillow==10.4.0 --force-reinstall"
    echo "  pip install mineru --no-binary :all:"
fi