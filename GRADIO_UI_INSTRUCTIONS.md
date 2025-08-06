# RAG-Anything Gradio UI - Quick Start Guide

## 🚀 Running the Gradio UI

### Method 1: Using the startup script (Recommended)

Open a new terminal and run:
```bash
cd /Users/waiyan/Downloads/GraphRAG/LightRAG/RAG-Anything
./run_gradio.sh
```

This script will:
- Check and activate the virtual environment
- Verify environment variables
- Kill any existing instances
- Start the Gradio UI with proper logging

### Method 2: Manual startup

```bash
cd /Users/waiyan/Downloads/GraphRAG/LightRAG/RAG-Anything
source venv_rag_anything/bin/activate
python gradio_ui.py
```

### Method 3: Run in background

```bash
cd /Users/waiyan/Downloads/GraphRAG/LightRAG/RAG-Anything
source venv_rag_anything/bin/activate
nohup python gradio_ui.py > gradio_ui.log 2>&1 &
```

## 📊 Monitoring the UI

To monitor the UI in real-time (in a separate terminal):
```bash
cd /Users/waiyan/Downloads/GraphRAG/LightRAG/RAG-Anything
python monitor_gradio.py
```

This will show:
- 🔵 New queries
- ✅ Successful completions
- ⏱️ Timeouts
- 🔴 Errors
- ⚠️ Slow queries (>10 seconds)

## 🔧 Troubleshooting Slow/Hanging Queries

### Common Issues and Solutions:

1. **Query takes too long or doesn't respond**
   - Increase the timeout slider in the UI (default: 60 seconds)
   - Try simpler queries first
   - Check if Azure OpenAI is responding: `python test_azure_connection.py`

2. **"No documents have been processed" error**
   - Process a document first using the "Upload & Process" tab
   - Or use the "Process output/product.pdf" button for the sample document

3. **Complex queries timing out**
   - Break down complex questions into simpler ones
   - Use "bypass" mode for simple queries by including words like "hello" or "test"
   - Increase timeout to 120 seconds for very complex queries

4. **Check if the service is running**
   ```bash
   # Check if Gradio UI is running
   ps aux | grep gradio_ui.py
   
   # Check if port 7860 is in use
   lsof -i :7860
   ```

5. **View recent logs**
   ```bash
   tail -f gradio_ui.log
   ```

## 📝 Query Tips for Better Performance

### Fast Queries (< 5 seconds)
- Simple factual questions: "What is the product name?"
- Direct lookups: "What is the temperature range?"
- Basic summaries: "List the main features"

### Medium Queries (5-30 seconds)
- Comparative questions: "Compare the active and inductive sensors"
- Multi-part questions: "What are the benefits and specifications?"
- Context-aware questions: "Explain the mounting options"

### Slow Queries (30+ seconds)
- Complex analysis: "Analyze all technical differences between all sensor types"
- Full document summaries: "Provide a comprehensive overview of everything"
- Multiple relationships: "How do all components interact with each other?"

## 🛠️ Advanced Configuration

### Adjusting Timeouts Programmatically
Edit `gradio_ui.py` and modify the default timeout:
```python
async def query_async(question, timeout_seconds=60):  # Change 60 to your preferred default
```

### Changing Query Modes
The UI automatically selects the best mode, but you can force a specific mode in the code:
- `"bypass"` - For simple greetings/tests (fastest)
- `"local"` - For entity-specific queries
- `"global"` - For document-wide questions
- `"hybrid"` - For comprehensive answers (default, slowest)

### Debug Mode
To enable verbose logging, edit `gradio_ui.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Change INFO to DEBUG
```

## 🔄 Restarting the Service

If the UI becomes unresponsive:
```bash
# Kill the process
pkill -f "gradio_ui.py"

# Wait a moment
sleep 2

# Restart
./run_gradio.sh
```

## 📍 Access Points

- **Web Interface**: http://localhost:7860
- **Log File**: `gradio_ui.log`
- **Storage Directory**: `./rag_ui_storage/`

## ⚡ Performance Optimization

1. **Pre-process documents** during off-peak hours
2. **Use appropriate query modes** for your questions
3. **Keep questions focused** rather than overly broad
4. **Monitor the logs** to identify patterns in slow queries
5. **Adjust timeout** based on your typical query complexity

---

For more help, check the logs or run the test scripts:
- `python test_azure_connection.py` - Test Azure OpenAI connection
- `python test_query_direct.py` - Test query functionality directly
- `python test_gradio_simple.py` - Test simple queries