# Dependency Conflict Resolution Guide

## Known Issues & Solutions

### Problem: Version Conflicts
When installing RAG-Anything in a new environment, you may encounter conflicts between:
- **Gradio** (UI framework)
- **Matplotlib** (used by MinerU)
- **LightRAG** (core RAG engine)
- **MinerU** (document parser)

### Solution: Use Fixed Versions

## Quick Fix Installation

```bash
# 1. Clone the repository
git clone https://github.com/WaiYanNyeinNaing/RAG_Every.git
cd RAG-Anything

# 2. Use the installation script
chmod +x install_dependencies.sh
./install_dependencies.sh
```

## Manual Installation (if script fails)

```bash
# 1. Create virtual environment
python -m venv venv_rag_anything
source venv_rag_anything/bin/activate

# 2. Install in specific order
pip install numpy>=2.0.0
pip install matplotlib==3.10.5
pip install gradio==5.41.0
pip install mineru[core]==2.1.10
pip install lightrag-hku==1.4.5

# 3. Install other dependencies
pip install -r requirements_fixed.txt
```

## Working Versions (Tested & Confirmed)

| Package | Version | Notes |
|---------|---------|-------|
| **gradio** | 5.41.0 | UI framework |
| **matplotlib** | 3.10.5 | Required by MinerU |
| **mineru** | 2.1.10 | PDF parser |
| **lightrag-hku** | 1.4.5 | Core RAG engine |
| **numpy** | >=2.0.0 | Base dependency |
| **protobuf** | 5.29.5 | For Gemini |
| **grpcio** | 1.74.0 | For Gemini |

## Common Errors & Fixes

### Error: "ImportError: cannot import name 'xxx' from 'gradio'"
**Fix**: Install specific gradio version
```bash
pip uninstall gradio
pip install gradio==5.41.0
```

### Error: "matplotlib.pyplot not found"
**Fix**: Install specific matplotlib version
```bash
pip uninstall matplotlib
pip install matplotlib==3.10.5
```

### Error: "No module named 'lightrag'"
**Fix**: Install LightRAG
```bash
# If you have LightRAG in parent directory:
pip install -e ..

# Otherwise:
pip install lightrag-hku==1.4.5
```

### Error: "MinerU command not found"
**Fix**: Install MinerU with core extras
```bash
pip install mineru[core]==2.1.10
```

## Environment Variables

Make sure your `.env` file contains:

### For Azure/GPT-4:
```env
LLM_BINDING_API_KEY=your-azure-key
LLM_BINDING_HOST=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### For Gemini:
```env
GEMINI_API_KEY=your-gemini-key
```

## Testing Your Installation

```bash
# Test all components
python -c "
import gradio
import matplotlib
import mineru
import lightrag
print('✅ All packages imported successfully!')
print(f'Gradio: {gradio.__version__}')
print(f'Matplotlib: {matplotlib.__version__}')
"

# Test MinerU
mineru --version

# Test connections
python test_azure_connection.py   # For Azure
python test_gemini_local.py       # For Gemini
```

## Still Having Issues?

1. **Clean Install**:
```bash
rm -rf venv_rag_anything
python -m venv venv_rag_anything
source venv_rag_anything/bin/activate
./install_dependencies.sh
```

2. **Check Python Version**:
- Required: Python 3.10+
- Check: `python --version`

3. **Update pip**:
```bash
pip install --upgrade pip setuptools wheel
```

4. **Use requirements_fixed.txt**:
```bash
pip install -r requirements_fixed.txt
```

## Why These Conflicts Happen

1. **MinerU** requires specific matplotlib version for PDF rendering
2. **Gradio** has frequent updates that may break compatibility
3. **LightRAG** depends on specific versions of its dependencies
4. **Protobuf** versions conflict between Azure and Gemini SDKs

The `requirements_fixed.txt` file pins all versions to ensure compatibility.