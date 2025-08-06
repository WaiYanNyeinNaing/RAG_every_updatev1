#!/usr/bin/env python
"""
Fixed query test for product.pdf
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from lightrag import LightRAG, QueryParam
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

async def query_product_pdf():
    """Query the already processed product.pdf"""
    
    print("🔍 Querying product.pdf from existing storage...")
    print("="*60)
    
    # Initialize LightRAG with existing storage
    rag = LightRAG(
        working_dir="./rag_ui_storage",
        llm_model_func=create_azure_llm_func(),
        embedding_func=create_azure_embedding_func()
    )
    
    # Questions about your product
    questions = [
        "What product is described in this document?",
        "What are the main product benefits mentioned?",
        "What technical specifications or features are listed?",
        "What transmission types are mentioned?",
        "What is meant by 'robust design' in this context?",
        "What kind of sensors are discussed?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Question {i}: {question}")
        print('='*60)
        
        try:
            # Query with proper parameters
            result = await rag.aquery(
                question,
                param=QueryParam(
                    mode="hybrid",
                    enable_rerank=False
                )
            )
            
            # Display result
            print(f"\n📝 Answer:")
            print(result)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Try without param
            try:
                result = await rag.aquery(question)
                print(f"\n📝 Answer (default mode):")
                print(result)
            except Exception as e2:
                print(f"❌ Error with default query: {e2}")

    # Interactive mode
    print("\n" + "="*60)
    print("💬 Interactive Mode - Ask your own questions!")
    print("Type 'quit' to exit")
    print("="*60)
    
    while True:
        try:
            question = input("\n❓ Your question: ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question.strip():
                continue
            
            print("\n🤔 Thinking...")
            result = await rag.aquery(
                question,
                param=QueryParam(
                    mode="hybrid",
                    enable_rerank=False
                )
            )
            print(f"\n📝 Answer:\n{result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("RAG-Anything Product PDF Query Tool")
    print("Using existing processed data from: ./rag_ui_storage")
    print()
    
    asyncio.run(query_product_pdf())