"""
Azure OpenAI wrapper functions for LightRAG compatibility
"""

import os
from openai import AsyncAzureOpenAI
from lightrag.utils import EmbeddingFunc
import hashlib
import json
from typing import List, Optional, Dict, Any

# Global cache for responses
_response_cache = {}

def create_azure_llm_func():
    """Create Azure OpenAI LLM function compatible with LightRAG"""
    
    # Get Azure configuration
    api_key = os.getenv("LLM_BINDING_API_KEY")
    azure_endpoint = os.getenv("LLM_BINDING_HOST")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    
    # Create Azure OpenAI client
    client = AsyncAzureOpenAI(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version
    )
    
    async def llm_model_func(
        prompt: str, 
        system_prompt: Optional[str] = None, 
        history_messages: List[Dict[str, str]] = [], 
        **kwargs
    ) -> str:
        """Azure OpenAI completion function compatible with LightRAG"""
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add history messages
        for msg in history_messages:
            messages.append(msg)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Create cache key
        cache_key = hashlib.md5(
            json.dumps({"model": deployment, "messages": messages}, sort_keys=True).encode()
        ).hexdigest()
        
        # Check cache
        if cache_key in _response_cache:
            return _response_cache[cache_key]
        
        # Extract relevant kwargs
        temperature = kwargs.get("temperature", 0)
        max_tokens = kwargs.get("max_tokens", 4000)
        top_p = kwargs.get("top_p", 1.0)
        
        # Make API call
        response = await client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        
        result = response.choices[0].message.content
        
        # Cache response
        _response_cache[cache_key] = result
        
        return result
    
    return llm_model_func

def create_azure_embedding_func():
    """Create Azure OpenAI embedding function compatible with LightRAG"""
    
    # Get Azure configuration
    api_key = os.getenv("EMBEDDING_BINDING_API_KEY")
    azure_endpoint = os.getenv("EMBEDDING_BINDING_HOST")
    api_version = os.getenv("AZURE_EMBEDDING_API_VERSION")
    deployment = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    embedding_dim = int(os.getenv("EMBEDDING_DIM", "3072"))
    
    # Create Azure OpenAI client
    client = AsyncAzureOpenAI(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version
    )
    
    async def embed_func(texts: List[str]) -> List[List[float]]:
        """Azure OpenAI embedding function"""
        
        # Make API call
        response = await client.embeddings.create(
            model=deployment,
            input=texts
        )
        
        # Extract embeddings
        embeddings = [item.embedding for item in response.data]
        
        return embeddings
    
    # Return as EmbeddingFunc
    return EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=8192,
        func=embed_func
    )

def create_azure_vision_func():
    """Create Azure OpenAI vision function compatible with LightRAG"""
    
    # Get Azure configuration
    api_key = os.getenv("LLM_BINDING_API_KEY")
    azure_endpoint = os.getenv("LLM_BINDING_HOST")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    
    # Create Azure OpenAI client
    client = AsyncAzureOpenAI(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version=api_version
    )
    
    async def vision_model_func(
        prompt: str, 
        system_prompt: Optional[str] = None, 
        history_messages: List[Dict[str, str]] = [], 
        image_data: Optional[str] = None,
        **kwargs
    ) -> str:
        """Azure OpenAI vision function compatible with LightRAG"""
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add history messages
        for msg in history_messages:
            messages.append(msg)
        
        # Add current prompt with image if provided
        if image_data:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})
        
        # Extract relevant kwargs
        temperature = kwargs.get("temperature", 0)
        max_tokens = kwargs.get("max_tokens", 4000)
        top_p = kwargs.get("top_p", 1.0)
        
        # Make API call
        response = await client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        
        return response.choices[0].message.content
    
    return vision_model_func