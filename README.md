# Transparency Tool for Product Launch (AI Agents)

Multi-file document processing and querying system for product launch transparency using Azure OpenAI.

## Quick Start

### 1. Install
```bash
git clone https://github.com/HKUDS/RAG-Anything.git
cd RAG-Anything
pip install -r requirements.txt
```

### 2. Configure
```bash
cp .env.sample .env
# Edit .env with your Azure OpenAI credentials
```

Required in `.env`:
- `LLM_BINDING_HOST` - Azure OpenAI endpoint
- `LLM_BINDING_API_KEY` - API key
- `AZURE_OPENAI_DEPLOYMENT` - GPT-4 deployment name
- `EMBEDDING_BINDING_HOST` - Embedding endpoint
- `EMBEDDING_BINDING_API_KEY` - Embedding API key
- `AZURE_EMBEDDING_DEPLOYMENT` - Embedding deployment name

### 3. Run
```bash
python transparency_tool_product_launch.py
```
Opens at: http://127.0.0.1:7861

## Features

- **Multi-file Upload** - Process multiple PDFs, DOCX, TXT files at once
- **Azure GPT-4 Analysis** - Extract key information from documents
- **Query Interface** - Ask questions across all documents
- **Real-time Status** - Track processing progress

## Usage

1. **Upload** - Drag & drop multiple files
2. **Process** - Click "Process with Azure GPT-4"
3. **Query** - Ask questions about your documents
4. **Get Answers** - Receive AI-generated responses

## Supported Files

- PDF
- DOCX/DOC
- TXT/MD

## Query Modes

- **Hybrid** (recommended) - Best overall results
- **Local** - Specific document details
- **Global** - Overall themes
- **Naive** - Keyword search

## Requirements

- Python 3.9+
- Azure OpenAI account with:
  - GPT-4 deployment
  - text-embedding-3-large deployment

## Troubleshooting

**Port in use:**
```bash
lsof -t -i:7861 | xargs kill -9
```

**Azure errors:**
- Check API keys in `.env`
- Verify deployment names
- Check API quotas

## Project Structure

```
transparency_tool_product_launch.py   # Main application
.env                                   # Your credentials (not in git)
.env.sample                            # Template
requirements.txt                       # Dependencies
raganything/                          # Core library
```

## Links

- [Original Repository](https://github.com/HKUDS/RAG-Anything)
- [LightRAG](https://github.com/HKUDS/LightRAG)
- [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)