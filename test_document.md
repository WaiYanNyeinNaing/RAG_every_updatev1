# RAG-Anything Test Document

## Overview
This is a test document to demonstrate RAG-Anything's multimodal capabilities.

## Key Features

### 1. Text Processing
RAG-Anything can process regular text content and extract entities and relationships.

### 2. Table Processing
Here's a sample performance comparison table:

| Method | Accuracy | Processing Time | Memory Usage |
|--------|----------|-----------------|--------------|
| RAG-Anything | 95.2% | 120ms | 2.1GB |
| Traditional RAG | 87.3% | 180ms | 1.8GB |
| Baseline | 82.1% | 200ms | 1.5GB |

### 3. Mathematical Equations
The F1-score is calculated using the formula:

$$F1 = 2 \cdot \frac{precision \cdot recall}{precision + recall}$$

### 4. Code Snippets
```python
from raganything import RAGAnything

# Initialize RAG
rag = RAGAnything()

# Process document
result = await rag.process_document("document.pdf")
```

## Conclusion
RAG-Anything provides comprehensive multimodal document processing capabilities, making it ideal for complex document analysis tasks.