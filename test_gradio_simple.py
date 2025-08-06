#!/usr/bin/env python
"""
Simple test of Gradio UI query functionality
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import sys
sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def test_simple_query():
    """Test a simple query directly"""
    
    print("Initializing RAG-Anything...")
    
    # Initialize with existing storage
    config = RAGAnythingConfig(
        working_dir="./rag_ui_storage",
        parser="mineru",
        parse_method="auto"
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=create_azure_llm_func(),
        embedding_func=create_azure_embedding_func()
    )
    
    # Ensure LightRAG is initialized
    print("Initializing LightRAG...")
    await rag._ensure_lightrag_initialized()
    print("LightRAG initialized successfully")
    
    # Test query with timeout
    question = "What is the main topic of this document?"
    print(f"\nQuestion: {question}")
    print("-" * 60)
    
    try:
        print("Executing query...")
        result = await asyncio.wait_for(
            rag.aquery(question, mode="hybrid", enable_rerank=False),
            timeout=30
        )
        print(f"\nAnswer: {result[:500]}...")
        print(f"\nFull answer length: {len(result)} characters")
    except asyncio.TimeoutError:
        print("ERROR: Query timed out after 30 seconds")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_query())