#!/usr/bin/env python3
"""
Comprehensive installer that resolves ALL dependency conflicts
Including: Pillow, pypdf, python-dotenv, subprocess errors
"""

import subprocess
import sys
import os
import platform

def run_command(cmd, capture=True, ignore_errors=False):
    """Run shell command with error handling"""
    print(f"  Running: {cmd}")
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode != 0 and not ignore_errors:
                print(f"  ⚠️  Warning: {result.stderr[:200]}")
                return False
            return True
        else:
            subprocess.run(cmd, shell=True, check=not ignore_errors, timeout=300)
            return True
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  Command timed out")
        return False
    except subprocess.SubprocessError as e:
        if not ignore_errors:
            print(f"  ⚠️  Subprocess error: {e}")
        return False

def install_package(package, method="pip", ignore_errors=False):
    """Install a package with multiple fallback methods"""
    methods = []
    
    if method == "pip":
        methods = [
            f"pip install {package}",
            f"pip install --no-deps {package}",
            f"pip install --no-binary :all: {package}",
            f"pip install --force-reinstall {package}"
        ]
    
    for i, cmd in enumerate(methods):
        print(f"  Method {i+1}: {cmd}")
        if run_command(cmd, ignore_errors=True):
            return True
    
    if not ignore_errors:
        print(f"  ❌ Failed to install {package}")
    return False

def main():
    print("🔧 RAG-Anything Complete Installation (Resolves ALL Conflicts)")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    print(f"📌 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("❌ Python 3.9+ required")
        sys.exit(1)
    
    # Step 1: Clean environment
    print("\n📦 Step 1: Cleaning environment...")
    run_command("pip uninstall -y pillow pypdf python-dotenv gradio matplotlib mineru", ignore_errors=True)
    
    # Step 2: Upgrade pip
    print("\n📦 Step 2: Upgrading pip...")
    run_command("pip install --upgrade pip setuptools wheel")
    
    # Step 3: Install core dependencies with specific versions
    print("\n📦 Step 3: Installing core dependencies...")
    
    packages_ordered = [
        # Core (must be first)
        ("numpy==1.26.4", "Core"),
        ("Pillow==10.4.0", "Image processing"),
        
        # Python-dotenv (older version to avoid subprocess issues)
        ("python-dotenv==1.0.1", "Environment variables"),
        
        # Gradio
        ("gradio==4.44.0", "UI framework"),
        ("gradio-client==1.3.0", "Gradio client"),
        
        # Matplotlib
        ("matplotlib==3.7.2", "Plotting"),
        
        # PDF processing (compatible versions)
        ("pypdf==3.17.4", "PDF processing"),
        ("pdfminer.six==20221105", "PDF mining"),
        ("pypdfium2==4.30.0", "PDF rendering"),
        
        # Document processing
        ("python-docx==1.1.2", "Word documents"),
        ("markdown==3.6", "Markdown"),
        ("openpyxl==3.1.5", "Excel files"),
        ("pandas==2.2.0", "Data processing"),
        ("tqdm==4.66.2", "Progress bars"),
        
        # LLM providers
        ("openai==1.50.0", "OpenAI/Azure"),
        ("google-generativeai==0.8.5", "Google Gemini"),
        
        # Azure
        ("azure-identity==1.17.1", "Azure auth"),
        ("azure-core==1.30.2", "Azure core"),
        
        # Networking
        ("aiohttp==3.9.5", "Async HTTP"),
        ("requests==2.31.0", "HTTP requests"),
        ("httpx==0.26.0", "Modern HTTP"),
        
        # Utilities
        ("tenacity==8.2.3", "Retry logic"),
        ("tiktoken==0.5.2", "Tokenization"),
        ("networkx==3.2.1", "Graph processing"),
        ("pydantic==2.5.3", "Data validation"),
        ("nest_asyncio==1.6.0", "Async nesting"),
        
        # Additional
        ("protobuf==4.25.3", "Protocol buffers"),
        ("grpcio==1.60.1", "gRPC"),
        ("huggingface_hub==0.20.3", "HuggingFace"),
        ("typing-extensions==4.9.0", "Typing"),
    ]
    
    failed_packages = []
    
    for package, description in packages_ordered:
        print(f"\n📦 Installing {package} ({description})...")
        if not install_package(package):
            failed_packages.append(package)
    
    # Step 4: Install MinerU (special handling)
    print("\n📦 Step 4: Installing MinerU...")
    mineru_installed = False
    
    # Try different MinerU installation methods
    mineru_methods = [
        "pip install mineru==2.0.0",  # Older version with less strict requirements
        "pip install --no-deps mineru",  # Without dependencies
        "pip install mineru --no-binary :all:",  # From source
    ]
    
    for method in mineru_methods:
        print(f"  Trying: {method}")
        if run_command(method, ignore_errors=True):
            mineru_installed = True
            break
    
    if not mineru_installed:
        print("  ⚠️  MinerU installation failed - continuing without it")
        print("     You can try installing it manually later")
    
    # Install MinerU dependencies
    mineru_deps = [
        "click", "loguru", "opencv-python-headless",
        "boto3", "modelscope", "fast-langdetect",
        "json-repair"
    ]
    
    print("\n📦 Installing MinerU dependencies...")
    for dep in mineru_deps:
        install_package(dep, ignore_errors=True)
    
    # Step 5: Install LightRAG
    print("\n📦 Step 5: Installing LightRAG...")
    if os.path.exists("../lightrag"):
        run_command("pip install -e ..", ignore_errors=True)
    else:
        install_package("lightrag-hku==1.4.5")
    
    # Step 6: Test installations
    print("\n🧪 Testing installations...")
    print("-" * 40)
    
    test_results = []
    
    # Test imports
    test_packages = [
        ("PIL", "Pillow", True),
        ("dotenv", "python-dotenv", True),
        ("gradio", "Gradio", True),
        ("matplotlib", "Matplotlib", True),
        ("pypdf", "PyPDF", True),
        ("openai", "OpenAI", True),
        ("google.generativeai", "Gemini", True),
        ("lightrag", "LightRAG", True),
        ("mineru", "MinerU", False),  # Optional
    ]
    
    for module, name, required in test_packages:
        try:
            __import__(module)
            print(f"✅ {name}")
            test_results.append((name, True))
        except ImportError:
            if required:
                print(f"❌ {name}")
                test_results.append((name, False))
            else:
                print(f"⚠️  {name} (optional)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Installation Summary:")
    
    all_required_ok = all(result for name, result in test_results if name != "MinerU")
    
    if all_required_ok:
        print("✅ All required packages installed successfully!")
    else:
        print("⚠️  Some packages failed. See above for details.")
    
    if failed_packages:
        print(f"\n⚠️  Failed packages: {', '.join(failed_packages)}")
        print("You may need to install these manually")
    
    # Create run scripts
    print("\n📝 Creating helper scripts...")
    
    # Create run_gemini.sh
    with open("run_gemini.sh", "w") as f:
        f.write("""#!/bin/bash
echo "🚀 Starting Gemini UI..."
python gradio_ui_gemini.py
""")
    os.chmod("run_gemini.sh", 0o755)
    
    # Create run_azure.sh
    with open("run_azure.sh", "w") as f:
        f.write("""#!/bin/bash
echo "🚀 Starting Azure UI..."
python gradio_ui.py
""")
    os.chmod("run_azure.sh", 0o755)
    
    print("\n✅ Helper scripts created:")
    print("   ./run_gemini.sh - Start Gemini version")
    print("   ./run_azure.sh - Start Azure version")
    
    print("\n🚀 Next Steps:")
    print("1. Configure API keys:")
    print("   cp .env.gemini.sample .env  # For Gemini")
    print("   cp .env.sample .env  # For Azure")
    print("\n2. Run the application:")
    print("   ./run_gemini.sh  # For Gemini")
    print("   ./run_azure.sh  # For Azure")

if __name__ == "__main__":
    main()