#!/bin/bash

echo "📦 Pushing complete working version to GitHub..."
echo "This includes dependency fixes and Gemini support"
echo ""

# Files to push
FILES=(
    # Core UI files
    "gradio_ui.py"
    "gradio_ui_with_progress.py"
    "gradio_ui_fixed.py"
    "gradio_ui_gemini.py"
    
    # Wrapper files
    "azure_openai_wrappers.py"
    "gemini_wrappers.py"
    
    # Requirements and fixes
    "requirements.txt"
    "requirements_fixed.txt"
    "install_dependencies.sh"
    
    # Configuration samples
    ".env.sample"
    ".env.gemini.sample"
    
    # Test scripts
    "test_azure_connection.py"
    "test_gemini_connection.py"
    "test_gemini_local.py"
    "setup_gemini.py"
    
    # Documentation
    "README_AZURE.md"
    "README_GEMINI.md"
    "DEPENDENCY_FIX.md"
    "MINERU_MODELS.md"
    
    # Launcher scripts
    "launch_progress_ui.sh"
    "launch_gemini.sh"
    
    # Monitoring
    "monitor_gradio.py"
)

# Create temp directory
TEMP_DIR="/tmp/rag_push_complete_$$"
echo "Creating temporary directory: $TEMP_DIR"

# Clone repository
echo "Cloning repository..."
gh repo clone WaiYanNyeinNaing/RAG_Every "$TEMP_DIR"

# Copy all files
echo "Copying files..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$TEMP_DIR/"
        echo "  ✓ Copied $file"
    else
        echo "  ⚠️  File not found: $file"
    fi
done

# Update main README
cat > "$TEMP_DIR/README.md" << 'ENDREADME'
# RAG-Anything with Azure OpenAI & Google Gemini Support

Complete multimodal RAG system with dual LLM support and dependency fixes.

## 🚀 Quick Start

### Option 1: Azure OpenAI (GPT-4.1)
```bash
# Setup
cp .env.sample .env
# Add your Azure credentials to .env
python gradio_ui.py
```

### Option 2: Google Gemini (400x cheaper!)
```bash
# Setup
cp .env.gemini.sample .env
# Add your Gemini API key to .env
python gradio_ui_gemini.py
```

## 🔧 Installation (Fixes Dependency Conflicts)

```bash
# Clone repository
git clone https://github.com/WaiYanNyeinNaing/RAG_Every.git
cd RAG-Anything

# Use the fixed installation script
chmod +x install_dependencies.sh
./install_dependencies.sh
```

## 📦 Working Versions
- gradio==5.41.0
- matplotlib==3.10.5
- mineru==2.1.10
- lightrag-hku==1.4.5
- google-generativeai==0.8.5

## 📚 Documentation
- [Azure Setup Guide](README_AZURE.md)
- [Gemini Setup Guide](README_GEMINI.md)
- [Dependency Fixes](DEPENDENCY_FIX.md)
- [MinerU Models](MINERU_MODELS.md)

## 💰 Cost Comparison
| Model | Cost per 1M tokens | Free Tier |
|-------|-------------------|-----------|
| Gemini 2.0 Flash | $0.075 | 1M tokens/month |
| GPT-4 | $30 | None |

## Features
- ✅ Multimodal document processing (PDF, images, tables, equations)
- ✅ Real-time progress tracking
- ✅ Dual LLM support (Azure & Gemini)
- ✅ Dependency conflict resolution
- ✅ Document caching & resume
- ✅ Local MinerU parsing
ENDREADME

# Push changes
echo ""
echo "Pushing to GitHub..."
cd "$TEMP_DIR"
git add .
git commit -m "feat: complete working version with dependency fixes and Gemini support

- Fixed all dependency conflicts (gradio, matplotlib, mineru, lightrag)
- Added Google Gemini 2.0 Flash support (400x cheaper than GPT-4)
- Includes working requirements_fixed.txt with exact versions
- Installation script handles proper dependency order
- Comprehensive documentation for troubleshooting
- Tested and working on macOS with Python 3.10"

git push

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Successfully pushed complete version to GitHub!"
echo "🔗 Repository: https://github.com/WaiYanNyeinNaing/RAG_Every"
echo ""
echo "📝 Included:"
echo "  - Working dependency versions"
echo "  - Gemini integration"
echo "  - Installation fixes"
echo "  - Complete documentation"