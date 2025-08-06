#!/usr/bin/env python
"""
Test script to verify Gradio UI query functionality via HTTP
"""

import requests
import json

# Gradio API endpoint
GRADIO_URL = "http://localhost:7860"

def test_query_endpoint():
    """Test the query endpoint of the Gradio UI"""
    
    # Test questions
    test_questions = [
        "What is this document about?",
        "What are the main features mentioned?"
    ]
    
    for question in test_questions:
        print(f"\nTesting query: {question}")
        print("-" * 60)
        
        try:
            # Make request to Gradio predict endpoint
            response = requests.post(
                f"{GRADIO_URL}/api/predict",
                json={
                    "fn_index": 4,  # Index for query_documents function
                    "data": [question]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Answer: {result.get('data', ['No data'])[0][:200]}...")
            else:
                print(f"Error: HTTP {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"Error connecting to Gradio UI: {e}")

if __name__ == "__main__":
    print("Testing Gradio UI Query Functionality")
    print("=" * 60)
    test_query_endpoint()