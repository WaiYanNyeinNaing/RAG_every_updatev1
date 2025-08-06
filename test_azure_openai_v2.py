#!/usr/bin/env python
"""
Test Azure OpenAI with proper client initialization
"""

import os
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
import asyncio

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def test_azure_client():
    """Test Azure OpenAI with proper client setup"""
    
    # Get Azure configuration
    api_key = os.getenv("LLM_BINDING_API_KEY")
    azure_endpoint = os.getenv("LLM_BINDING_HOST")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    
    print("Testing Azure OpenAI with Proper Client")
    print("=" * 50)
    print(f"Endpoint: {azure_endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Version: {api_version}")
    
    # Create Azure OpenAI client for LLM
    llm_client = AsyncAzureOpenAI(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version
    )
    
    # Test 1: LLM call
    print("\nTest 1: Azure LLM call...")
    try:
        response = await llm_client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is RAG-Anything in one sentence?"}
            ],
            max_tokens=100,
            temperature=0
        )
        print(f"Success! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Embedding call
    print("\nTest 2: Azure Embedding call...")
    try:
        embed_api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
        embed_endpoint = os.getenv("EMBEDDING_BINDING_HOST")
        embed_deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        embed_api_version = os.getenv("AZURE_EMBEDDING_API_VERSION")
        
        # Create Azure OpenAI client for embeddings
        embed_client = AsyncAzureOpenAI(
            api_key=embed_api_key,
            azure_endpoint=embed_endpoint,
            api_version=embed_api_version
        )
        
        response = await embed_client.embeddings.create(
            model=embed_deployment,
            input=["What is RAG-Anything?", "How does it work?"]
        )
        
        embeddings = [item.embedding for item in response.data]
        print(f"Success! Got {len(embeddings)} embeddings")
        print(f"Embedding dimension: {len(embeddings[0])}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    # Run the async test
    asyncio.run(test_azure_client())

if __name__ == "__main__":
    main()