"""
Google Gemini wrapper functions for LightRAG compatibility
Supports Gemini 2.0 Flash for fast, cost-effective processing
"""

import os
import google.generativeai as genai
from typing import List, Optional, Dict, Any
import asyncio
import numpy as np
from lightrag.utils import EmbeddingFunc
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
def configure_gemini():
    """Configure Google Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)
    return api_key

def create_gemini_llm_func():
    """Create Gemini LLM function compatible with LightRAG"""
    
    # Configure API
    api_key = configure_gemini()
    
    # Get model name from env or use default
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # Create model with safety settings
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        }
    ]
    
    # Generation config for better control
    generation_config = {
        "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.1")),
        "top_p": float(os.getenv("GEMINI_TOP_P", "0.95")),
        "top_k": int(os.getenv("GEMINI_TOP_K", "40")),
        "max_output_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "8192")),
    }
    
    async def llm_model_func(
        prompt: str, 
        system_prompt: Optional[str] = None, 
        history_messages: List[Dict[str, str]] = [], 
        **kwargs
    ) -> str:
        """Gemini completion function compatible with LightRAG"""
        
        try:
            # Create model instance
            model = genai.GenerativeModel(
                model_name=model_name,
                safety_settings=safety_settings,
                generation_config=generation_config,
                system_instruction=system_prompt if system_prompt else None
            )
            
            # Build conversation history
            chat_history = []
            for msg in history_messages:
                role = "user" if msg.get("role") == "user" else "model"
                chat_history.append({
                    "role": role,
                    "parts": [msg.get("content", "")]
                })
            
            # Start chat session
            if chat_history:
                chat = model.start_chat(history=chat_history)
                response = await asyncio.to_thread(
                    chat.send_message, prompt
                )
            else:
                # Direct generation without history
                response = await asyncio.to_thread(
                    model.generate_content, prompt
                )
            
            # Extract text from response
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return ""
                
        except Exception as e:
            logger.error(f"Gemini LLM error: {str(e)}")
            # Retry with exponential backoff for rate limits
            if "429" in str(e) or "quota" in str(e).lower():
                await asyncio.sleep(2)
                return await llm_model_func(prompt, system_prompt, history_messages, **kwargs)
            raise e
    
    return llm_model_func

def create_gemini_embedding_func():
    """Create Gemini embedding function compatible with LightRAG"""
    
    # Configure API
    api_key = configure_gemini()
    
    # Use text embedding model
    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
    embedding_dim = int(os.getenv("GEMINI_EMBEDDING_DIM", "768"))
    
    async def embed_texts(texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        
        try:
            # Gemini has a different embedding API
            model = f"models/{embedding_model}"
            
            embeddings = []
            
            # Process in batches to avoid rate limits
            batch_size = 20
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings for batch
                batch_embeddings = []
                for text in batch:
                    # Use the embedding model
                    result = await asyncio.to_thread(
                        genai.embed_content,
                        model=model,
                        content=text,
                        task_type="retrieval_document",
                        title="Document chunk"
                    )
                    batch_embeddings.append(result['embedding'])
                
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Gemini embedding error: {str(e)}")
            # Retry logic for rate limits
            if "429" in str(e) or "quota" in str(e).lower():
                await asyncio.sleep(2)
                return await embed_texts(texts)
            raise e
    
    # Create embedding function wrapper
    embedding_func = EmbeddingFunc(
        embedding_dim=embedding_dim,
        max_token_size=8192,
        func=lambda texts: asyncio.run(embed_texts(texts))
    )
    
    return embedding_func

def create_gemini_vision_func():
    """Create Gemini vision function for multimodal processing"""
    
    # Configure API
    api_key = configure_gemini()
    
    # Use Flash model for vision
    model_name = os.getenv("GEMINI_VISION_MODEL", "gemini-2.0-flash-exp")
    
    async def vision_model_func(
        prompt: str,
        system_prompt: Optional[str] = None,
        history_messages: List[Dict[str, str]] = [],
        image_data: Optional[str] = None,
        **kwargs
    ) -> str:
        """Gemini vision function for image analysis"""
        
        try:
            # Create model with vision capabilities
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt if system_prompt else None
            )
            
            # Prepare content
            if image_data:
                import base64
                from PIL import Image
                import io
                
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Create multimodal prompt
                response = await asyncio.to_thread(
                    model.generate_content, [prompt, image]
                )
            else:
                # Text-only fallback
                response = await asyncio.to_thread(
                    model.generate_content, prompt
                )
            
            return response.text if response.text else ""
            
        except Exception as e:
            logger.error(f"Gemini vision error: {str(e)}")
            if "429" in str(e) or "quota" in str(e).lower():
                await asyncio.sleep(2)
                return await vision_model_func(prompt, system_prompt, history_messages, image_data, **kwargs)
            raise e
    
    return vision_model_func

# Synchronous wrappers for compatibility
def create_gemini_llm_func_sync():
    """Synchronous wrapper for Gemini LLM"""
    llm_async = create_gemini_llm_func()
    
    def llm_sync(prompt, system_prompt=None, history_messages=[], **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                llm_async(prompt, system_prompt, history_messages, **kwargs)
            )
        finally:
            loop.close()
    
    return llm_sync

def create_gemini_vision_func_sync():
    """Synchronous wrapper for Gemini vision"""
    vision_async = create_gemini_vision_func()
    
    def vision_sync(prompt, system_prompt=None, history_messages=[], image_data=None, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                vision_async(prompt, system_prompt, history_messages, image_data, **kwargs)
            )
        finally:
            loop.close()
    
    return vision_sync