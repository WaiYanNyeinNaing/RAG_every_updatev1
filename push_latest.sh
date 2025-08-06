#!/bin/bash

echo "📦 Pushing latest changes to GitHub..."

# Files to push
FILES=(
    "gradio_ui_with_progress.py"
    "gradio_ui_fixed.py"
    "launch_progress_ui.sh"
    "MINERU_MODELS.md"
    ".env.sample"
    "requirements.txt"
    "azure_openai_wrappers.py"
    "test_azure_connection.py"
    "monitor_gradio.py"
)

# Create temp directory
TEMP_DIR="/tmp/rag_every_push_$$"
echo "Creating temporary directory: $TEMP_DIR"

# Clone the repository
echo "Cloning repository..."
gh repo clone WaiYanNyeinNaing/RAG_Every "$TEMP_DIR"

# Copy files
echo "Copying files..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$TEMP_DIR/"
        echo "  ✓ Copied $file"
    else
        echo "  ⚠️  File not found: $file"
    fi
done

# Create README_AZURE.md
cat > "$TEMP_DIR/README_AZURE.md" << 'ENDREADME'
# RAG-Anything with Azure OpenAI Integration

## 🚀 Latest Updates

### Progress Tracking UI
- **NEW**: Real-time progress tracking with `gradio_ui_with_progress.py`
- Shows detailed processing stages:
  - Document Parsing (MinerU)
  - Entity Extraction (Azure GPT-4)
  - Relation Extraction (Azure GPT-4)
  - Graph Building
  - Embedding Creation (Azure text-embedding-3-large)
  - Indexing

### Quick Start
```bash
# Enhanced UI with progress tracking
python gradio_ui_with_progress.py

# OR use the launcher
./launch_progress_ui.sh
```

### Key Features
- Azure OpenAI integration (GPT-4 + text-embedding-3-large)
- Local MinerU parsing (YOLOv8, TableTransformer, LaTeX-OCR, PaddleOCR)
- Automatic rate limit handling
- Document caching and resume capability
- Real-time status updates

### Installation
1. Clone this repository
2. Copy `.env.sample` to `.env` and add your Azure credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python gradio_ui_with_progress.py`

See full documentation in the main README.
ENDREADME

# Push changes
echo "Pushing to GitHub..."
cd "$TEMP_DIR"
git add .
git commit -m "feat: add progress tracking UI with real-time status updates

- Added gradio_ui_with_progress.py for detailed progress visibility
- Shows entity extraction, relation extraction stages in real-time
- Added gradio_ui_fixed.py with event-loop safe implementation
- Documented MinerU models and processing stages
- Handles Azure OpenAI rate limiting gracefully"

git push

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Successfully pushed to GitHub!"
echo "🔗 Repository: https://github.com/WaiYanNyeinNaing/RAG_Every"