#!/bin/bash

echo "🔧 Clean Installation Script for RAG-Anything"
echo "=============================================="
echo "This script resolves ALL dependency conflicts"
echo ""

# Function to handle errors
handle_error() {
    echo "❌ Error occurred: $1"
    echo "Attempting to continue..."
}

# Create and activate virtual environment
echo "📦 Step 1: Creating clean virtual environment..."
rm -rf venv_clean 2>/dev/null
python3 -m venv venv_clean || handle_error "Failed to create venv"
source venv_clean/bin/activate || handle_error "Failed to activate venv"

# Upgrade pip and install build tools
echo ""
echo "📦 Step 2: Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel || handle_error "Failed to upgrade pip"

# Install packages in specific order to avoid conflicts
echo ""
echo "📦 Step 3: Installing core dependencies..."
pip install numpy==1.26.4 || handle_error "numpy"
pip install Pillow==10.4.0 || handle_error "Pillow"

echo ""
echo "📦 Step 4: Installing python-dotenv (older compatible version)..."
pip install python-dotenv==1.0.1 || handle_error "python-dotenv"

echo ""
echo "📦 Step 5: Installing Gradio..."
pip install gradio==4.44.0 || handle_error "gradio"

echo ""
echo "📦 Step 6: Installing Matplotlib..."
pip install matplotlib==3.7.2 || handle_error "matplotlib"

echo ""
echo "📦 Step 7: Installing PDF libraries (compatible versions)..."
pip install pypdf==3.17.4 || handle_error "pypdf"
pip install pdfminer.six==20221105 || handle_error "pdfminer"
pip install pypdfium2==4.30.0 || handle_error "pypdfium2"

echo ""
echo "📦 Step 8: Installing MinerU (attempting multiple methods)..."
# Method 1: Try standard installation
pip install mineru 2>/dev/null || {
    echo "⚠️  Standard MinerU installation failed, trying alternative..."
    
    # Method 2: Install without dependencies
    pip install --no-deps mineru 2>/dev/null || {
        echo "⚠️  No-deps installation failed, trying older version..."
        
        # Method 3: Try older version
        pip install mineru==2.0.0 2>/dev/null || {
            echo "⚠️  MinerU installation failed. Continuing without it..."
            echo "   You may need to install MinerU manually later"
        }
    }
}

# Install MinerU dependencies that don't conflict
echo ""
echo "📦 Step 9: Installing MinerU dependencies..."
pip install click loguru opencv-python-headless \
    boto3 modelscope huggingface_hub \
    fast-langdetect httpx json-repair \
    requests tqdm || handle_error "MinerU dependencies"

echo ""
echo "📦 Step 10: Installing LightRAG..."
# Check if LightRAG exists in parent directory
if [ -d "../lightrag" ]; then
    echo "Found LightRAG in parent directory, installing..."
    pip install -e .. || handle_error "LightRAG from parent"
else
    pip install lightrag-hku==1.4.5 || handle_error "LightRAG from PyPI"
fi

echo ""
echo "📦 Step 11: Installing LLM providers..."
pip install openai==1.50.0 || handle_error "openai"
pip install google-generativeai==0.8.5 || handle_error "google-generativeai"

echo ""
echo "📦 Step 12: Installing remaining packages..."
pip install -r requirements_minimal.txt || handle_error "requirements_minimal"

echo ""
echo "🧪 Testing installations..."
python3 << 'EOF'
import sys
print("Testing package imports...")
print("-" * 40)

packages_to_test = [
    ("PIL", "Pillow"),
    ("dotenv", "python-dotenv"),
    ("gradio", "Gradio"),
    ("matplotlib", "Matplotlib"),
    ("pypdf", "PyPDF"),
    ("lightrag", "LightRAG"),
    ("openai", "OpenAI"),
    ("google.generativeai", "Gemini")
]

failed = []
for module, name in packages_to_test:
    try:
        __import__(module)
        print(f"✅ {name}")
    except ImportError as e:
        print(f"❌ {name}: {e}")
        failed.append(name)

# Try MinerU separately as it might not be installed
try:
    import mineru
    print("✅ MinerU")
except ImportError:
    print("⚠️  MinerU: Not installed (optional)")

if not failed:
    print("\n✅ All required packages installed successfully!")
else:
    print(f"\n⚠️  Failed packages: {', '.join(failed)}")
    print("You may need to install these manually")
EOF

echo ""
echo "=============================================="
echo "📝 Installation Summary:"
echo ""
echo "✅ Virtual environment: venv_clean"
echo "✅ Core packages installed with compatible versions"
echo ""
echo "🚀 To use RAG-Anything:"
echo ""
echo "1. Activate environment:"
echo "   source venv_clean/bin/activate"
echo ""
echo "2. Configure API keys:"
echo "   cp .env.sample .env  # For Azure"
echo "   OR"
echo "   cp .env.gemini.sample .env  # For Gemini"
echo ""
echo "3. Run the application:"
echo "   python gradio_ui.py  # Azure/GPT-4"
echo "   python gradio_ui_gemini.py  # Gemini"
echo ""

# Create activation helper
cat > activate.sh << 'ACTIVATION'
#!/bin/bash
source venv_clean/bin/activate
echo "✅ Virtual environment activated"
echo "Run: python gradio_ui_gemini.py (for Gemini)"
echo "Or:  python gradio_ui.py (for Azure)"
ACTIVATION
chmod +x activate.sh

echo "💡 Quick activate: ./activate.sh"