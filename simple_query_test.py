#!/usr/bin/env python
"""
Simple query test using direct LightRAG
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from lightrag import LightRAG
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def test_lightrag_directly():
    """Test using LightRAG directly with existing storage"""
    
    print("Testing LightRAG with existing storage...")
    
    # Initialize LightRAG directly
    rag = LightRAG(
        working_dir="./rag_ui_storage",
        llm_model_func=create_azure_llm_func(),
        embedding_func=create_azure_embedding_func()
    )
    
    # Test queries
    questions = [
        "What product is described in the document?",
        "What are the product benefits?",
        "What technical specifications are mentioned?"
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        try:
            # Use different query modes
            for mode in ["hybrid", "local"]:
                print(f"\nMode: {mode}")
                result = await rag.aquery(
                    question,
                    mode=mode,
                    enable_rerank=False
                )
                print(f"Answer: {result[:300]}..." if len(result) > 300 else f"Answer: {result}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lightrag_directly())