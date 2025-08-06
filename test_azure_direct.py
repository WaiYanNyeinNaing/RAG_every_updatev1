#!/usr/bin/env python
"""
Direct test of Azure OpenAI functions without async complexity
"""

import os
from dotenv import load_dotenv
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
import asyncio

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def test_azure_functions():
    """Test Azure OpenAI functions directly"""
    
    # Get Azure configuration
    api_key = os.getenv("LLM_BINDING_API_KEY")
    azure_endpoint = os.getenv("LLM_BINDING_HOST")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    
    print("Testing Azure OpenAI Functions")
    print("=" * 50)
    print(f"Endpoint: {azure_endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Version: {api_version}")
    
    # Test 1: Direct LLM call
    print("\nTest 1: Direct LLM call...")
    try:
        # Build the full URL as Azure expects
        full_url = f"{azure_endpoint}/openai/deployments/{deployment}"
        
        result = await openai_complete_if_cache(
            deployment,  # model name
            "What is RAG-Anything?",
            system_prompt="You are a helpful assistant.",
            api_key=api_key,
            base_url=full_url,
            api_version=api_version
        )
        print(f"Success! Response: {result[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Embedding call
    print("\nTest 2: Embedding call...")
    try:
        embed_api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
        embed_endpoint = os.getenv("EMBEDDING_BINDING_HOST")
        embed_deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        embed_api_version = os.getenv("AZURE_EMBEDDING_API_VERSION")
        
        # Build the full URL for embeddings
        embed_full_url = f"{embed_endpoint}/openai/deployments/{embed_deployment}"
        
        embeddings = await openai_embed(
            ["What is RAG-Anything?", "How does it work?"],
            model=embed_deployment,
            api_key=embed_api_key,
            base_url=embed_full_url
        )
        print(f"Success! Got {len(embeddings)} embeddings")
        print(f"Embedding dimension: {len(embeddings[0])}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    # Run the async test
    asyncio.run(test_azure_functions())

if __name__ == "__main__":
    main()