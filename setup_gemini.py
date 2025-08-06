#!/usr/bin/env python
"""
Quick setup and test for Google Gemini API
"""

import os
import webbrowser
from dotenv import load_dotenv
import subprocess
import sys

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

def setup_gemini():
    """Help user setup Gemini API"""
    
    print("\n" + "="*60)
    print("🚀 Google Gemini Setup for RAG-Anything")
    print("="*60)
    
    # Check if API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "":
        print("\n❌ No Gemini API key found in .env")
        print("\n📝 Let's get you a FREE API key (takes 2 minutes):\n")
        
        print("1️⃣  Opening Google AI Studio in your browser...")
        print("    (If browser doesn't open, visit: https://aistudio.google.com/apikey)\n")
        
        # Try to open browser
        try:
            webbrowser.open("https://aistudio.google.com/apikey")
        except:
            print("    Could not open browser automatically.")
            print("    Please visit: https://aistudio.google.com/apikey\n")
        
        print("2️⃣  Click 'Get API Key' button")
        print("3️⃣  Select 'Create API key in new project'")
        print("4️⃣  Copy the API key that appears\n")
        
        # Get API key from user
        api_key = input("5️⃣  Paste your API key here: ").strip()
        
        if api_key:
            # Update .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            # Update or add GEMINI_API_KEY
            found = False
            for i, line in enumerate(lines):
                if line.startswith("GEMINI_API_KEY="):
                    lines[i] = f"GEMINI_API_KEY={api_key}\n"
                    found = True
                    break
            
            if not found:
                lines.append(f"\nGEMINI_API_KEY={api_key}\n")
            
            with open(".env", "w") as f:
                f.writelines(lines)
            
            print("\n✅ API key saved to .env file!")
            return api_key
        else:
            print("\n❌ No API key provided. Exiting...")
            return None
    else:
        print(f"\n✅ Gemini API key found (length: {len(api_key)})")
        return api_key

def test_gemini_connection(api_key):
    """Test the Gemini connection"""
    
    print("\n" + "="*60)
    print("🧪 Testing Gemini Connection...")
    print("="*60)
    
    try:
        import google.generativeai as genai
    except ImportError:
        print("\n📦 Installing Google Gemini SDK...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
        import google.generativeai as genai
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    try:
        print("\n📝 Testing Gemini 2.0 Flash...")
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            "Say 'Hello from Gemini!' in exactly 3 words",
            generation_config={
                "temperature": 0,
                "max_output_tokens": 50
            }
        )
        
        print(f"✅ Response: {response.text}")
        
        print("\n📊 Testing embeddings...")
        embedding_result = genai.embed_content(
            model="models/text-embedding-004",
            content="Test embedding",
            task_type="retrieval_document",
            title="Test"
        )
        
        print(f"✅ Embedding dimension: {len(embedding_result['embedding'])}")
        
        print("\n" + "="*60)
        print("🎉 Success! Gemini is ready to use!")
        print("="*60)
        
        print("\n💰 Cost Comparison (per 1M tokens):")
        print("  Gemini 2.0 Flash: $0.075 input, $0.30 output")
        print("  GPT-4: $30 input, $60 output (400x more!)")
        
        print("\n🚀 You can now run:")
        print("  python gradio_ui_gemini.py")
        print("  OR")
        print("  ./launch_gemini.sh")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        if "API_KEY_INVALID" in str(e):
            print("\n🔑 Invalid API key. Please check:")
            print("  - Key is correctly copied")
            print("  - No extra spaces")
            print("  - Try generating a new key")
        
        return False

def main():
    # Setup API key
    api_key = setup_gemini()
    
    if api_key:
        # Test connection
        success = test_gemini_connection(api_key)
        
        if success:
            print("\n🎯 Next steps:")
            print("1. Process documents: python gradio_ui_gemini.py")
            print("2. The UI will open at: http://localhost:7861")
            print("3. Upload a PDF and click 'Process with Gemini'")
            print("4. Ask questions about your document")
            
            # Ask if user wants to start now
            start_now = input("\n🚀 Start Gemini UI now? (y/n): ").strip().lower()
            if start_now == 'y':
                print("\nStarting Gemini UI...")
                subprocess.run([sys.executable, "gradio_ui_gemini.py"])

if __name__ == "__main__":
    main()