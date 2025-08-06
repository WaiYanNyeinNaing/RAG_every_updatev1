#!/usr/bin/env python
"""
Test Azure OpenAI connection to diagnose hanging issue
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def test_azure_connection():
    """Test Azure OpenAI connection directly"""
    
    print("Testing Azure OpenAI Connection (GPT-4.1/gpt-4o)...")
    print("-" * 60)
    
    # Check environment variables
    required_vars = {
        "LLM_BINDING_API_KEY": os.getenv("LLM_BINDING_API_KEY"),
        "LLM_BINDING_HOST": os.getenv("LLM_BINDING_HOST"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "EMBEDDING_BINDING_API_KEY": os.getenv("EMBEDDING_BINDING_API_KEY"),
        "EMBEDDING_BINDING_HOST": os.getenv("EMBEDDING_BINDING_HOST"),
    }
    
    print("Environment Variables Status:")
    for var, value in required_vars.items():
        if value:
            print(f"  ✓ {var}: Set (length: {len(value)})")
        else:
            print(f"  ✗ {var}: NOT SET")
    
    print("\n" + "-" * 60)
    
    # Test Azure OpenAI API call
    from openai import AsyncAzureOpenAI
    
    api_key = os.getenv("LLM_BINDING_API_KEY")
    azure_endpoint = os.getenv("LLM_BINDING_HOST")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    
    if not all([api_key, azure_endpoint, api_version]):
        print("ERROR: Missing required Azure OpenAI configuration")
        return
    
    print(f"Testing connection to: {azure_endpoint}")
    print(f"Using deployment: {deployment}")
    print(f"API Version: {api_version}")
    
    try:
        client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version
        )
        
        print("\nSending test query...")
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Connection successful' in 3 words."}
                ],
                temperature=0,
                max_tokens=50
            ),
            timeout=10  # 10 second timeout
        )
        
        print(f"✓ Success! Response: {response.choices[0].message.content}")
        
    except asyncio.TimeoutError:
        print("✗ ERROR: Request timed out after 10 seconds")
        print("  The Azure OpenAI endpoint is not responding")
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_azure_connection())