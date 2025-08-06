#!/usr/bin/env python
"""
Fixed test script for RAG-Anything with proper Azure OpenAI integration
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from raganything import RAGAnything, RAGAnythingConfig
import functools

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_azure_llm_func():
    """Create a wrapper for Azure OpenAI LLM calls"""
    api_key = os.getenv("LLM_BINDING_API_KEY")
    azure_endpoint = os.getenv("LLM_BINDING_HOST")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    
    # Create a partial function with Azure parameters
    azure_llm = functools.partial(
        openai_complete_if_cache,
        deployment,
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        model=deployment  # Azure uses deployment name as model
    )
    
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        # Filter out any duplicate parameters
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['api_key', 'azure_endpoint', 'api_version', 'model']}
        
        return azure_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            **filtered_kwargs
        )
    
    return llm_model_func

def create_azure_embedding_func():
    """Create a wrapper for Azure OpenAI embeddings"""
    api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
    azure_endpoint = os.getenv("EMBEDDING_BINDING_HOST")
    api_version = os.getenv("AZURE_EMBEDDING_API_VERSION")
    deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    embedding_dim = int(os.getenv("EMBEDDING_DIM", "3072"))
    
    # Create embedding function
    async def azure_embed_func(texts):
        # Use the standard openai_embed but with Azure endpoint
        return await openai_embed(
            texts,
            model=deployment,
            api_key=api_key,
            base_url=azure_endpoint
        )
    
    return EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=8192,
        func=azure_embed_func
    )

async def test_raganything():
    """Test RAG-Anything with proper Azure configuration"""
    
    logger.info("Initializing RAG-Anything with Azure OpenAI...")
    
    # Create configuration
    config = RAGAnythingConfig(
        working_dir="./rag_storage_azure",
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
    
    # For vision, use the same LLM function
    vision_model_func = llm_model_func
    
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
        # First, just parse the document
        logger.info("Step 1: Parsing document...")
        from raganything.parser import MineruParser
        parser = MineruParser()
        parse_result = parser.parse_document(
            file_path=test_file,
            output_dir="./output",
            method="auto"
        )
        logger.info("Document parsed successfully!")
        
        # Now process it with RAG
        logger.info("\nStep 2: Processing with RAG-Anything...")
        await rag.process_document_complete(
            test_file, 
            output_dir="./output",
            parse_method="auto"
        )
        logger.info("Document processed successfully!")
        
        # Test basic queries
        logger.info("\nStep 3: Testing queries...")
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
    print("RAG-Anything Azure OpenAI Integration Test")
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