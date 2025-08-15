#!/usr/bin/env python3
"""
Simple Transparency Tool for Product Launch
Stable version without complex UI features
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import gradio as gr
from openai import AzureOpenAI
import PyPDF2

# Storage paths
RAG_STORAGE_PATH = Path("./rag_storage")
DOCUMENT_CACHE_PATH = Path("./document_cache.json")

# Global variables
processed_documents = {}
azure_client = None
embedding_client = None

def initialize_azure():
    """Initialize Azure OpenAI clients"""
    global azure_client, embedding_client
    
    try:
        azure_client = AzureOpenAI(
            api_key=os.getenv("LLM_BINDING_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
            azure_endpoint=os.getenv("LLM_BINDING_HOST")
        )
        
        embedding_client = AzureOpenAI(
            api_key=os.getenv("EMBEDDING_BINDING_API_KEY"),
            api_version=os.getenv("AZURE_EMBEDDING_API_VERSION", "2024-02-01"),
            azure_endpoint=os.getenv("EMBEDDING_BINDING_HOST")
        )
        
        print("✅ Azure connected")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def load_existing_data():
    """Load existing documents from RAG storage"""
    global processed_documents
    
    loaded = 0
    
    # Load from RAG storage
    if RAG_STORAGE_PATH.exists():
        docs_file = RAG_STORAGE_PATH / "kv_store_full_docs.json"
        if docs_file.exists():
            try:
                with open(docs_file, 'r') as f:
                    rag_docs = json.load(f)
                    for doc_id, doc_data in rag_docs.items():
                        fname = f"Document_{doc_id[:8]}"
                        processed_documents[fname] = {
                            "text": doc_data.get("content", ""),
                            "analysis": f"Loaded from RAG storage (ID: {doc_id[:8]})",
                            "doc_id": doc_id
                        }
                        loaded += 1
                print(f"📚 Loaded {loaded} documents from RAG storage")
            except Exception as e:
                print(f"Error loading: {e}")
    
    return loaded

def extract_text_from_file(file_path):
    """Extract text from uploaded file"""
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        elif file_ext in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            return f"Unsupported file type: {file_ext}"
    except Exception as e:
        return f"Error: {str(e)}"

def process_files(files):
    """Process uploaded files"""
    global processed_documents, azure_client
    
    if not files:
        return "No files uploaded", ""
    
    if not azure_client:
        initialize_azure()
    
    results = []
    for file in files:
        fname = Path(file.name).name
        text = extract_text_from_file(file.name)
        
        if "Error" in text or "Unsupported" in text:
            results.append(f"❌ {fname}: {text}")
        else:
            # Simple analysis
            analysis = f"Document processed: {len(text)} characters"
            processed_documents[fname] = {
                "text": text,
                "analysis": analysis
            }
            results.append(f"✅ {fname}: Processed successfully")
    
    summary = f"Processed {len(files)} files\nTotal documents: {len(processed_documents)}"
    details = "\n".join(results)
    
    return summary, details

def query_documents(query):
    """Query processed documents"""
    global azure_client, processed_documents
    
    if not processed_documents:
        return "No documents loaded. Please upload files first."
    
    if not azure_client:
        initialize_azure()
        if not azure_client:
            return "Azure not connected. Check .env file."
    
    try:
        # Build context
        context = ""
        sources = []
        for fname, doc in list(processed_documents.items())[:5]:
            context += f"\nDocument: {fname}\n{doc['text'][:2000]}\n"
            sources.append(fname)
        
        # Query Azure
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
            messages=[
                {"role": "system", "content": "Answer based on the documents. Cite sources."},
                {"role": "user", "content": f"Question: {query}\n\nDocuments:\n{context[:5000]}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        return f"""📝 Query: {query}

{answer}

📚 Sources: {', '.join(sources)}
⏰ Generated: {datetime.now().strftime('%H:%M:%S')}"""
        
    except Exception as e:
        return f"Error: {str(e)}"

def get_library_info():
    """Get library status"""
    if not processed_documents:
        return "Library is empty"
    
    info = f"📚 Documents: {len(processed_documents)}\n\n"
    for fname, doc in processed_documents.items():
        info += f"• {fname}: {len(doc.get('text', ''))} chars\n"
    
    return info

# Initialize
print("\n" + "="*60)
print("🚀 Simple Transparency Tool for Product Launch")
print("="*60)

connected = initialize_azure()
docs_loaded = load_existing_data()

print(f"Status: {'Connected' if connected else 'Not connected'}")
print(f"Documents: {docs_loaded} loaded")
print("="*60)

# Create simple UI
with gr.Blocks(title="Transparency Tool") as demo:
    gr.Markdown("# 🚀 Transparency Tool for Product Launch")
    
    with gr.Row():
        gr.Markdown(f"**Status:** {'✅ Connected' if connected else '❌ Not connected'} | **Documents:** {docs_loaded}")
    
    with gr.Tab("📁 Upload"):
        file_input = gr.File(label="Upload Files", file_count="multiple")
        upload_btn = gr.Button("Process Files", variant="primary")
        upload_output = gr.Textbox(label="Summary", lines=3)
        upload_details = gr.Textbox(label="Details", lines=10)
        
        upload_btn.click(
            process_files,
            inputs=file_input,
            outputs=[upload_output, upload_details]
        )
    
    with gr.Tab("🔍 Query"):
        query_input = gr.Textbox(label="Your Question", lines=2)
        query_btn = gr.Button("Search", variant="primary")
        query_output = gr.Textbox(label="Answer", lines=15)
        
        query_btn.click(
            query_documents,
            inputs=query_input,
            outputs=query_output
        )
        
        gr.Examples(
            examples=[
                "What are the main risks?",
                "What is the timeline?",
                "Who are the stakeholders?"
            ],
            inputs=query_input
        )
    
    with gr.Tab("📚 Library"):
        refresh_btn = gr.Button("Refresh")
        library_info = gr.Textbox(label="Library Status", lines=15)
        
        refresh_btn.click(
            get_library_info,
            outputs=library_info
        )

if __name__ == "__main__":
    print(f"\n🌐 Opening at: http://127.0.0.1:7861\n")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False
    )