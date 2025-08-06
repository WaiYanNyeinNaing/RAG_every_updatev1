#!/usr/bin/env python
"""
Test Gemini locally - quick check
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

print("\n" + "="*60)
print("🧪 Checking Gemini Setup")
print("="*60)

# Check if API key exists
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key or api_key == "":
    print("\n❌ No Gemini API key found in .env file")
    print("\n📝 To get a FREE Gemini API key:\n")
    print("1. Visit: https://aistudio.google.com/apikey")
    print("2. Click 'Get API Key' (no credit card needed!)")
    print("3. Copy the key")
    print("4. Edit .env file and add: GEMINI_API_KEY=your-key-here")
    print("5. Run this script again\n")
    print("💡 Gemini is 400x cheaper than GPT-4!")
    print("   - Gemini: $0.075 per 1M tokens")
    print("   - GPT-4: $30 per 1M tokens")
    print("   - Free tier: 1M tokens/month!")
    exit(1)

print(f"✅ API key found (length: {len(api_key)})")

# Try to import and test
try:
    import google.generativeai as genai
    print("✅ Google Gemini SDK installed")
except ImportError:
    print("❌ Google Gemini SDK not installed")
    print("   Run: pip install google-generativeai")
    exit(1)

# Configure and test
print("\n📡 Testing connection to Gemini...")
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content(
        "Reply with exactly: 'Gemini ready'",
        generation_config={"temperature": 0, "max_output_tokens": 10}
    )
    
    print(f"✅ Connection successful!")
    print(f"   Response: {response.text.strip()}")
    
    print("\n" + "="*60)
    print("🎉 Gemini is ready to use!")
    print("="*60)
    
    print("\n🚀 You can now run:")
    print("   python gradio_ui_gemini.py")
    print("\n   The UI will open at: http://localhost:7861")
    print("\n💡 Gemini advantages:")
    print("   - 400x cheaper than GPT-4")
    print("   - 2x faster processing")
    print("   - 2M token context (vs 128K)")
    print("   - Free tier: 1M tokens/month")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    
    if "API_KEY_INVALID" in str(e):
        print("\n🔑 Invalid API key. Please:")
        print("1. Get a new key from: https://aistudio.google.com/apikey")
        print("2. Update .env file with: GEMINI_API_KEY=your-new-key")
    elif "not found" in str(e).lower():
        print("\n⚠️ Model not available. Try:")
        print("   gemini-1.5-flash or gemini-1.5-pro")
    else:
        print("\n💡 Check your internet connection and try again")