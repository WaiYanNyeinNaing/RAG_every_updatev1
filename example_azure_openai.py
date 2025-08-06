#!/usr/bin/env python
"""
Example: Using RAG-Anything with Azure OpenAI

This example demonstrates how to set up and use RAG-Anything with Azure OpenAI
for multimodal document processing and querying.
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Main example function"""
    
    # 1. Create configuration
    config = RAGAnythingConfig(
        working_dir="./rag_azure_storage",  # Where to store the RAG index
        parser="mineru",                    # Use MinerU for parsing
        parse_method="auto",                # Auto-detect document type
        enable_image_processing=True,       # Process images in documents
        enable_table_processing=True,       # Process tables in documents
        enable_equation_processing=True,    # Process equations in documents
        display_content_stats=True          # Show content statistics
    )
    
    # 2. Create Azure OpenAI functions
    logger.info("Setting up Azure OpenAI functions...")
    llm_model_func = create_azure_llm_func()
    embedding_func = create_azure_embedding_func()
    vision_model_func = create_azure_vision_func()
    
    # 3. Initialize RAG-Anything
    logger.info("Initializing RAG-Anything...")
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func
    )
    
    # 4. Process a document
    document_path = "test_document.md"  # Change this to your document
    logger.info(f"\nProcessing document: {document_path}")
    
    await rag.process_document_complete(
        file_path=document_path,
        output_dir="./parsed_output"  # Where to store parsed content
    )
    
    logger.info("Document processing completed!")
    
    # 5. Query the processed document
    logger.info("\n" + "="*50)
    logger.info("Testing queries on the processed document:")
    logger.info("="*50)
    
    # Example queries
    queries = [
        "What is the main topic of this document?",
        "Summarize the key findings or features.",
        "What data or statistics are mentioned?"
    ]
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\nQuery {i}: {query}")
        
        # Perform the query
        result = await rag.aquery(
            query, 
            mode="hybrid",  # Use hybrid search (semantic + keyword)
            enable_rerank=False  # Disable reranking since we don't have a rerank model
        )
        
        logger.info(f"Answer: {result}")
    
    # 6. Example of multimodal query (if your document has tables/images)
    logger.info("\n" + "="*50)
    logger.info("Testing multimodal query:")
    logger.info("="*50)
    
    multimodal_query = "Analyze the performance data and provide insights."
    
    # You can also provide additional context like tables or images
    multimodal_result = await rag.aquery_with_multimodal(
        multimodal_query,
        multimodal_content=[],  # Add specific multimodal content if needed
        mode="hybrid",
        enable_rerank=False
    )
    
    logger.info(f"Multimodal Answer: {multimodal_result}")
    
    logger.info("\n✅ Example completed successfully!")

if __name__ == "__main__":
    # Check required environment variables
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
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file.")
        exit(1)
    
    # Run the example
    asyncio.run(main())