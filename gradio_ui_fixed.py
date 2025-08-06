#!/usr/bin/env python
"""
Fixed Gradio UI for RAG-Anything with Azure OpenAI
Handles event loop issues properly
"""

import os
import asyncio
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
import logging
import nest_asyncio
from typing import Optional

# IMPORTANT: Allow nested event loops (fixes the event loop issue)
nest_asyncio.apply()

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func, create_azure_vision_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gradio_ui.log')
    ]
)
logger = logging.getLogger(__name__)

# Global RAG instance
rag_instance = None
# Global lock for thread safety
init_lock = asyncio.Lock()

async def initialize_rag_async():
    """Initialize RAG-Anything with Azure OpenAI (async-safe version)"""
    global rag_instance
    
    async with init_lock:
        if rag_instance is None:
            config = RAGAnythingConfig(
                working_dir="./rag_ui_storage",
                parser="mineru",
                parse_method="auto",
                enable_image_processing=True,
                enable_table_processing=True,
                enable_equation_processing=True,
                display_content_stats=True,
                # Important: Set max workers to avoid overwhelming async
                max_concurrent_files=2
            )
            
            rag_instance = RAGAnything(
                config=config,
                llm_model_func=create_azure_llm_func(),
                embedding_func=create_azure_embedding_func(),
                vision_model_func=create_azure_vision_func()
            )
            
            # Initialize LightRAG properly
            await rag_instance._ensure_lightrag_initialized()
            logger.info("RAG-Anything initialized successfully")
    
    return rag_instance

def initialize_rag():
    """Synchronous wrapper for initialization"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create task
            task = asyncio.create_task(initialize_rag_async())
            return asyncio.run_coroutine_threadsafe(task, loop).result()
        else:
            # If no loop running, create new one
            return asyncio.run(initialize_rag_async())
    except RuntimeError:
        # Fallback: create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(initialize_rag_async())

async def process_document_async(file_path):
    """Process a document asynchronously (event-loop safe)"""
    rag = await initialize_rag_async()
    
    # Check if document already processed
    doc_status = await rag.get_document_status(
        os.path.basename(file_path)
    )
    
    if doc_status.get('fully_processed', False):
        logger.info(f"Document already fully processed: {file_path}")
        return f"✅ Document already processed: {os.path.basename(file_path)}"
    
    await rag.process_document_complete(
        file_path=file_path,
        output_dir="./parsed_output_ui"
    )
    return f"✅ Successfully processed: {os.path.basename(file_path)}"

def process_document(file):
    """Process uploaded document (thread-safe wrapper)"""
    if file is None:
        return "Please upload a document first."
    
    try:
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async processing
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                process_document_async(file.name), 
                loop
            )
            result = future.result(timeout=300)  # 5 minute timeout
        else:
            result = loop.run_until_complete(
                process_document_async(file.name)
            )
        
        return result
    except asyncio.TimeoutError:
        logger.error("Document processing timed out")
        return "❌ Processing timed out. Please try a smaller document."
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        return f"❌ Error processing document: {str(e)}"

async def query_async(question, timeout_seconds=60):
    """Query the processed documents asynchronously (event-loop safe)"""
    import time
    start_time = time.time()
    
    logger.info(f"Starting query: {question[:100]}...")
    rag = await initialize_rag_async()
    
    try:
        # Check for simple queries that might use bypass mode
        simple_keywords = ['hello', 'hi', 'test', 'ping']
        if any(keyword in question.lower() for keyword in simple_keywords):
            logger.info("Detected simple query, using bypass mode")
            mode = "bypass"
        else:
            mode = "hybrid"
        
        logger.info(f"Executing query in {mode} mode...")
        
        # Use wait_for to implement timeout
        result = await asyncio.wait_for(
            rag.aquery(
                question,
                mode=mode,
                enable_rerank=False
            ),
            timeout=timeout_seconds
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Query completed in {elapsed:.2f} seconds. Result length: {len(result)}")
        return result
        
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        logger.error(f"Query timed out after {elapsed:.2f} seconds")
        raise
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Query failed after {elapsed:.2f} seconds: {str(e)}")
        raise

def query_documents(question, timeout_seconds=60):
    """Query the processed documents (thread-safe wrapper)"""
    if not question:
        return "Please enter a question."
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"New query request: {question}")
        logger.info(f"Timeout set to: {timeout_seconds} seconds")
        logger.info(f"{'='*60}")
        
        # Check if storage exists
        storage_path = "./rag_ui_storage"
        if not os.path.exists(storage_path):
            return "❌ No documents have been processed yet. Please upload and process a document first."
        
        # Check if any documents are indexed
        chunks_file = os.path.join(storage_path, "vdb_chunks.json")
        if not os.path.exists(chunks_file):
            return "❌ No documents in the index. Please process a document first."
        
        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run async query
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                query_async(question, timeout_seconds),
                loop
            )
            result = future.result(timeout=timeout_seconds + 5)  # Extra buffer
        else:
            result = loop.run_until_complete(
                query_async(question, timeout_seconds)
            )
        
        logger.info(f"Returning result to UI: {result[:200]}...")
        return result
        
    except asyncio.TimeoutError:
        return f"⏱️ Query timed out after {timeout_seconds} seconds. This might be due to:\n" \
               f"1. Complex query requiring more processing\n" \
               f"2. Network latency to Azure OpenAI\n" \
               f"3. Large document corpus\n\n" \
               f"Try a simpler query or increase timeout."
    except Exception as e:
        logger.error(f"Error querying documents: {e}", exc_info=True)
        return f"❌ Error: {str(e)}\n\nPlease check the logs for more details."

def process_existing_pdf():
    """Process the existing product.pdf file"""
    pdf_path = "output/product.pdf"
    if os.path.exists(pdf_path):
        try:
            # Create a simple file object
            class SimpleFile:
                def __init__(self, name):
                    self.name = name
            
            return process_document(SimpleFile(pdf_path))
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return f"❌ Error processing PDF: {str(e)}"
    else:
        return f"❌ File not found: {pdf_path}"

# Create Gradio interface
with gr.Blocks(title="RAG-Anything UI") as demo:
    gr.Markdown("""
    # 🚀 RAG-Anything with Azure OpenAI
    
    Upload documents and ask questions about them using multimodal RAG.
    """)
    
    with gr.Tab("Upload & Process"):
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="Upload Document",
                    file_types=[".pdf", ".txt", ".md", ".docx", ".png", ".jpg", ".jpeg"]
                )
                process_btn = gr.Button("Process Document", variant="primary")
                
                # Button to process existing PDF
                gr.Markdown("### Or process existing document:")
                existing_pdf_btn = gr.Button("Process output/product.pdf", variant="secondary")
                
            with gr.Column():
                process_output = gr.Textbox(
                    label="Processing Status",
                    lines=3,
                    interactive=False
                )
        
        process_btn.click(
            fn=process_document,
            inputs=[file_input],
            outputs=[process_output]
        )
        
        existing_pdf_btn.click(
            fn=process_existing_pdf,
            inputs=[],
            outputs=[process_output]
        )
    
    with gr.Tab("Query Documents"):
        with gr.Row():
            with gr.Column():
                question_input = gr.Textbox(
                    label="Ask a Question",
                    placeholder="What is this document about?",
                    lines=2
                )
                
                # Add timeout slider
                with gr.Row():
                    timeout_slider = gr.Slider(
                        minimum=10,
                        maximum=120,
                        value=60,
                        step=10,
                        label="Query Timeout (seconds)",
                        info="Increase for complex queries"
                    )
                
                query_btn = gr.Button("Submit Query", variant="primary")
                
                # Example questions
                gr.Markdown("### Example Questions:")
                example_btns = []
                examples = [
                    "What is the main topic of this document?",
                    "Summarize the key features or findings.",
                    "What data or statistics are mentioned?",
                    "List all the technical specifications.",
                    "What are the main benefits described?"
                ]
                
                for example in examples:
                    btn = gr.Button(example, size="sm", variant="secondary")
                    example_btns.append(btn)
                
            with gr.Column():
                answer_output = gr.Textbox(
                    label="Answer",
                    lines=10,
                    interactive=False
                )
        
        # Connect query button with timeout
        query_btn.click(
            fn=lambda q, t: query_documents(q, timeout_seconds=t),
            inputs=[question_input, timeout_slider],
            outputs=[answer_output]
        )
        
        # Connect example buttons with timeout
        for btn, example in zip(example_btns, examples):
            btn.click(
                fn=lambda x=example: x,
                outputs=[question_input]
            ).then(
                fn=lambda q, t: query_documents(q, timeout_seconds=t),
                inputs=[question_input, timeout_slider],
                outputs=[answer_output]
            )
    
    with gr.Tab("Info"):
        gr.Markdown("""
        ## 📋 How to Use
        
        1. **Upload Document**: Go to the "Upload & Process" tab and upload your document
        2. **Process**: Click "Process Document" to parse and index the content
        3. **Query**: Go to "Query Documents" tab and ask questions
        
        ## 🎯 Features
        
        - **Multimodal Processing**: Handles text, tables, images, and equations
        - **Azure OpenAI**: Powered by GPT-4 and text-embedding-3-large
        - **Smart Caching**: Avoids re-processing already indexed documents
        - **Event Loop Safe**: Handles async operations properly
        
        ## ⚙️ Current Configuration
        
        - LLM: Azure OpenAI GPT-4
        - Embeddings: Azure OpenAI text-embedding-3-large
        - Parser: MinerU 2.0
        - Storage: Local (./rag_ui_storage)
        """)

if __name__ == "__main__":
    # Check environment variables
    required_vars = [
        "LLM_BINDING_API_KEY",
        "LLM_BINDING_HOST",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file.")
        exit(1)
    
    print("🚀 Starting RAG-Anything UI (Event-Loop Safe Version)...")
    print("📂 Ready to process documents!")
    
    # Launch the interface
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )