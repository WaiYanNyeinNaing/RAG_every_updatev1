# Pillow Version Conflict Resolution

## The Problem

There's a version conflict between packages:
- **mineru[core]** requires: `Pillow >= 11.0.0`
- **gradio 4.44.0** requires: `Pillow >= 6.2.0` (any version)
- **matplotlib 3.7.2** requires: `Pillow >= 6.2.0` (any version)

When pip tries to install, it can't satisfy mineru's strict requirement without potentially breaking gradio/matplotlib.

## Solutions (Try in Order)

### Solution 1: Use Compatible Pillow Version (Recommended)

```bash
# Create fresh virtual environment
python3 -m venv venv_rag_clean
source venv_rag_clean/bin/activate

# Install with specific Pillow version
pip install Pillow==10.4.0

# Run the fix script
python fix_pillow_conflict.py
```

### Solution 2: Install with Relaxed Dependencies

```bash
# Install packages without strict dependency checking
pip install --no-deps gradio==4.44.0
pip install --no-deps matplotlib==3.7.2
pip install --no-deps mineru

# Then install dependencies manually
pip install -r requirements_fixed_v2.txt
```

### Solution 3: Use Older MinerU Version

```bash
# MinerU 2.0.x has less strict Pillow requirements
pip install Pillow==10.4.0
pip install mineru==2.0.0
pip install gradio==4.44.0
pip install matplotlib==3.7.2
```

### Solution 4: Install MinerU from Source (Advanced)

```bash
# Clone MinerU
git clone https://github.com/opendatalab/MinerU.git
cd MinerU

# Edit requirements.txt to change Pillow requirement
# Change: Pillow>=11.0.0
# To: Pillow>=10.0.0

# Install modified version
pip install -e .
```

## Quick Fix Script

Run this automated fix:

```bash
chmod +x install_fixed.sh
./install_fixed.sh
```

Or use Python script:

```bash
python fix_pillow_conflict.py
```

## Working Package Versions

These versions are confirmed to work together:

| Package | Version | Notes |
|---------|---------|-------|
| Pillow | 10.4.0 | Compatible with all |
| gradio | 4.44.0 | UI framework |
| matplotlib | 3.7.2 | For MinerU |
| mineru | 2.0.0 or 2.1.10* | *May need --no-deps |
| lightrag-hku | 1.4.5+ | Core RAG |

## If You Still Get Errors

### Error: "No module named 'PIL'"
```bash
pip uninstall pillow
pip install Pillow==10.4.0 --force-reinstall
```

### Error: "mineru requires Pillow>=11.0.0"
```bash
# Install mineru without dependencies
pip install mineru --no-deps

# Then install its dependencies manually
pip install click loguru pdfminer.six pypdf opencv-python-headless
```

### Error: "gradio not working"
```bash
# Reinstall gradio with its dependencies
pip uninstall gradio
pip install gradio==4.44.0
pip install gradio-client fastapi uvicorn
```

## Alternative: Docker Solution

If conflicts persist, use Docker:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    git

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements_fixed_v2.txt .

# Install Python packages in order
RUN pip install Pillow==10.4.0
RUN pip install numpy>=2.0.0
RUN pip install gradio==4.44.0 --no-deps
RUN pip install matplotlib==3.7.2 --no-deps
RUN pip install mineru --no-deps || pip install mineru==2.0.0
RUN pip install -r requirements_fixed_v2.txt

# Copy application
COPY . .

# Run application
CMD ["python", "gradio_ui_gemini.py"]
```

## Testing Your Installation

After installation, test with:

```python
# test_packages.py
import PIL
import gradio
import matplotlib
import mineru
import lightrag

print(f"✅ Pillow: {PIL.__version__}")
print(f"✅ Gradio: {gradio.__version__}")
print(f"✅ Matplotlib: {matplotlib.__version__}")
print("✅ MinerU: installed")
print("✅ LightRAG: installed")
print("\n🎉 All packages working!")
```

## Prevention for Future

1. Always use a virtual environment
2. Install packages in specific order
3. Pin versions in requirements.txt
4. Use `--no-deps` flag when conflicts arise
5. Consider using Poetry or Pipenv for better dependency management

## Support

If none of these solutions work:
1. Post the full error message
2. Include output of `pip list`
3. Specify your Python version and OS
4. Try with Python 3.10 (most tested)