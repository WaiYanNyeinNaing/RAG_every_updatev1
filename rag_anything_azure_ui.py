#!/usr/bin/env python3
"""
Clean and Simple RAG-Anything UI with Azure OpenAI
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
from openai import AzureOpenAI
import PyPDF2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables
processed_documents = {}
processing_status = {}
azure_client = None
embedding_client = None

def initialize_azure():
    """Initialize Azure OpenAI clients"""
    global azure_client, embedding_client
    
    try:
        # LLM Client
        azure_client = AzureOpenAI(
            api_key=os.getenv("LLM_BINDING_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("LLM_BINDING_HOST")
        )
        
        # Embedding Client
        embedding_client = AzureOpenAI(
            api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),
            api_version=os.getenv("AZURE_EMBEDDING_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("EMBEDDING_BINDING_HOST")
        )
        
        logger.info("✅ Azure connected")
        return True
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False

# Auto-initialize on startup
connected = initialize_azure()

def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_file(file_path):
    """Extract text based on file type"""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['.txt', '.md']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif file_ext in ['.docx', '.doc']:
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        except:
            return "Install python-docx: pip install python-docx"
    else:
        return f"Unsupported: {file_ext}"

def analyze_document(text, filename):
    """Analyze document with Azure GPT-4"""
    global azure_client
    
    if not azure_client:
        return "Not connected to Azure"
    
    try:
        prompt = f"""Analyze this document and extract:
1. Main topics
2. Key findings
3. Important dates
4. Risks or issues

Document: {filename}
Content: {text[:3000]}"""

        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
            messages=[
                {"role": "system", "content": "Extract key information from documents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_embedding(text):
    """Get embedding from Azure"""
    global embedding_client
    
    if not embedding_client:
        return None
    
    try:
        response = embedding_client.embeddings.create(
            model=os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
            input=text[:7000]
        )
        return response.data[0].embedding
    except:
        return None

def process_files(files):
    """Process uploaded files"""
    global processed_documents, processing_status, azure_client
    
    if not files:
        return "No files uploaded", []
    
    if not azure_client:
        initialize_azure()
        if not azure_client:
            return "❌ Cannot connect to Azure. Check .env settings.", []
    
    results = []
    file_names = [Path(f.name).name for f in files]
    
    log = f"Processing {len(files)} files...\n" + "="*50 + "\n\n"
    
    for i, file in enumerate(files, 1):
        fname = Path(file.name).name
        log += f"[{i}/{len(files)}] {fname}\n"
        
        try:
            # Extract text
            text = extract_text_from_file(file.name)
            if "Error" in text or not text:
                results.append([fname, "❌ Failed"])
                log += f"  ❌ Text extraction failed\n\n"
                continue
            
            # Analyze
            analysis = analyze_document(text, fname)
            
            # Get embedding
            embedding = get_embedding(text[:2000])
            
            # Store
            processed_documents[fname] = {
                "text": text,
                "analysis": analysis,
                "embedding": embedding
            }
            
            results.append([fname, "✅ Complete"])
            log += f"  ✅ Processed successfully\n\n"
            
        except Exception as e:
            results.append([fname, f"❌ {str(e)[:30]}"])
            log += f"  ❌ Error: {str(e)[:50]}\n\n"
    
    log += "="*50 + f"\n✅ Complete: {len(processed_documents)} documents ready for queries"
    
    return log, results

def query_documents(query, mode):
    """Query processed documents"""
    global azure_client, processed_documents
    
    if not processed_documents:
        return "No documents processed yet. Upload and process files first."
    
    if not azure_client:
        return "Not connected to Azure"
    
    try:
        # Build context with source tracking
        context_parts = []
        source_docs = []
        for fname, doc in list(processed_documents.items())[:5]:
            context_parts.append(f"Document: {fname}\n{doc['analysis']}\n{doc['text'][:500]}")
            source_docs.append(fname)
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Answer this question based on the documents. Include specific references to which documents support your statements.

Question: {query}

Documents:
{context[:4000]}

IMPORTANT: When answering, cite the specific document names that support each key point."""

        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
            messages=[
                {"role": "system", "content": f"Answer in {mode} mode. Always cite specific document sources."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        answer = response.choices[0].message.content
        
        # Format references section
        references = "\n".join([f"  [{i+1}] {fname}" for i, fname in enumerate(source_docs)])
        
        return f"""📝 Query: {query}
🔍 Mode: {mode}

{answer}

═══════════════════════════════════════
📚 References:
{references}

⏰ Generated: {datetime.now().strftime('%H:%M:%S')}"""
        
    except Exception as e:
        return f"Error: {str(e)}"

def clear_all():
    """Clear all documents"""
    global processed_documents, processing_status
    count = len(processed_documents)
    processed_documents = {}
    processing_status = {}
    return f"Cleared {count} documents", []

# Create clean UI
with gr.Blocks(title="Transparency Tool for Product Launch", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚀 Transparency Tool for Product Launch (AI Agents)")
    
    # Simple connection status
    with gr.Row():
        connection_status = gr.Textbox(
            value="✅ Connected" if connected else "❌ Not connected - Check .env",
            show_label=False,
            interactive=False,
            scale=4
        )
        reconnect_btn = gr.Button("🔄", scale=1)
        
    def reconnect():
        success = initialize_azure()
        return "✅ Connected" if success else "❌ Connection failed"
    
    reconnect_btn.click(reconnect, outputs=connection_status)
    
    with gr.Tabs():
        # Process Tab
        with gr.TabItem("📁 Process"):
            files = gr.File(
                label="Upload Files",
                file_count="multiple",
                file_types=[".pdf", ".txt", ".md", ".docx"]
            )
            
            process_btn = gr.Button("Process Files", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column(scale=2):
                    process_log = gr.Textbox(
                        label="Log",
                        lines=15,
                        interactive=False
                    )
                
                with gr.Column(scale=1):
                    file_status = gr.Dataframe(
                        headers=["File", "Status"],
                        label="Status"
                    )
            
            process_btn.click(
                process_files,
                inputs=files,
                outputs=[process_log, file_status]
            )
        
        # Query Tab
        with gr.TabItem("🔍 Query"):
            query_input = gr.Textbox(
                label="Question",
                placeholder="What are the main risks?",
                lines=2
            )
            
            with gr.Row():
                query_mode = gr.Radio(
                    choices=["hybrid", "local", "global"],
                    value="hybrid",
                    label="Mode",
                    scale=3
                )
                query_btn = gr.Button("Ask", variant="primary", scale=1)
            
            query_output = gr.Textbox(
                label="Answer",
                lines=20,
                interactive=False
            )
            
            gr.Examples(
                examples=[
                    ["What are the main risks?"],
                    ["What is the timeline?"],
                    ["Who are the stakeholders?"],
                ],
                inputs=query_input
            )
            
            query_btn.click(
                query_documents,
                inputs=[query_input, query_mode],
                outputs=query_output
            )
        
        # Library Tab
        with gr.TabItem("📚 Library"):
            def show_library():
                if not processed_documents:
                    return "No documents", []
                
                data = [[fname, f"{len(doc['text'])} chars"] 
                        for fname, doc in processed_documents.items()]
                summary = f"{len(processed_documents)} documents"
                return summary, data
            
            with gr.Row():
                refresh_btn = gr.Button("Refresh")
                clear_btn = gr.Button("Clear All", variant="stop")
            
            lib_summary = gr.Textbox(label="Summary", interactive=False)
            lib_table = gr.Dataframe(
                headers=["Document", "Size"],
                label="Documents"
            )
            
            refresh_btn.click(show_library, outputs=[lib_summary, lib_table])
            clear_btn.click(clear_all, outputs=[lib_summary, lib_table])

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Transparency Tool for Product Launch (AI Agents)")
    print("="*50)
    print(f"Azure: {'Connected' if connected else 'Not connected'}")
    print(f"URL: http://127.0.0.1:7861")
    print("="*50 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True
    )