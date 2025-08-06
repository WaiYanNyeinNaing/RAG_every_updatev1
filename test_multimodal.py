#!/usr/bin/env python
"""
Test script for RAG-Anything with multimodal document processing
"""

import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from lightrag.llm.azure_openai import azure_openai_complete_if_cache, azure_openai_embed
from lightrag.utils import EmbeddingFunc
from raganything import RAGAnything, RAGAnythingConfig

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_raganything():
    """Test RAG-Anything with a sample document"""
    
    # Configuration
    api_key = os.getenv("LLM_BINDING_API_KEY")
    base_url = os.getenv("LLM_BINDING_HOST")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    if not api_key:
        logger.error("API key not found in environment variables")
        return
    
    logger.info("Initializing RAG-Anything...")
    
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
    
    # Define LLM function for Azure OpenAI
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return azure_openai_complete_if_cache(
            os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            api_version=azure_api_version,
            **kwargs
        )
    
    # Define vision model function (using same model for simplicity)
    vision_model_func = llm_model_func
    
    # Define embedding function for Azure OpenAI
    def azure_embed_func(texts):
        return azure_openai_embed(
            texts,
            model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
            api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),
            base_url=os.getenv("EMBEDDING_BINDING_HOST"),
            api_version=os.getenv("AZURE_EMBEDDING_API_VERSION")
        )
    
    embedding_func = EmbeddingFunc(
        embedding_dim=int(os.getenv("EMBEDDING_DIM", "3072")),
        max_token_size=8192,
        func=azure_embed_func
    )
    
    # Initialize RAG-Anything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func
    )
    
    # Process the test document
    test_file = "test_document.md"
    logger.info(f"Processing document: {test_file}")
    
    try:
        # Process document completely (parse + insert into LightRAG)
        await rag.process_document_complete(test_file, output_dir="./output")
        logger.info("Document processed successfully!")
        
        # Test queries
        queries = [
            "What are the key features of RAG-Anything?",
            "What is the accuracy of RAG-Anything compared to traditional RAG?",
            "What is the F1-score formula mentioned in the document?",
            "How do you initialize RAG-Anything according to the code snippet?"
        ]
        
        logger.info("\nTesting queries:")
        for query in queries:
            logger.info(f"\nQuery: {query}")
            result = await rag.aquery(query, mode="hybrid")
            logger.info(f"Answer: {result}")
            
        # Test multimodal query with table data
        logger.info("\nTesting multimodal query with table context:")
        multimodal_query = "Based on the performance data, which method has the best balance of accuracy and speed?"
        result = await rag.aquery_with_multimodal(
            multimodal_query,
            multimodal_content=[{
                "type": "table",
                "table_data": """Method,Accuracy,Processing_Time,Memory_Usage
RAG-Anything,95.2%,120ms,2.1GB
Traditional_RAG,87.3%,180ms,1.8GB
Baseline,82.1%,200ms,1.5GB""",
                "table_caption": "Performance comparison of different RAG methods"
            }],
            mode="hybrid"
        )
        logger.info(f"Multimodal Answer: {result}")
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Main function"""
    print("RAG-Anything Multimodal Test")
    print("=" * 50)
    print("Testing with Azure OpenAI configuration")
    print("=" * 50)
    
    # Run async test
    asyncio.run(test_raganything())

if __name__ == "__main__":
    main()