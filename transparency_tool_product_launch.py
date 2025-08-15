#!/usr/bin/env python3
"""
Transparency Tool for Product Launch (AI Agents)
With persistent storage and knowledge graph support
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
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
rag_storage_data = {}

# Storage paths
RAG_STORAGE_PATH = Path("./rag_storage")
OUTPUT_PATH = Path("./output")
DOCUMENT_CACHE_PATH = Path("./document_cache.json")

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

def sync_with_storage():
    """Sync document list with actual files in storage directories"""
    synced_docs = {}
    
    # Check RAG storage for actual documents
    if RAG_STORAGE_PATH.exists():
        docs_file = RAG_STORAGE_PATH / "kv_store_full_docs.json"
        if docs_file.exists():
            try:
                with open(docs_file, 'r') as f:
                    rag_docs = json.load(f)
                    for doc_id, doc_data in rag_docs.items():
                        # Use original filename if available in metadata
                        metadata = doc_data.get("metadata", {})
                        fname = metadata.get("filename")
                        if not fname:
                            fname = f"Document_{doc_id[:8]}"
                        
                        synced_docs[fname] = {
                            "source": "rag_storage",
                            "doc_id": doc_id,
                            "exists": True
                        }
                        
                        # Don't create duplicate entries with doc IDs when we have the original filename
            except Exception as e:
                logger.error(f"Error reading RAG storage: {e}")
    
    # Check output directory for PDFs
    if OUTPUT_PATH.exists():
        for pdf_file in OUTPUT_PATH.glob("*.pdf"):
            if pdf_file.name not in synced_docs:
                synced_docs[pdf_file.name] = {
                    "source": "output",
                    "path": str(pdf_file),
                    "exists": True
                }
    
    return synced_docs

def load_existing_data():
    """Load existing processed documents and RAG storage data - dynamically synced"""
    global processed_documents, rag_storage_data
    
    loaded_docs = 0
    has_rag_storage = False
    
    # First, sync with actual storage to see what really exists
    actual_files = sync_with_storage()
    
    # Store current in-memory documents that aren't from storage
    in_memory_docs = {}
    for fname, doc in processed_documents.items():
        # Keep documents that were just processed but not yet in storage
        if not doc.get('doc_id') and fname not in actual_files:
            in_memory_docs[fname] = doc
    
    # Clear processed_documents to reload from storage
    processed_documents.clear()
    
    # Load from RAG storage if exists
    if RAG_STORAGE_PATH.exists():
        try:
            # Load full documents from RAG storage
            docs_file = RAG_STORAGE_PATH / "kv_store_full_docs.json"
            if docs_file.exists():
                with open(docs_file, 'r') as f:
                    rag_docs = json.load(f)
                    # Only add documents that actually exist
                    for doc_id, doc_data in rag_docs.items():
                        # Try to get original filename from metadata, fallback to doc ID
                        metadata = doc_data.get("metadata", {})
                        fname = metadata.get("filename")
                        if not fname:
                            fname = f"Document_{doc_id[:8]}"
                        
                        # Check if this document exists in actual files by filename
                        if fname in actual_files:
                            content = doc_data.get("content", "")
                            analysis = metadata.get("analysis", f"Loaded from existing RAG storage (ID: {doc_id[:8]})")
                            
                            processed_documents[fname] = {
                                "text": content,
                                "analysis": analysis,
                                "processed_date": datetime.fromtimestamp(doc_data.get("create_time", 0)).isoformat() if doc_data.get("create_time") else datetime.now().isoformat(),
                                "doc_id": doc_id
                            }
                            loaded_docs += 1
                
                # Load other RAG storage files for reference
                chunks_file = RAG_STORAGE_PATH / "vdb_chunks.json"
                if chunks_file.exists():
                    with open(chunks_file, 'r') as f:
                        rag_storage_data['chunks'] = json.load(f)
                
                entities_file = RAG_STORAGE_PATH / "vdb_entities.json"
                if entities_file.exists():
                    with open(entities_file, 'r') as f:
                        rag_storage_data['entities'] = json.load(f)
                
                has_rag_storage = True
                logger.info(f"📚 Loaded {loaded_docs} documents from RAG storage")
                
        except Exception as e:
            logger.error(f"Error loading RAG storage: {e}")
    
    # Load cached metadata but only for files that actually exist
    if DOCUMENT_CACHE_PATH.exists():
        try:
            with open(DOCUMENT_CACHE_PATH, 'r') as f:
                cache_data = json.load(f)
                stale_entries = []
                for fname, metadata in cache_data.items():
                    # Check if this cached file actually exists in storage
                    if fname in actual_files:
                        if fname not in processed_documents:
                            processed_documents[fname] = metadata
                            loaded_docs += 1
                    else:
                        stale_entries.append(fname)
                
                if stale_entries:
                    logger.info(f"🧹 Removing {len(stale_entries)} stale cache entries: {', '.join(stale_entries[:3])}...")
                    # Update cache to remove stale entries
                    save_document_cache()
                    
        except Exception as e:
            logger.error(f"Error loading document cache: {e}")
    
    # Add any output PDFs that aren't in processed_documents
    if OUTPUT_PATH.exists():
        for pdf_file in OUTPUT_PATH.glob("*.pdf"):
            if pdf_file.name not in processed_documents and pdf_file.name in actual_files:
                processed_documents[pdf_file.name] = {
                    "text": f"PDF file in output directory",
                    "analysis": f"Found in output directory",
                    "processed_date": datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat(),
                    "doc_id": ""
                }
                loaded_docs += 1
    
    # Restore in-memory documents that aren't in storage yet
    for fname, doc in in_memory_docs.items():
        processed_documents[fname] = doc
        loaded_docs += 1
    
    logger.info(f"✅ Sync complete: {loaded_docs} valid documents found")
    
    # Save the synced state to cache
    if loaded_docs > 0:
        save_document_cache()
    
    return loaded_docs, has_rag_storage

def save_document_cache():
    """Save document metadata to cache"""
    try:
        cache_data = {}
        for fname, doc in processed_documents.items():
            cache_data[fname] = {
                "analysis": doc.get("analysis", ""),
                "processed_date": doc.get("processed_date", datetime.now().isoformat()),
                "text_length": len(doc.get("text", "")),
                "doc_id": doc.get("doc_id", "")
            }
        
        with open(DOCUMENT_CACHE_PATH, 'w') as f:
            json.dump(cache_data, f, indent=2)
        logger.info(f"💾 Saved document cache with {len(cache_data)} entries")
    except Exception as e:
        logger.error(f"Error saving document cache: {e}")

def save_to_rag_storage():
    """Save current documents to RAG storage format"""
    try:
        # Create RAG storage directory if it doesn't exist
        RAG_STORAGE_PATH.mkdir(exist_ok=True)
        
        # Prepare documents for RAG storage
        rag_docs = {}
        for fname, doc in processed_documents.items():
            # Generate or use existing doc_id
            doc_id = doc.get('doc_id') or f"doc-{hash(fname + doc.get('text', ''))}"
            rag_docs[doc_id] = {
                "content": doc.get('text', ''),
                "create_time": int(datetime.now().timestamp()),
                "metadata": {
                    "filename": fname,
                    "analysis": doc.get('analysis', '')
                }
            }
        
        # Save to RAG storage
        docs_file = RAG_STORAGE_PATH / "kv_store_full_docs.json"
        with open(docs_file, 'w') as f:
            json.dump(rag_docs, f, indent=2)
        
        logger.info(f"💾 Saved {len(rag_docs)} documents to RAG storage")
        return True
    except Exception as e:
        logger.error(f"Error saving to RAG storage: {e}")
        return False

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
1. Main topics and themes
2. Key findings and insights
3. Important dates and milestones
4. Risks, issues, or concerns
5. Key stakeholders mentioned

Document: {filename}
Content: {text[:3000]}"""

        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
            messages=[
                {"role": "system", "content": "You are analyzing documents for a product launch transparency tool. Extract key information relevant to product launch planning and risk assessment."},
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

def process_files(files, merge_mode=True):
    """Process uploaded files with option to merge or replace"""
    global processed_documents, processing_status, azure_client
    
    if not files:
        return "No files uploaded", []
    
    if not azure_client:
        initialize_azure()
        if not azure_client:
            return "❌ Cannot connect to Azure. Check .env settings.", []
    
    results = []
    file_names = [Path(f.name).name for f in files]
    
    # Initialize counters
    existing_count = len(processed_documents) if merge_mode else 0
    new_count = 0
    
    log = f"{'Merging' if merge_mode else 'Processing'} {len(files)} files...\n"
    if merge_mode and existing_count > 0:
        log += f"📚 Existing documents: {existing_count}\n"
    log += "="*50 + "\n\n"
    
    # Clear existing if not merging
    if not merge_mode:
        processed_documents = {}
        log += "🗑️ Cleared existing documents\n\n"
    
    for i, file in enumerate(files, 1):
        fname = Path(file.name).name
        
        # Skip if already processed in merge mode
        if merge_mode and fname in processed_documents:
            results.append([fname, "⏭️ Already processed"])
            log += f"[{i}/{len(files)}] {fname}\n  ⏭️ Skipped (already in library)\n\n"
            continue
        
        log += f"[{i}/{len(files)}] {fname}\n"
        
        try:
            # Extract text
            text = extract_text_from_file(file.name)
            if "Error" in text or not text:
                results.append([fname, "❌ Failed"])
                log += f"  ❌ Text extraction failed\n\n"
                continue
            
            # Analyze
            log += f"  📊 Analyzing with Azure GPT-4...\n"
            analysis = analyze_document(text, fname)
            
            # Get embedding
            log += f"  🔢 Generating embeddings...\n"
            embedding = get_embedding(text[:2000])
            
            # Store
            processed_documents[fname] = {
                "text": text,
                "analysis": analysis,
                "embedding": embedding,
                "processed_date": datetime.now().isoformat()
            }
            
            new_count += 1
            results.append([fname, "✅ Complete"])
            log += f"  ✅ Processed successfully\n\n"
            
        except Exception as e:
            results.append([fname, f"❌ {str(e)[:30]}"])
            log += f"  ❌ Error: {str(e)[:50]}\n\n"
    
    # Save cache
    save_document_cache()
    
    total_docs = len(processed_documents)
    log += "="*50 + f"\n✅ Complete: {total_docs} total documents"
    if merge_mode and new_count > 0:
        log += f" ({new_count} new, {existing_count} existing)"
    
    # Save to RAG storage after processing
    if new_count > 0:
        if save_to_rag_storage():
            log += "\n💾 Saved to RAG storage"
        else:
            log += "\n⚠️ Could not save to RAG storage"
    
    return log, results

def query_documents(query, mode):
    """Query processed documents"""
    global azure_client, processed_documents, rag_storage_data
    
    if not processed_documents:
        return "No documents in library. Upload and process files first."
    
    if not azure_client:
        initialize_azure()
        if not azure_client:
            return "Not connected to Azure"
    
    try:
        # Build context with source tracking
        context_parts = []
        source_docs = []
        
        # Use all available documents (up to 10 for context)
        for fname, doc in list(processed_documents.items())[:10]:
            doc_text = doc.get('text', '')
            doc_analysis = doc.get('analysis', '')
            
            if doc_text:
                context_parts.append(f"Document: {fname}\nAnalysis: {doc_analysis}\nContent: {doc_text[:1000]}")
                source_docs.append(fname)
        
        if not context_parts:
            return "No document content available for querying."
        
        context = "\n\n".join(context_parts)
        
        # Enhanced prompt based on mode
        system_prompts = {
            "hybrid": "You are analyzing product launch documents. Provide comprehensive answers combining both specific details and overall themes. Always cite which documents support your statements.",
            "local": "You are analyzing product launch documents. Focus on specific details, facts, and direct quotes from the documents. Always cite the exact document source.",
            "global": "You are analyzing product launch documents. Focus on overall themes, patterns, and high-level insights across all documents. Identify common threads and relationships.",
            "naive": "Answer based on keyword matching and direct text references from the documents."
        }
        
        prompt = f"""Based on the product launch documents, answer this question comprehensively.
Include specific references to which documents support your statements.

Question: {query}

Available Documents:
{context[:6000]}

IMPORTANT: 
1. Cite specific document names when referencing information
2. If information is not available in the documents, clearly state that
3. Focus on information relevant to product launch planning and transparency"""

        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
            messages=[
                {"role": "system", "content": system_prompts.get(mode, system_prompts["hybrid"])},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        answer = response.choices[0].message.content
        
        # Format references section
        references = "\n".join([f"  [{i+1}] {fname}" for i, fname in enumerate(source_docs)])
        
        # Add RAG storage indicator if available
        storage_status = "RAG Storage" if rag_storage_data else "Direct Processing"
        
        return f"""📝 Query: {query}
🔍 Mode: {mode} | 💾 Source: {storage_status}

{answer}

═══════════════════════════════════════
📚 References Used ({len(source_docs)} documents):
{references}

📊 Total Library: {len(processed_documents)} documents
⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
    except Exception as e:
        return f"Error processing query: {str(e)}"

def clear_all():
    """Clear all documents and storage"""
    global processed_documents, processing_status, rag_storage_data
    count = len(processed_documents)
    processed_documents = {}
    processing_status = {}
    rag_storage_data = {}
    
    # Clear cache file
    if DOCUMENT_CACHE_PATH.exists():
        DOCUMENT_CACHE_PATH.unlink()
    
    # Note: We don't delete rag_storage folder to preserve original data
    # User can manually delete if needed
    
    return f"Cleared {count} documents from memory (RAG storage preserved)", []

def search_pdfs_by_keyword(keyword):
    """Search PDFs by filename keyword"""
    if not keyword:
        # Return all documents if no keyword
        all_docs = [[fname, ""] for fname in sorted(processed_documents.keys())][:10]
        return all_docs
    
    keyword_lower = keyword.lower()
    filtered = []
    for fname in sorted(processed_documents.keys()):
        if keyword_lower in fname.lower():
            filtered.append([fname, ""])
    
    return filtered[:10] if filtered else [["No matches found", ""]]

def preview_document(evt: gr.SelectData, doc_list_data):
    """Preview selected document"""
    # Handle DataFrame input from Gradio
    import pandas as pd
    
    if isinstance(doc_list_data, pd.DataFrame):
        if doc_list_data.empty or evt.index[0] >= len(doc_list_data):
            return "No document selected"
        selected_file = doc_list_data.iloc[evt.index[0], 0]
    elif isinstance(doc_list_data, list):
        if not doc_list_data or evt.index[0] >= len(doc_list_data):
            return "No document selected"
        selected_file = doc_list_data[evt.index[0]][0]
    else:
        return "No document selected"
    
    if selected_file == "No matches found":
        return "No document to preview"
    
    if selected_file in processed_documents:
        doc = processed_documents[selected_file]
        
        # Create HTML formatted preview that looks like a PDF document
        html_preview = f"""
        <div style='font-family: Georgia, serif; background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <div style='border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-bottom: 15px;'>
                <h3 style='color: #1a1a1a; margin: 0; font-size: 18px;'>📄 {selected_file}</h3>
                <div style='color: #666; font-size: 12px; margin-top: 5px;'>
                    <span>📅 {doc.get('processed_date', 'Unknown')}</span> | 
                    <span>📊 {len(doc.get('text', ''))} characters</span>
                </div>
            </div>
            
            <div style='background: #fafafa; padding: 15px; border-radius: 3px; margin-bottom: 15px;'>
                <h4 style='color: #333; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;'>Document Content</h4>
                <div style='color: #2c3e50; font-size: 13px; line-height: 1.6; text-align: justify;'>
        """
        
        # Format the text content
        text = doc.get('text', 'No content available')
        preview_text = text[:500] + "..." if len(text) > 500 else text
        
        # Convert line breaks to HTML and escape special characters
        preview_text = preview_text.replace('\n\n', '</p><p style="margin: 10px 0;">').replace('\n', '<br>')
        if not preview_text.startswith('<p'):
            preview_text = f"<p style='margin: 10px 0;'>{preview_text}</p>"
        
        html_preview += preview_text
        html_preview += """
                </div>
            </div>
        """
        
        # Add analysis summary if available
        if doc.get('analysis'):
            analysis = doc.get('analysis', '')
            # Extract key points
            points = []
            if "1. Main" in analysis:
                first_section = analysis.split("2.")[0] if "2." in analysis else analysis[:500]
                # Parse bullet points
                lines = first_section.split('\n')
                for line in lines[:5]:  # Show first 5 points
                    if line.strip().startswith('-'):
                        points.append(line.strip()[1:].strip())
            
            if points:
                html_preview += """
                <div style='background: #f0f8ff; padding: 15px; border-radius: 3px; border-left: 3px solid #4CAF50;'>
                    <h4 style='color: #333; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;'>Key Insights</h4>
                    <ul style='color: #2c3e50; font-size: 12px; line-height: 1.5; margin: 5px 0; padding-left: 20px;'>
                """
                for point in points:
                    html_preview += f"<li style='margin: 5px 0;'>{point}</li>"
                html_preview += """
                    </ul>
                </div>
                """
        
        html_preview += "</div>"
        return html_preview
    
    return "<div style='padding: 20px; color: #666; font-style: italic;'>Document not found in memory</div>"

def show_related_documents(selected_docs):
    """Show documents related to the selected one"""
    import pandas as pd
    
    # Handle DataFrame input
    if isinstance(selected_docs, pd.DataFrame):
        if selected_docs.empty:
            return [["Select a document first", ""]]
        selected_file = selected_docs.iloc[0, 0]
    elif isinstance(selected_docs, list):
        if not selected_docs or len(selected_docs) == 0:
            return [["Select a document first", ""]]
        selected_file = selected_docs[0][0] if isinstance(selected_docs[0], list) else selected_docs[0]
    else:
        return [["Select a document first", ""]]
    
    # Simple related document logic - you can enhance this
    # For now, show documents with similar naming patterns
    related = []
    if selected_file in processed_documents:
        # Extract number or pattern from filename
        numbers = re.findall(r'\d+', selected_file)
        
        for fname in processed_documents.keys():
            if fname != selected_file:
                # Check if they share common numbers or patterns
                fname_numbers = re.findall(r'\d+', fname)
                if any(num in fname_numbers for num in numbers):
                    related.append([fname, "Related"])
    
    return related[:5] if related else [["No related documents found", ""]]

def update_doc_relevance_after_query(query_result, current_docs):
    """Update document list with relevance scores based on query results"""
    if not query_result or not current_docs:
        return current_docs
    
    # Parse query result to find mentioned documents
    updated_docs = []
    for doc_row in current_docs:
        doc_name = doc_row[0]
        relevance = ""
        
        # Check if document is mentioned in query result
        if doc_name in query_result:
            relevance = "⭐ High"
        elif any(keyword in query_result.lower() for keyword in doc_name.lower().split('_')):
            relevance = "✓ Medium"
        
        updated_docs.append([doc_name, relevance])
    
    return updated_docs

def export_query_context(query, result, relevant_docs):
    """Export query context including question, answer, and relevant documents"""
    import pandas as pd
    
    # Handle DataFrame input
    if isinstance(relevant_docs, pd.DataFrame):
        relevant_list = []
        for idx, row in relevant_docs.iterrows():
            if len(row) > 1 and row[1]:  # Check if has relevance indicator
                relevant_list.append(row[0])
    else:
        relevant_list = [doc[0] for doc in relevant_docs if len(doc) > 1 and doc[1]]
    
    context = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "result": result,
        "relevant_documents": relevant_list
    }
    
    context_file = Path("query_context.json")
    with open(context_file, 'w') as f:
        json.dump(context, f, indent=2)
    
    # Return HTML formatted success message
    return f"""
    <div style='padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; color: #155724;'>
        <strong>✅ Context Exported Successfully!</strong><br>
        <span style='font-size: 12px;'>Saved to: {context_file}</span>
    </div>
    """

def get_library_status():
    """Get current library status - with dynamic sync"""
    # Re-sync with actual storage files
    load_existing_data()
    
    if not processed_documents:
        return "📚 Library is empty (no documents found in storage)", []
    
    data = []
    for fname, doc in processed_documents.items():
        text_len = len(doc.get('text', ''))
        size = f"{text_len//1000}k" if text_len > 0 else "N/A"
        date = doc.get('processed_date', 'Unknown')
        if date != 'Unknown':
            try:
                date = datetime.fromisoformat(date).strftime('%m/%d %H:%M')
            except:
                pass
        
        # Add source indicator
        source = "RAG" if doc.get('doc_id') else "Output" if fname.endswith('.pdf') else "New"
        data.append([fname, size, date, source])
    
    rag_status = "✅ Loaded" if rag_storage_data else "📁 Available" if RAG_STORAGE_PATH.exists() else "❌ Not found"
    
    summary = f"""📚 Documents: {len(processed_documents)}
🔗 RAG Storage: {rag_status}
💾 Location: {RAG_STORAGE_PATH.absolute() if RAG_STORAGE_PATH.exists() else 'Not initialized'}"""
    
    return summary, data

# Auto-initialize on startup
print("\n" + "="*60)
print("🚀 Initializing Transparency Tool...")
print("="*60)

connected = initialize_azure()
docs_loaded, has_rag = load_existing_data()

print(f"✅ Azure: {'Connected' if connected else 'Not connected'}")
print(f"📚 Documents: {docs_loaded} loaded")
print(f"🔗 RAG Storage: {'Found' if has_rag else 'Not found'}")
print("="*60)

# Create UI
with gr.Blocks(title="Transparency Tool for Product Launch", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🚀 Transparency Tool for Product Launch (AI Agents)")
    
    # Status bar
    with gr.Row():
        connection_status = gr.Textbox(
            value=f"✅ Azure | 📚 {docs_loaded} docs | {'🔗 RAG Loaded' if has_rag else '📁 No RAG'}" if connected else "❌ Not connected - Check .env",
            show_label=False,
            interactive=False,
            scale=4
        )
        reconnect_btn = gr.Button("🔄", scale=1)
        
    def reconnect():
        success = initialize_azure()
        docs, rag = load_existing_data()
        if success:
            return f"✅ Azure | 📚 {docs} docs | {'🔗 RAG Loaded' if rag else '📁 No RAG'}"
        return "❌ Connection failed - Check .env settings"
    
    reconnect_btn.click(reconnect, outputs=connection_status)
    
    with gr.Tabs():
        # Process Tab
        with gr.TabItem("📁 Process Documents"):
            with gr.Row():
                with gr.Column(scale=3):
                    files = gr.File(
                        label="Upload New Documents",
                        file_count="multiple",
                        file_types=[".pdf", ".txt", ".md", ".docx"]
                    )
                with gr.Column(scale=1):
                    merge_checkbox = gr.Checkbox(
                        label="Merge with existing",
                        value=True,
                        info="Keep existing docs"
                    )
            
            with gr.Row():
                process_btn = gr.Button("📤 Process Files", variant="primary", size="lg", scale=2)
                clear_btn = gr.Button("🗑️ Clear Memory", variant="stop", scale=1)
            
            with gr.Row():
                with gr.Column(scale=2):
                    process_log = gr.Textbox(
                        label="Processing Log",
                        lines=15,
                        interactive=False,
                        value=f"Ready to process new documents.\n{'📚 ' + str(docs_loaded) + ' existing documents loaded from storage.' if docs_loaded > 0 else 'No existing documents found.'}"
                    )
                
                with gr.Column(scale=1):
                    file_status = gr.Dataframe(
                        headers=["File", "Status"],
                        label="File Status",
                        value=[[f"Existing Docs", f"{docs_loaded} loaded"]] if docs_loaded > 0 else []
                    )
            
            process_btn.click(
                process_files,
                inputs=[files, merge_checkbox],
                outputs=[process_log, file_status]
            )
            
            clear_btn.click(
                clear_all,
                outputs=[process_log, file_status]
            )
        
        # Query Tab with Enhanced Visualization
        with gr.TabItem("🔍 Query Knowledge Base"):
            if docs_loaded > 0:
                gr.Info(f"📚 {docs_loaded} documents ready for queries from existing RAG storage")
            
            with gr.Row():
                # Left side: Query interface
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="Enter Your Question",
                        placeholder="What are the main risks in the product launch?",
                        lines=2
                    )
                    
                    with gr.Row():
                        query_mode = gr.Radio(
                            choices=["hybrid", "local", "global", "naive"],
                            value="hybrid",
                            label="Query Mode",
                            info="Hybrid: Best overall | Local: Specific details | Global: Themes | Naive: Keywords",
                            scale=3
                        )
                        query_btn = gr.Button("🔍 Search", variant="primary", scale=1)
                    
                    query_output = gr.Textbox(
                        label="Answer with References",
                        lines=20,
                        interactive=False,
                        value="Enter a question above to search the knowledge base." if docs_loaded > 0 else "No documents loaded. Please process documents first."
                    )
                
                # Right side: Document visualization and search
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Document Explorer")
                    
                    # PDF search box
                    pdf_search = gr.Textbox(
                        label="Search PDFs by filename",
                        placeholder="Type to filter PDFs...",
                        lines=1
                    )
                    
                    # Document list with visualization
                    doc_list = gr.Dataframe(
                        headers=["📄 Document", "📊 Relevance"],
                        value=[[fname, ""] for fname in sorted(processed_documents.keys())][:10] if processed_documents else [],
                        interactive=False,
                        height=200
                    )
                    
                    # Selected document preview
                    with gr.Accordion("📖 Document Preview", open=False):
                        selected_doc_info = gr.HTML(
                            value="<div style='padding: 10px; background: #f8f9fa; border-radius: 5px; font-family: Arial, sans-serif;'><p style='color: #666;'>Click on a document to preview</p></div>"
                        )
                    
                    # Visualization controls
                    with gr.Row():
                        show_related_btn = gr.Button("🔗 Show Related", size="sm")
                        export_context_btn = gr.Button("💾 Export Context", size="sm")
            
            gr.Examples(
                examples=[
                    ["What are the main risks in the product launch?"],
                    ["What is the timeline for key milestones?"],
                    ["Who are the key stakeholders involved?"],
                    ["What are the success metrics?"],
                    ["What dependencies exist between teams?"],
                    ["What are the technical requirements?"],
                    ["What is the budget allocation?"],
                ],
                inputs=query_input
            )
            
            # Enhanced query with document relevance update
            def query_and_update_relevance(query, mode):
                result = query_documents(query, mode)
                # After getting result, update document relevance
                return result
            
            query_btn.click(
                query_and_update_relevance,
                inputs=[query_input, query_mode],
                outputs=query_output
            ).then(
                update_doc_relevance_after_query,
                inputs=[query_output, doc_list],
                outputs=doc_list
            )
            
            # PDF search functionality
            pdf_search.change(
                search_pdfs_by_keyword,
                inputs=pdf_search,
                outputs=doc_list
            )
            
            # Document selection for preview
            doc_list.select(
                preview_document,
                inputs=doc_list,
                outputs=selected_doc_info
            )
            
            # Show related documents
            show_related_btn.click(
                show_related_documents,
                inputs=doc_list,
                outputs=doc_list
            )
            
            # Export context
            export_context_btn.click(
                export_query_context,
                inputs=[query_input, query_output, doc_list],
                outputs=selected_doc_info
            )
        
        # Library Tab
        with gr.TabItem("📚 Document Library"):
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh", scale=1)
                export_btn = gr.Button("📥 Export Metadata", scale=1)
                stats_btn = gr.Button("📊 Statistics", scale=1)
            
            lib_summary = gr.Textbox(
                label="Library Status", 
                lines=3, 
                interactive=False
            )
            
            lib_table = gr.Dataframe(
                headers=["Document", "Size", "Date", "Source"],
                label="Document Library",
                interactive=False
            )
            
            def export_metadata():
                if not processed_documents:
                    return "No documents to export"
                
                export_data = {
                    "export_date": datetime.now().isoformat(),
                    "total_documents": len(processed_documents),
                    "has_rag_storage": bool(rag_storage_data),
                    "documents": []
                }
                
                for fname, doc in processed_documents.items():
                    export_data["documents"].append({
                        "filename": fname,
                        "analysis": doc.get("analysis", ""),
                        "text_length": len(doc.get("text", "")),
                        "processed_date": doc.get("processed_date", ""),
                        "source": "rag_storage" if doc.get("doc_id") else "uploaded"
                    })
                
                export_path = Path("library_export.json")
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                return f"✅ Exported {len(processed_documents)} documents to library_export.json"
            
            def show_statistics():
                if not processed_documents:
                    return "No documents to analyze"
                
                total_chars = sum(len(doc.get('text', '')) for doc in processed_documents.values())
                avg_chars = total_chars // len(processed_documents) if processed_documents else 0
                
                from_rag = sum(1 for doc in processed_documents.values() if doc.get('doc_id'))
                from_upload = len(processed_documents) - from_rag
                
                stats = f"""📊 Library Statistics:
━━━━━━━━━━━━━━━━━━━━━
📄 Total Documents: {len(processed_documents)}
📁 From RAG Storage: {from_rag}
📤 From Uploads: {from_upload}
📝 Total Text: {total_chars:,} characters
📈 Average Size: {avg_chars:,} chars/doc
💾 Storage Path: {RAG_STORAGE_PATH.absolute()}
"""
                return stats
            
            refresh_btn.click(get_library_status, outputs=[lib_summary, lib_table])
            export_btn.click(export_metadata, outputs=lib_summary)
            stats_btn.click(show_statistics, outputs=lib_summary)
            
            # Auto-refresh on tab selection
            demo.load(get_library_status, outputs=[lib_summary, lib_table])

if __name__ == "__main__":
    print(f"\n🌐 URL: http://127.0.0.1:7861")
    print("="*60 + "\n")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True
    )