#!/usr/bin/env python
"""
Simplified Azure OpenAI test focusing on direct LightRAG usage
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
import functools

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc

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
        base_url=azure_endpoint + "/openai/deployments/" + deployment,
        api_version=api_version,
        model=deployment
    )
    
    async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        # Filter out any duplicate parameters
        filtered_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['api_key', 'base_url', 'api_version', 'model']}
        
        return await azure_llm(
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
        full_url = azure_endpoint + "/openai/deployments/" + deployment
        return await openai_embed(
            texts,
            model=deployment,
            api_key=api_key,
            base_url=full_url
        )
    
    return EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=8192,
        func=azure_embed_func
    )

async def test_lightrag_azure():
    """Test basic LightRAG with Azure OpenAI"""
    
    logger.info("Initializing LightRAG with Azure OpenAI...")
    
    # Create Azure-compatible functions
    llm_model_func = create_azure_llm_func()
    embedding_func = create_azure_embedding_func()
    
    # Initialize LightRAG
    rag = LightRAG(
        working_dir="./rag_storage_simple",
        llm_model_func=llm_model_func,
        embedding_func=embedding_func
    )
    
    # Test with simple text
    logger.info("Testing with simple text insertion...")
    
    test_content = """
# RAG-Anything: Advanced Multimodal RAG System

## Key Features
- Supports multiple document types (PDF, images, tables, equations)
- Uses MinerU 2.0 for advanced document parsing
- Integrates seamlessly with LightRAG
- Provides multimodal query capabilities

## Performance
RAG-Anything achieves 95.2% accuracy on benchmark tests, outperforming traditional RAG systems by 8%.

## Usage
Initialize RAG-Anything with your preferred LLM and embedding models, then process documents using the simple API.
"""
    
    try:
        # Insert content
        logger.info("Inserting content into RAG...")
        await rag.ainsert(test_content)
        logger.info("Content inserted successfully!")
        
        # Test queries
        logger.info("\nTesting queries...")
        queries = [
            "What is RAG-Anything?",
            "What accuracy does RAG-Anything achieve?",
            "What document types are supported?"
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
    print("LightRAG Azure OpenAI Test")
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
    asyncio.run(test_lightrag_azure())

if __name__ == "__main__":
    main()