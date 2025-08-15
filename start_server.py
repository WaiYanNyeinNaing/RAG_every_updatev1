#!/usr/bin/env python3
"""
Startup script for Transparency Tool for Product Launch
Handles port conflicts and ensures clean startup
"""

import os
import sys
import subprocess
import time
import socket
from pathlib import Path

def check_port(port):
    """Check if a port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def kill_port_process(port):
    """Kill process using the specified port"""
    try:
        # Get PID of process using the port
        result = subprocess.run(
            f"lsof -t -i:{port}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            pid = result.stdout.strip()
            print(f"🛑 Stopping existing process (PID: {pid}) on port {port}...")
            subprocess.run(f"kill -9 {pid}", shell=True)
            time.sleep(2)
            print(f"✅ Process stopped")
            return True
        return False
    except Exception as e:
        print(f"⚠️  Could not kill process: {e}")
        return False

def check_requirements():
    """Check and install required packages"""
    required_packages = {
        'gradio': 'gradio',
        'openai': 'openai',
        'PyPDF2': 'PyPDF2',
        'dotenv': 'python-dotenv',
        'docx': 'python-docx'
    }
    
    print("📦 Checking required packages...")
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✅ {package} is installed")
        except ImportError:
            print(f"  📥 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         capture_output=True)
            print(f"  ✅ {package} installed")

def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Error: .env file not found!")
        print("📝 Creating .env from .env.sample...")
        
        sample_path = Path(".env.sample")
        if sample_path.exists():
            import shutil
            shutil.copy(".env.sample", ".env")
            print("✅ Created .env file")
            print("⚠️  Please edit .env with your Azure credentials before running again")
            return False
        else:
            print("❌ No .env.sample found either")
            print("Please create .env file with your Azure credentials")
            return False
    
    # Check if .env has actual credentials (not just template)
    with open(".env", "r") as f:
        content = f.read()
        if "your-resource-name" in content or "your-azure-openai-api-key" in content:
            print("⚠️  Warning: .env contains template values")
            print("Please update .env with your actual Azure credentials")
            return False
    
    print("✅ Found .env file with credentials")
    return True

def check_rag_storage():
    """Check for existing RAG storage"""
    rag_path = Path("rag_storage")
    if rag_path.exists():
        json_files = list(rag_path.glob("*.json"))
        print(f"📚 Found existing RAG storage with {len(json_files)} files")
        
        # Check for key files
        key_files = ["kv_store_full_docs.json", "vdb_chunks.json"]
        for kf in key_files:
            if (rag_path / kf).exists():
                print(f"  ✅ {kf} exists")
    else:
        print("📁 No existing RAG storage (will be created when needed)")

def main():
    """Main startup function"""
    print("="*60)
    print("🚀 Transparency Tool for Product Launch (AI Agents)")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required (you have {sys.version})")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check and kill existing process on port 7861
    port = 7861
    print(f"\n🔄 Checking port {port}...")
    
    if check_port(port):
        print(f"⚠️  Port {port} is in use")
        if not kill_port_process(port):
            print(f"❌ Could not free port {port}")
            print("Try running: lsof -t -i:7861 | xargs kill -9")
            sys.exit(1)
    else:
        print(f"✅ Port {port} is available")
    
    # Check requirements
    print()
    check_requirements()
    
    # Check .env file
    print()
    if not check_env_file():
        sys.exit(1)
    
    # Check RAG storage
    print()
    check_rag_storage()
    
    # Start the server
    print()
    print("="*60)
    print(f"🌐 Starting server at http://127.0.0.1:{port}")
    print("="*60)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Import and run the main application
        import transparency_tool_product_launch
        
        # The app will run from here
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct Azure credentials")
        print("2. Ensure all packages are installed: pip install -r requirements.txt")
        print("3. Try running directly: python transparency_tool_product_launch.py")
        sys.exit(1)

if __name__ == "__main__":
    main()