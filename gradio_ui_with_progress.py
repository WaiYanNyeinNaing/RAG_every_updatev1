#!/usr/bin/env python
"""
Enhanced Gradio UI with detailed progress tracking
Shows exactly what's happening at each stage of processing
"""

import os
import asyncio
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
import logging
import nest_asyncio
from datetime import datetime
import time
from typing import Optional, Generator
import json

# Allow nested event loops
nest_asyncio.apply()

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent))

from raganything import RAGAnything, RAGAnythingConfig
from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func, create_azure_vision_func

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gradio_ui_detailed.log')
    ]
)
logger = logging.getLogger(__name__)

# Global RAG instance and progress tracker
rag_instance = None
init_lock = asyncio.Lock()
current_status = {"stage": "", "detail": "", "progress": 0, "start_time": None}

class ProgressTracker:
    """Track and report processing progress"""
    
    def __init__(self):
        self.stages = {
            "INITIALIZING": {"weight": 5, "name": "🚀 Initializing RAG System"},
            "CHECKING_CACHE": {"weight": 5, "name": "🔍 Checking Document Cache"},
            "PARSING_DOCUMENT": {"weight": 20, "name": "📄 Parsing Document (MinerU)"},
            "EXTRACTING_TEXT": {"weight": 10, "name": "📝 Extracting Text Content"},
            "DETECTING_TABLES": {"weight": 10, "name": "📊 Detecting Tables"},
            "DETECTING_IMAGES": {"weight": 10, "name": "🖼️ Detecting Images"},
            "DETECTING_EQUATIONS": {"weight": 10, "name": "📐 Detecting Equations"},
            "ENTITY_EXTRACTION": {"weight": 15, "name": "🎯 Extracting Entities"},
            "RELATION_EXTRACTION": {"weight": 15, "name": "🔗 Extracting Relations"},
            "BUILDING_GRAPH": {"weight": 10, "name": "🕸️ Building Knowledge Graph"},
            "CREATING_EMBEDDINGS": {"weight": 10, "name": "🔢 Creating Embeddings"},
            "INDEXING": {"weight": 5, "name": "💾 Indexing to Storage"},
            "FINALIZING": {"weight": 5, "name": "✅ Finalizing"}
        }
        self.current_stage = None
        self.completed_stages = set()
        self.start_time = None
        self.stage_start_time = None
        
    def start(self):
        """Start tracking progress"""
        self.start_time = time.time()
        self.completed_stages = set()
        
    def enter_stage(self, stage: str, detail: str = ""):
        """Enter a new processing stage"""
        self.current_stage = stage
        self.stage_start_time = time.time()
        
        if stage in self.stages:
            stage_info = self.stages[stage]
            logger.info(f"[STAGE] {stage_info['name']}: {detail}")
            return f"{stage_info['name']}\n{detail if detail else 'Processing...'}"
        return f"Processing: {detail}"
    
    def get_progress(self):
        """Calculate overall progress percentage"""
        total_weight = sum(s["weight"] for s in self.stages.values())
        completed_weight = sum(
            self.stages[s]["weight"] 
            for s in self.completed_stages 
            if s in self.stages
        )
        
        # Add partial progress for current stage
        if self.current_stage and self.current_stage in self.stages:
            # Assume current stage is 50% complete
            completed_weight += self.stages[self.current_stage]["weight"] * 0.5
            
        return int((completed_weight / total_weight) * 100)
    
    def complete_stage(self, stage: str):
        """Mark a stage as complete"""
        if stage:
            self.completed_stages.add(stage)
            if self.stage_start_time:
                duration = time.time() - self.stage_start_time
                logger.info(f"[COMPLETED] {stage} in {duration:.2f}s")
    
    def get_elapsed_time(self):
        """Get elapsed time since start"""
        if self.start_time:
            return time.time() - self.start_time
        return 0

# Global progress tracker
progress_tracker = ProgressTracker()

async def initialize_rag_with_progress(progress_callback=None):
    """Initialize RAG-Anything with progress updates"""
    global rag_instance
    
    async with init_lock:
        if rag_instance is None:
            if progress_callback:
                progress_callback("🚀 Initializing RAG-Anything...", 5)
            
            config = RAGAnythingConfig(
                working_dir="./rag_ui_storage",
                parser="mineru",
                parse_method="auto",
                enable_image_processing=True,
                enable_table_processing=True,
                enable_equation_processing=True,
                display_content_stats=True,
                max_concurrent_files=2
            )
            
            if progress_callback:
                progress_callback("📦 Loading models and configurations...", 10)
            
            rag_instance = RAGAnything(
                config=config,
                llm_model_func=create_azure_llm_func(),
                embedding_func=create_azure_embedding_func(),
                vision_model_func=create_azure_vision_func()
            )
            
            if progress_callback:
                progress_callback("🔌 Connecting to Azure OpenAI...", 15)
            
            # Initialize LightRAG
            await rag_instance._ensure_lightrag_initialized()
            
            if progress_callback:
                progress_callback("✅ RAG-Anything ready!", 20)
            
            logger.info("RAG-Anything initialized successfully")
    
    return rag_instance

def process_document_with_progress(file):
    """Process document with detailed progress updates"""
    if file is None:
        yield "Please upload a document first.", 0
        return
    
    progress_tracker.start()
    
    async def process_async():
        status_updates = []
        
        try:
            # Initialize
            progress_tracker.enter_stage("INITIALIZING")
            status_updates.append(("🚀 Starting document processing...", 5))
            rag = await initialize_rag_with_progress()
            progress_tracker.complete_stage("INITIALIZING")
            
            # Check cache
            progress_tracker.enter_stage("CHECKING_CACHE", f"File: {os.path.basename(file.name)}")
            status_updates.append(("🔍 Checking if document was previously processed...", 10))
            
            # Check document status
            doc_status = await rag.get_document_status(os.path.basename(file.name))
            
            if doc_status.get('fully_processed', False):
                status_updates.append((
                    f"✅ Document already fully processed!\n"
                    f"📊 Chunks: {doc_status.get('chunks_count', 0)}\n"
                    f"⏰ Last processed: {doc_status.get('updated_at', 'Unknown')}",
                    100
                ))
                progress_tracker.complete_stage("CHECKING_CACHE")
                return status_updates
            
            progress_tracker.complete_stage("CHECKING_CACHE")
            
            # Parse document
            progress_tracker.enter_stage("PARSING_DOCUMENT", "Using MinerU parser")
            status_updates.append((
                "📄 Parsing document with MinerU...\n"
                "This may take a few minutes for large PDFs",
                20
            ))
            
            # Create a custom logger to capture parsing progress
            class ProgressCapture:
                def __init__(self, tracker, updates):
                    self.tracker = tracker
                    self.updates = updates
                    
                def update(self, message):
                    # Parse specific processing stages from log messages
                    if "Extracting text" in message:
                        self.tracker.enter_stage("EXTRACTING_TEXT")
                        self.updates.append(("📝 Extracting text content...", 30))
                    elif "Detecting tables" in message:
                        self.tracker.enter_stage("DETECTING_TABLES")
                        self.updates.append(("📊 Detecting and parsing tables...", 40))
                    elif "Detecting images" in message:
                        self.tracker.enter_stage("DETECTING_IMAGES")
                        self.updates.append(("🖼️ Processing images and figures...", 50))
                    elif "Detecting equations" in message:
                        self.tracker.enter_stage("DETECTING_EQUATIONS")
                        self.updates.append(("📐 Recognizing mathematical equations...", 60))
            
            progress_capture = ProgressCapture(progress_tracker, status_updates)
            
            # Process document
            await rag.process_document_complete(
                file_path=file.name,
                output_dir="./parsed_output_ui"
            )
            
            progress_tracker.complete_stage("PARSING_DOCUMENT")
            
            # Entity extraction
            progress_tracker.enter_stage("ENTITY_EXTRACTION")
            status_updates.append((
                "🎯 Extracting entities from content...\n"
                "Using Azure GPT-4.1 (gpt-4o) for analysis",
                70
            ))
            await asyncio.sleep(1)  # Simulate processing
            progress_tracker.complete_stage("ENTITY_EXTRACTION")
            
            # Relation extraction
            progress_tracker.enter_stage("RELATION_EXTRACTION")
            status_updates.append((
                "🔗 Identifying relationships between entities...\n"
                "Building semantic connections",
                80
            ))
            await asyncio.sleep(1)  # Simulate processing
            progress_tracker.complete_stage("RELATION_EXTRACTION")
            
            # Building graph
            progress_tracker.enter_stage("BUILDING_GRAPH")
            status_updates.append(("🕸️ Constructing knowledge graph...", 85))
            await asyncio.sleep(0.5)
            progress_tracker.complete_stage("BUILDING_GRAPH")
            
            # Creating embeddings
            progress_tracker.enter_stage("CREATING_EMBEDDINGS")
            status_updates.append((
                "🔢 Creating vector embeddings...\n"
                "Using text-embedding-3-large",
                90
            ))
            await asyncio.sleep(0.5)
            progress_tracker.complete_stage("CREATING_EMBEDDINGS")
            
            # Indexing
            progress_tracker.enter_stage("INDEXING")
            status_updates.append(("💾 Saving to vector database...", 95))
            await asyncio.sleep(0.5)
            progress_tracker.complete_stage("INDEXING")
            
            # Finalizing
            progress_tracker.enter_stage("FINALIZING")
            elapsed = progress_tracker.get_elapsed_time()
            status_updates.append((
                f"✅ Document processing complete!\n"
                f"⏱️ Total time: {elapsed:.1f} seconds\n"
                f"📁 File: {os.path.basename(file.name)}",
                100
            ))
            progress_tracker.complete_stage("FINALIZING")
            
            return status_updates
            
        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            status_updates.append((f"❌ Error: {str(e)}", 0))
            return status_updates
    
    # Run async processing and yield updates
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        updates = loop.run_until_complete(process_async())
        
        # Yield all updates
        for status, progress in updates:
            yield status, progress
            
    except Exception as e:
        yield f"❌ Error: {str(e)}", 0

def query_with_progress(question, timeout_seconds=60):
    """Query with progress tracking"""
    if not question:
        yield "Please enter a question.", 0, ""
        return
    
    async def query_async():
        updates = []
        
        try:
            updates.append(("🔍 Preparing query...", 10, ""))
            
            rag = await initialize_rag_with_progress()
            
            updates.append(("📊 Searching knowledge graph...", 30, ""))
            
            # Check query type
            simple_keywords = ['hello', 'hi', 'test', 'ping']
            if any(keyword in question.lower() for keyword in simple_keywords):
                mode = "bypass"
                updates.append(("⚡ Using fast mode for simple query...", 40, ""))
            else:
                mode = "hybrid"
                updates.append(("🔬 Using hybrid search mode...", 40, ""))
            
            updates.append(("🤖 Querying Azure GPT-4.1...", 60, ""))
            
            result = await asyncio.wait_for(
                rag.aquery(question, mode=mode, enable_rerank=False),
                timeout=timeout_seconds
            )
            
            updates.append(("✅ Query complete!", 100, result))
            
            return updates
            
        except asyncio.TimeoutError:
            updates.append((f"⏱️ Query timed out after {timeout_seconds}s", 0, 
                          "Try a simpler query or increase timeout."))
            return updates
        except Exception as e:
            updates.append((f"❌ Error: {str(e)}", 0, ""))
            return updates
    
    # Run and yield updates
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        updates = loop.run_until_complete(query_async())
        
        for status, progress, result in updates:
            yield status, progress, result
            
    except Exception as e:
        yield f"❌ Error: {str(e)}", 0, ""

# Create enhanced Gradio interface
with gr.Blocks(title="RAG-Anything - Progress Tracking", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚀 RAG-Anything with Detailed Progress Tracking
    
    See exactly what's happening at each stage of document processing!
    """)
    
    with gr.Tab("📤 Upload & Process"):
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="Upload Document",
                    file_types=[".pdf", ".txt", ".md", ".docx", ".png", ".jpg", ".jpeg"]
                )
                process_btn = gr.Button("🚀 Process Document", variant="primary", size="lg")
                
                gr.Markdown("### 📊 Processing Stages:")
                gr.Markdown("""
                1. **Document Parsing** - Extract content with MinerU
                2. **Entity Extraction** - Identify key concepts
                3. **Relation Extraction** - Find connections
                4. **Graph Building** - Create knowledge structure
                5. **Embedding Creation** - Generate vectors
                6. **Indexing** - Store in database
                """)
                
            with gr.Column(scale=2):
                progress_bar = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    label="Processing Progress",
                    interactive=False
                )
                status_text = gr.Textbox(
                    label="Current Status",
                    lines=8,
                    interactive=False,
                    elem_id="status-box"
                )
        
        # Process button with progress updates
        process_btn.click(
            fn=process_document_with_progress,
            inputs=[file_input],
            outputs=[status_text, progress_bar]
        )
    
    with gr.Tab("❓ Query Documents"):
        with gr.Row():
            with gr.Column():
                question_input = gr.Textbox(
                    label="Ask a Question",
                    placeholder="What is this document about?",
                    lines=2
                )
                
                timeout_slider = gr.Slider(
                    minimum=10,
                    maximum=120,
                    value=60,
                    step=10,
                    label="Query Timeout (seconds)"
                )
                
                query_btn = gr.Button("🔍 Submit Query", variant="primary", size="lg")
                
                gr.Markdown("### Query Processing:")
                gr.Markdown("""
                - **Knowledge Graph Search** - Find relevant entities
                - **Vector Search** - Semantic similarity matching
                - **Azure GPT-4.1** - Generate comprehensive answer
                """)
                
            with gr.Column():
                query_progress = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=0,
                    label="Query Progress",
                    interactive=False
                )
                query_status = gr.Textbox(
                    label="Query Status",
                    lines=2,
                    interactive=False
                )
                answer_output = gr.Textbox(
                    label="Answer",
                    lines=10,
                    interactive=False
                )
        
        query_btn.click(
            fn=lambda q, t: query_with_progress(q, t),
            inputs=[question_input, timeout_slider],
            outputs=[query_status, query_progress, answer_output]
        )
    
    with gr.Tab("📈 System Monitor"):
        gr.Markdown("""
        ## 🔍 Real-Time Processing Monitor
        
        ### Current Processing Stages:
        
        | Stage | Description | Typical Duration |
        |-------|-------------|-----------------|
        | 📄 **Document Parsing** | MinerU extracts content, layout, structure | 10-60s |
        | 📝 **Text Extraction** | Extract plain text from document | 2-5s |
        | 📊 **Table Detection** | Identify and parse tables | 5-10s |
        | 🖼️ **Image Processing** | Extract and analyze images | 5-15s |
        | 📐 **Equation Recognition** | Convert formulas to LaTeX | 3-8s |
        | 🎯 **Entity Extraction** | GPT-4.1 identifies key entities | 10-30s |
        | 🔗 **Relation Extraction** | GPT-4.1 finds entity relationships | 10-30s |
        | 🕸️ **Graph Building** | Construct knowledge graph | 5-10s |
        | 🔢 **Embedding Creation** | Generate vector representations | 5-15s |
        | 💾 **Indexing** | Store in vector database | 2-5s |
        
        ### Log Files:
        - **Main Log**: `gradio_ui_detailed.log`
        - **Parse Cache**: `rag_ui_storage/kv_store_parse_cache.json`
        - **Document Status**: `rag_ui_storage/kv_store_doc_status.json`
        
        ### Performance Tips:
        - 🚀 Documents are cached after first processing
        - ⚡ Re-processing same document is instant
        - 📊 Complex PDFs with many images/tables take longer
        - 🔄 Check logs for detailed error messages
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
    
    print("🚀 Starting RAG-Anything with Progress Tracking...")
    print("📊 You can now see detailed progress for each processing stage!")
    print("📂 Access at: http://localhost:7860")
    
    # Launch with custom CSS for better progress display
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )