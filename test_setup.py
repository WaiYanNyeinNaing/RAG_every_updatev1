#!/usr/bin/env python
"""
Simple test script to verify RAG-Anything setup with Azure OpenAI
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

print("RAG-Anything Setup Test")
print("=" * 50)

# Test 1: Check Python version
print(f"Python Version: {sys.version}")

# Test 2: Check imports
try:
    import raganything
    print("✓ RAGAnything package imported successfully")
except ImportError as e:
    print(f"✗ Failed to import RAGAnything: {e}")

try:
    import lightrag
    print("✓ LightRAG package imported successfully")
except ImportError as e:
    print(f"✗ Failed to import LightRAG: {e}")

try:
    import mineru
    print("✓ MinerU package imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MinerU: {e}")

# Test 3: Check environment variables
print("\nEnvironment Configuration:")
print(f"- LLM Binding: {os.getenv('LLM_BINDING', 'Not set')}")
print(f"- LLM Model: {os.getenv('LLM_MODEL', 'Not set')}")
print(f"- LLM Host: {os.getenv('LLM_BINDING_HOST', 'Not set')[:50]}...")
print(f"- Embedding Binding: {os.getenv('EMBEDDING_BINDING', 'Not set')}")
print(f"- Embedding Model: {os.getenv('EMBEDDING_MODEL', 'Not set')}")
print(f"- Working Directory: {os.getenv('WORKING_DIR', 'Not set')}")

# Test 4: Check RAG-Anything specific settings
print("\nRAG-Anything Settings:")
print(f"- Parser: {os.getenv('PARSER', 'Not set')}")
print(f"- Parse Method: {os.getenv('PARSE_METHOD', 'Not set')}")
print(f"- Image Processing: {os.getenv('ENABLE_IMAGE_PROCESSING', 'Not set')}")
print(f"- Table Processing: {os.getenv('ENABLE_TABLE_PROCESSING', 'Not set')}")
print(f"- Equation Processing: {os.getenv('ENABLE_EQUATION_PROCESSING', 'Not set')}")

# Test 5: Check directories
print("\nDirectory Structure:")
working_dir = os.getenv('WORKING_DIR', './rag_storage')
output_dir = os.getenv('OUTPUT_DIR', './output')

print(f"- Working Directory: {os.path.abspath(working_dir)} (exists: {os.path.exists(working_dir)})")
print(f"- Output Directory: {os.path.abspath(output_dir)} (exists: {os.path.exists(output_dir)})")

# Test 6: Try to initialize RAGAnything config
try:
    from raganything import RAGAnythingConfig
    config = RAGAnythingConfig()
    print("\n✓ RAGAnythingConfig initialized successfully")
    print(f"  - Parser: {config.parser}")
    print(f"  - Parse Method: {config.parse_method}")
    print(f"  - Multimodal Processing Enabled: Image={config.enable_image_processing}, Table={config.enable_table_processing}, Equation={config.enable_equation_processing}")
except Exception as e:
    print(f"\n✗ Failed to initialize RAGAnythingConfig: {e}")

print("\n" + "=" * 50)
print("Setup test completed!")