#!/usr/bin/env python
"""
Direct query test for already processed documents
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def test_query():
    """Test querying existing RAG storage"""
    
    print("Testing direct query on existing RAG storage...")
    
    # Initialize with existing storage
    config = RAGAnythingConfig(
        working_dir="./rag_ui_storage",  # Use the existing storage
        parser="mineru",
        parse_method="auto"
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=create_azure_llm_func(),
        embedding_func=create_azure_embedding_func()
    )
    
    # Ensure LightRAG is initialized
    await rag._ensure_lightrag_initialized()
    
    # Test a simple query
    test_questions = [
        "What is this document about?",
        "What are the main features mentioned?",
        "List the key points from the document."
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 60)
        try:
            result = await rag.aquery(
                question,
                mode="hybrid",
                enable_rerank=False
            )
            print(f"Answer: {result}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_query())