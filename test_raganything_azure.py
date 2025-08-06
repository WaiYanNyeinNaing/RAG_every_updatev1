#!/usr/bin/env python
"""
Test RAG-Anything with Azure OpenAI using proper wrapper functions
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func, create_azure_vision_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_raganything():
    """Test RAG-Anything with Azure OpenAI wrappers"""
    
    logger.info("Initializing RAG-Anything with Azure OpenAI...")
    
    # Create configuration
    config = RAGAnythingConfig(
        working_dir="./rag_storage_azure_v2",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
        display_content_stats=True
    )
    
    # Create Azure-compatible functions
    llm_model_func = create_azure_llm_func()
    embedding_func = create_azure_embedding_func()
    vision_model_func = create_azure_vision_func()
    
    # Initialize RAG-Anything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func
    )
    
    # Test document
    test_file = "test_document.md"
    logger.info(f"Processing document: {test_file}")
    
    try:
        # Process the document
        logger.info("Processing document with RAG-Anything...")
        await rag.process_document_complete(
            test_file, 
            output_dir="./output",
            parse_method="auto"
        )
        logger.info("Document processed successfully!")
        
        # Test basic queries
        logger.info("\nTesting queries...")
        queries = [
            "What are the key features mentioned in the document?",
            "What is the accuracy comparison between different methods?",
            "Explain the F1-score formula from the document."
        ]
        
        for query in queries:
            logger.info(f"\nQuery: {query}")
            try:
                result = await rag.aquery(query, mode="hybrid")
                logger.info(f"Answer: {result[:200]}..." if len(result) > 200 else f"Answer: {result}")
            except Exception as e:
                logger.error(f"Query failed: {e}")
                
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Main function"""
    print("RAG-Anything Azure OpenAI Test")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "LLM_BINDING_API_KEY",
        "LLM_BINDING_HOST", 
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
        "EMBEDDING_BINDING_API_KEY",
        "EMBEDDING_BINDING_HOST",
        "AZURE_EMBEDDING_DEPLOYMENT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return
    
    logger.info("All required environment variables found!")
    
    # Run async test
    asyncio.run(test_raganything())

if __name__ == "__main__":
    main()