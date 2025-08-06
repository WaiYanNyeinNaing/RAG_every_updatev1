# RAG-Anything Setup Guide

## Overview
RAG-Anything is a multimodal extension of LightRAG that enables processing of various document types including images, PDFs, office documents, and more.

## Setup Summary

### 1. Environment Configuration
- Cloned RAG-Anything repository into: `/Users/waiyan/Downloads/GraphRAG/LightRAG/RAG-Anything`
- Created new git branch: `rag-anything-multimodal`
- Copied existing `.env` file from LightRAG with Azure OpenAI configuration

### 2. Key Configuration Settings

#### Azure OpenAI Configuration (Already Set)
- **LLM Model**: GPT-4 (Azure deployment)
- **Embedding Model**: text-embedding-3-large
- **Endpoints**: Azure OpenAI endpoints configured

#### RAG-Anything Specific Settings Added
```env
### RAGAnything Configuration (Multimodal Document Processing)
PARSE_METHOD=auto
OUTPUT_DIR=./output
PARSER=mineru
DISPLAY_CONTENT_STATS=true

### Multimodal Processing Configuration
ENABLE_IMAGE_PROCESSING=true
ENABLE_TABLE_PROCESSING=true
ENABLE_EQUATION_PROCESSING=true

### Batch Processing Configuration
MAX_CONCURRENT_FILES=1
SUPPORTED_FILE_EXTENSIONS=.pdf,.jpg,.jpeg,.png,.bmp,.tiff,.tif,.gif,.webp,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md
RECURSIVE_FOLDER_PROCESSING=true

### Context Extraction Configuration
CONTEXT_WINDOW=1
CONTEXT_MODE=page
MAX_CONTEXT_TOKENS=2000
INCLUDE_HEADERS=true
INCLUDE_CAPTIONS=true
CONTEXT_FILTER_CONTENT_TYPES=text
CONTENT_FORMAT=minerU
```

### 3. Virtual Environment
- Created Python 3.10 virtual environment: `venv_rag_anything`
- Installed dependencies including:
  - MinerU 2.0 (document parsing)
  - LightRAG-HKU
  - Hugging Face Hub
  - Various multimodal processing libraries

### 4. Directory Structure
```
RAG-Anything/
├── .env                    # Configuration file (copied from LightRAG)
├── venv_rag_anything/      # Python 3.10 virtual environment
├── raganything/            # Main package directory
├── examples/               # Example scripts
├── docs/                   # Documentation
└── output/                 # Parsed document output directory
```

## Usage

### Activate Environment
```bash
cd RAG-Anything
source venv_rag_anything/bin/activate
```

### Process Multimodal Documents
```python
from raganything import RAGAnything

# Initialize with Azure OpenAI configuration from .env
rag = RAGAnything()

# Process various file types
rag.process_document("path/to/image.jpg")
rag.process_document("path/to/document.pdf")
rag.process_document("path/to/presentation.pptx")
```

### Batch Processing
```python
# Process entire directory
rag.batch_process("path/to/documents/")
```

## Key Features
1. **Multimodal Support**: Images, PDFs, Office documents, text files
2. **Table & Equation Processing**: Extract structured data
3. **Context-Aware Processing**: Maintains document context
4. **Azure OpenAI Integration**: Uses existing LightRAG configuration
5. **Batch Processing**: Process multiple files efficiently

## Next Steps
1. Test with sample multimodal files
2. Integrate with existing LightRAG workflow
3. Create custom processing pipelines for specific document types