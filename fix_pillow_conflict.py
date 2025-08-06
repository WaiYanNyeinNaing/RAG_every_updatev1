#!/usr/bin/env python3
"""
Fix Pillow version conflicts between gradio, matplotlib, and mineru
"""

import subprocess
import sys
import os

def run_command(cmd, ignore_errors=False):
    """Run a shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and not ignore_errors:
        print(f"Error: {result.stderr}")
        return False
    return True

def main():
    print("🔧 Fixing Pillow Version Conflicts")
    print("=" * 60)
    
    # Check if in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Not in a virtual environment!")
        print("Please activate your virtual environment first:")
        print("  source venv_rag/bin/activate")
        sys.exit(1)
    
    print("\n📦 Step 1: Uninstalling conflicting packages...")
    run_command("pip uninstall -y pillow gradio matplotlib mineru", ignore_errors=True)
    
    print("\n📦 Step 2: Installing Pillow 10.4.0 (compatible version)...")
    if not run_command("pip install Pillow==10.4.0"):
        print("Failed to install Pillow")
        sys.exit(1)
    
    print("\n📦 Step 3: Installing packages with --no-deps to avoid conflicts...")
    
    # Install gradio without dependencies
    print("Installing Gradio...")
    run_command("pip install gradio==4.44.0 --no-deps")
    
    # Install gradio's actual dependencies
    gradio_deps = [
        "fastapi", "uvicorn", "httpx", "pydantic", "typing-extensions",
        "orjson", "python-multipart", "ffmpy", "aiofiles", "jinja2",
        "semantic-version", "pyyaml", "importlib-resources", "gradio-client"
    ]
    for dep in gradio_deps:
        run_command(f"pip install {dep}", ignore_errors=True)
    
    # Install matplotlib without dependencies
    print("\nInstalling Matplotlib...")
    run_command("pip install matplotlib==3.7.2 --no-deps")
    
    # Install matplotlib's dependencies
    matplotlib_deps = [
        "numpy", "cycler", "pyparsing", "python-dateutil", 
        "kiwisolver", "contourpy", "fonttools", "packaging"
    ]
    for dep in matplotlib_deps:
        run_command(f"pip install {dep}", ignore_errors=True)
    
    print("\n📦 Step 4: Installing MinerU with modified requirements...")
    
    # First install MinerU dependencies that don't conflict
    mineru_deps = [
        "click", "loguru", "pdfminer.six", "pypdf", 
        "opencv-python-headless", "boto3", "modelscope", 
        "huggingface-hub", "fast-langdetect", "httpx", 
        "json-repair", "pdftext", "pypdfium2", "requests", "tqdm"
    ]
    
    print("Installing MinerU dependencies...")
    for dep in mineru_deps:
        run_command(f"pip install {dep}", ignore_errors=True)
    
    # Try to install mineru without strict Pillow requirement
    print("\nInstalling MinerU...")
    if not run_command("pip install mineru --no-deps", ignore_errors=True):
        print("⚠️  MinerU installation may have issues")
        print("You might need to install it from source with modified requirements")
    
    print("\n📦 Step 5: Installing remaining packages...")
    
    # Install other essential packages
    other_packages = [
        "lightrag-hku>=1.4.5",
        "python-dotenv",
        "openai",
        "azure-identity",
        "azure-core",
        "google-generativeai",
        "aiohttp",
        "tenacity",
        "tiktoken",
        "networkx",
        "nest_asyncio",
        "pandas",
        "openpyxl",
        "python-docx",
        "markdown",
        "protobuf",
        "grpcio"
    ]
    
    for package in other_packages:
        run_command(f"pip install {package}", ignore_errors=True)
    
    print("\n🧪 Testing installations...")
    print("-" * 40)
    
    # Test imports
    test_code = """
import sys
import importlib

packages = {
    'PIL': 'Pillow',
    'gradio': 'Gradio',
    'matplotlib': 'Matplotlib',
    'mineru': 'MinerU',
    'lightrag': 'LightRAG'
}

all_good = True
for module, name in packages.items():
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, '__version__', 'unknown')
        print(f'✅ {name} {version}')
    except ImportError as e:
        print(f'❌ {name}: Not found')
        all_good = False

if all_good:
    print('\\n✅ All packages installed successfully!')
else:
    print('\\n⚠️ Some packages need attention')
    """
    
    subprocess.run([sys.executable, '-c', test_code])
    
    print("\n" + "=" * 60)
    print("📝 Installation Notes:")
    print("1. If MinerU still has issues, you may need to:")
    print("   - Use an older version: pip install mineru==2.0.0")
    print("   - Or install from source with modified requirements")
    print("\n2. To run the application:")
    print("   - Azure/GPT-4: python gradio_ui.py")
    print("   - Gemini: python gradio_ui_gemini.py")

if __name__ == "__main__":
    main()