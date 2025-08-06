#!/usr/bin/env python
"""
Test script specifically for processing and querying product.pdf
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

async def test_product_pdf():
    """Test RAG-Anything with product.pdf"""
    
    # Path to your PDF
    pdf_path = "output/product.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return
    
    logger.info(f"Found PDF file: {pdf_path}")
    
    # 1. Initialize RAG-Anything
    logger.info("Initializing RAG-Anything with Azure OpenAI...")
    
    config = RAGAnythingConfig(
        working_dir="./rag_product_storage",
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
        display_content_stats=True
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=create_azure_llm_func(),
        vision_model_func=create_azure_vision_func(),
        embedding_func=create_azure_embedding_func()
    )
    
    # 2. Process the PDF
    logger.info(f"\nProcessing PDF: {pdf_path}")
    logger.info("This may take a few minutes for the first time...")
    
    try:
        await rag.process_document_complete(
            file_path=pdf_path,
            output_dir="./parsed_product"
        )
        logger.info("✅ PDF processed successfully!")
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Query the document
    logger.info("\n" + "="*60)
    logger.info("Testing queries on product.pdf")
    logger.info("="*60)
    
    # General queries to understand your document
    queries = [
        "What is this product? Provide a brief overview.",
        "What are the main features or capabilities of this product?",
        "What technical specifications are mentioned?",
        "Who is the target audience or user for this product?",
        "What are the key benefits or advantages?",
        "Are there any pricing details or packages mentioned?",
        "What requirements or prerequisites are needed?",
        "Are there any limitations or constraints mentioned?"
    ]
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Query {i}: {query}")
        logger.info("="*60)
        
        try:
            result = await rag.aquery(
                query,
                mode="hybrid",
                enable_rerank=False
            )
            logger.info(f"Answer:\n{result}")
        except Exception as e:
            logger.error(f"Error with query: {e}")
    
    # 4. Interactive mode
    logger.info("\n" + "="*60)
    logger.info("Interactive Query Mode")
    logger.info("Type your questions (or 'quit' to exit)")
    logger.info("="*60)
    
    while True:
        try:
            question = input("\n💬 Your question: ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question.strip():
                continue
            
            logger.info("Thinking...")
            result = await rag.aquery(
                question,
                mode="hybrid",
                enable_rerank=False
            )
            print(f"\n📝 Answer:\n{result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    logger.info("\n✅ Test completed!")

def main():
    """Main function"""
    print("RAG-Anything Product PDF Test")
    print("=" * 60)
    
    # Check environment variables
    required_vars = [
        "LLM_BINDING_API_KEY",
        "LLM_BINDING_HOST", 
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return
    
    # Run the test
    asyncio.run(test_product_pdf())

if __name__ == "__main__":
    main()