#!/usr/bin/env python
"""
Simple test to verify RAG-Anything can parse documents
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env", override=False)

# Import RAG-Anything components
from raganything import RAGAnythingConfig
from raganything.parser import MineruParser

def test_parsing():
    """Test document parsing with MinerU"""
    
    print("Testing MinerU Parser...")
    
    # Create configuration
    config = RAGAnythingConfig(
        parser="mineru",
        parse_method="auto",
        parser_output_dir="./output",
        display_content_stats=True
    )
    
    # Initialize parser (MineruParser doesn't take config in __init__)
    parser = MineruParser()
    
    # Parse the test document
    test_file = "test_document.md"
    print(f"\nParsing document: {test_file}")
    
    try:
        result = parser.parse_document(
            file_path=test_file,
            output_dir="./output",
            method="auto"  # Changed from parse_method to method
        )
        
        # Check if result is a tuple or just content_list
        if isinstance(result, tuple):
            content_list, doc_id = result
        else:
            content_list = result
            doc_id = "unknown"
        
        print(f"\nParsing completed!")
        print(f"Document ID: {doc_id}")
        print(f"Number of content blocks: {len(content_list)}")
        
        # Display content types
        content_types = {}
        for item in content_list:
            content_type = item.get('type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        print("\nContent types found:")
        for content_type, count in content_types.items():
            print(f"  - {content_type}: {count}")
        
        # Show first few content items
        print("\nFirst 3 content items:")
        for i, item in enumerate(content_list[:3]):
            print(f"\n{i+1}. Type: {item.get('type', 'unknown')}")
            if 'text' in item:
                print(f"   Text: {item['text'][:100]}...")
            if 'table_data' in item:
                print(f"   Table: {len(item['table_data'])} rows")
            if 'latex' in item:
                print(f"   LaTeX: {item['latex'][:50]}...")
                
    except Exception as e:
        print(f"\nError during parsing: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    print("RAG-Anything Parsing Test")
    print("=" * 50)
    
    # Run test
    test_parsing()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()