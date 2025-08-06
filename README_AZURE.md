# RAG-Anything with Azure OpenAI 🚀

A powerful multimodal RAG (Retrieval-Augmented Generation) system with Gradio UI, optimized for Azure OpenAI integration. Process and query documents with advanced multimodal understanding capabilities.

## 🌟 Features

- **Multimodal Document Processing**: Supports PDFs, Word docs, images, tables, and equations
- **Azure OpenAI Integration**: Seamless integration with Azure's GPT-4 and text-embedding models
- **Interactive Gradio UI**: User-friendly web interface for document upload and querying
- **Smart Query Handling**: Automatic timeout management and query optimization
- **Real-time Monitoring**: Built-in monitoring tools for debugging and performance tracking
- **Flexible Parsers**: Support for MinerU and Docling parsers

## 📋 Prerequisites

- Python 3.10+
- Azure OpenAI subscription with:
  - GPT-4 or GPT-4-Turbo deployment
  - text-embedding-3-large deployment
  - (Optional) GPT-4V for vision capabilities

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd RAG-Anything

# Create virtual environment
python3 -m venv venv_rag_anything
source venv_rag_anything/bin/activate  # On Windows: venv_rag_anything\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# If LightRAG is in parent directory
pip install -e ..
```

### 2. Configure Azure OpenAI

```bash
# Copy the sample environment file
cp .env.sample .env

# Edit .env with your Azure credentials
nano .env  # or use your preferred editor
```

Required Azure configurations:
- `LLM_BINDING_API_KEY`: Your Azure OpenAI API key
- `LLM_BINDING_HOST`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT`: Your GPT-4 deployment name
- `EMBEDDING_BINDING_API_KEY`: Your embedding API key
- `EMBEDDING_BINDING_HOST`: Your embedding endpoint
- `AZURE_EMBEDDING_DEPLOYMENT`: Your embedding deployment name

### 3. Run the Application

```bash
# Using the startup script (recommended)
./run_gradio.sh

# Or manually
source venv_rag_anything/bin/activate
python gradio_ui.py
```

Access the UI at: **http://localhost:7860**

## 📁 Project Structure

```
RAG-Anything/
├── gradio_ui.py              # Main Gradio interface
├── azure_openai_wrappers.py  # Azure OpenAI integration
├── raganything/              # Core RAG implementation
│   ├── __init__.py
│   ├── raganything.py        # Main RAG class
│   ├── query.py              # Query handling
│   ├── processor.py          # Document processing
│   └── modalprocessors.py    # Multimodal processors
├── run_gradio.sh             # Startup script
├── monitor_gradio.py         # Real-time monitoring
├── .env.sample               # Environment template
├── requirements.txt          # Python dependencies
└── rag_ui_storage/           # Document storage (created at runtime)
```

## 💡 Usage Guide

### Processing Documents

1. **Upload Document**: Use the "Upload & Process" tab
2. **Select File**: Choose PDF, DOCX, MD, or image files
3. **Process**: Click "Process Document" and wait for completion
4. **Or Use Sample**: Click "Process output/product.pdf" for testing

### Querying Documents

1. **Enter Question**: Type your query in the text box
2. **Adjust Timeout**: Use slider for complex queries (10-120 seconds)
3. **Submit**: Click "Submit Query" or use example questions
4. **View Results**: Results appear in the answer box

### Query Performance Tips

**Fast Queries (< 5 seconds)**
- Simple facts: "What is the product name?"
- Direct lookups: "What is the temperature range?"

**Medium Queries (5-30 seconds)**
- Comparisons: "Compare the sensor types"
- Multi-part: "List benefits and specifications"

**Complex Queries (30+ seconds)**
- Analysis: "Analyze all technical differences"
- Comprehensive: "Provide complete overview"

## 🔧 Advanced Configuration

### Query Modes

The system automatically selects the best mode:
- `bypass`: Simple greetings/tests (fastest)
- `local`: Entity-specific queries
- `global`: Document-wide questions
- `hybrid`: Comprehensive answers (default)

### Timeout Settings

Adjust in the UI or modify defaults in `gradio_ui.py`:
```python
async def query_async(question, timeout_seconds=60):  # Change default
```

### Debug Mode

Enable verbose logging:
```python
# In gradio_ui.py
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring

Run the monitor in a separate terminal:
```bash
python monitor_gradio.py
```

Shows:
- 🔵 New queries
- ✅ Successful completions
- ⏱️ Timeouts
- 🔴 Errors
- ⚠️ Slow queries

## 🐛 Troubleshooting

### Query Timeouts
- Increase timeout slider
- Simplify query
- Check Azure connection: `python test_azure_connection.py`

### No Results
- Ensure documents are processed first
- Check `rag_ui_storage/` has data
- Verify Azure credentials

### Connection Issues
```bash
# Test Azure connection
python test_azure_connection.py

# Check logs
tail -f gradio_ui.log

# Restart service
pkill -f "gradio_ui.py"
./run_gradio.sh
```

## 🧪 Testing

```bash
# Test Azure OpenAI connection
python test_azure_connection.py

# Test query functionality
python test_query_direct.py

# Test simple queries
python test_gradio_simple.py
```

## 📝 Environment Variables

See `.env.sample` for complete list. Key variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_BINDING_API_KEY` | Azure OpenAI API key | `sk-...` |
| `LLM_BINDING_HOST` | Azure endpoint | `https://xxx.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | GPT-4 deployment | `gpt-4` |
| `EMBEDDING_DIM` | Embedding dimension | `3072` |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built on [LightRAG](https://github.com/HKUDS/LightRAG)
- Uses [MinerU](https://github.com/opendatalab/MinerU) for PDF parsing
- Powered by Azure OpenAI

## 📞 Support

- Create an issue for bugs
- Check logs: `gradio_ui.log`
- Monitor performance: `python monitor_gradio.py`

---

**Note**: This is an Azure-optimized implementation. For other LLM providers, modify the wrapper functions in `azure_openai_wrappers.py`.