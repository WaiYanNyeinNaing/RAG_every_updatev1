# Azure OpenAI Setup for RAG-Anything

This guide explains how to use RAG-Anything with Azure OpenAI for multimodal document processing.

## ✅ Current Status

RAG-Anything is now fully working with Azure OpenAI! You can process multimodal documents (PDFs, images, tables, equations) and query them using Azure-hosted GPT-4 and embedding models.

## 🚀 Quick Start

1. **Run the example script:**
   ```bash
   source venv_rag_anything/bin/activate
   python example_azure_openai.py
   ```

2. **Process your own documents:**
   ```python
   from raganything import RAGAnything, RAGAnythingConfig
   from azure_openai_wrappers import create_azure_llm_func, create_azure_embedding_func
   
   # Initialize
   rag = RAGAnything(
       config=RAGAnythingConfig(working_dir="./rag_storage"),
       llm_model_func=create_azure_llm_func(),
       embedding_func=create_azure_embedding_func()
   )
   
   # Process document
   await rag.process_document_complete("your_document.pdf")
   
   # Query
   result = await rag.aquery("What is this document about?")
   ```

## 🔧 Configuration

### Required Environment Variables

Add these to your `.env` file:

```env
# Azure OpenAI LLM Configuration
LLM_BINDING_API_KEY=your-azure-openai-api-key
LLM_BINDING_HOST=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4.1

# Azure OpenAI Embedding Configuration
EMBEDDING_BINDING_API_KEY=your-azure-openai-api-key
EMBEDDING_BINDING_HOST=https://your-resource.cognitiveservices.azure.com/
AZURE_EMBEDDING_API_VERSION=2024-12-01-preview
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-large
EMBEDDING_DIM=3072
```

## 📁 Key Files

- **`azure_openai_wrappers.py`**: Contains the Azure OpenAI wrapper functions
  - `create_azure_llm_func()`: Creates LLM function for text generation
  - `create_azure_embedding_func()`: Creates embedding function
  - `create_azure_vision_func()`: Creates vision function for image analysis

- **`example_azure_openai.py`**: Complete working example showing document processing and querying

- **`test_raganything_azure.py`**: Test script that verifies the Azure integration

## 🛠️ Technical Details

### The Challenge
The standard LightRAG expects OpenAI-style API calls, but Azure OpenAI requires:
- Different client initialization (AsyncAzureOpenAI)
- API version parameter
- Azure endpoint format
- Deployment names instead of model names

### The Solution
We created wrapper functions that:
1. Initialize proper Azure OpenAI clients
2. Handle Azure-specific parameters
3. Provide the same interface that LightRAG expects
4. Include response caching for efficiency

### Architecture
```
RAG-Anything
    ↓
Azure Wrapper Functions
    ↓
AsyncAzureOpenAI Client
    ↓
Azure OpenAI Service
```

## 🎯 Features Working

- ✅ Document parsing with MinerU 2.0
- ✅ Text extraction and processing
- ✅ Table extraction and analysis
- ✅ Equation/formula processing
- ✅ Image analysis (when using GPT-4V)
- ✅ Hybrid search (semantic + keyword)
- ✅ Multi-modal queries
- ✅ Response caching

## ⚠️ Known Limitations

1. **DocProcessingStatus Issue**: The current version of RAG-Anything tries to add a `multimodal_processed` field that's not in the LightRAG schema. This doesn't affect functionality but may show warnings.

2. **Reranking**: Reranking is not configured. Use `enable_rerank=False` in queries to avoid warnings.

## 📊 Performance Tips

1. **Batch Processing**: Process multiple documents concurrently:
   ```python
   await rag.process_folder_complete("./documents_folder")
   ```

2. **Query Optimization**: Use specific query modes:
   - `"hybrid"`: Best for most queries (combines semantic and keyword search)
   - `"local"`: Faster, focuses on entity relationships
   - `"global"`: Comprehensive but slower

3. **Caching**: Responses are automatically cached to reduce API calls

## 🔍 Troubleshooting

### "api_version parameter" error
- Make sure you're using the provided `azure_openai_wrappers.py`
- Don't use the standard OpenAI functions directly

### 404 Resource not found
- Check your Azure endpoint URL format
- Verify deployment names match your Azure setup

### Import errors
- Ensure you're in the correct virtual environment: `source venv_rag_anything/bin/activate`

## 📚 Next Steps

1. **Process Different Document Types**:
   - PDFs: Fully supported with layout preservation
   - Images: Supported with vision models
   - Office docs: Convert to PDF first

2. **Customize Processing**:
   ```python
   config = RAGAnythingConfig(
       chunk_token_size=1200,  # Adjust chunk size
       max_context_tokens=8000,  # Increase context window
       enable_table_processing=True,
       enable_equation_processing=True
   )
   ```

3. **Advanced Queries**:
   - Use `aquery_with_multimodal()` for queries that need visual context
   - Combine multiple documents into a single knowledge base

## 🎉 Success!

You now have a fully functional multimodal RAG system powered by Azure OpenAI! The system can process complex documents and answer questions using both text and visual understanding.