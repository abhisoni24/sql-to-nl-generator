"""
OpenAI API client.
"""

from typing import Dict, Any, Optional
import os
from .base import LLMClient

class OpenAIClient(LLMClient):
    """OpenAI API client (placeholder for future implementation)."""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        # Will implement when needed
        raise NotImplementedError("OpenAI client not yet implemented")
    
    def _get_api_key(self) -> str:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        return api_key
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # To be implemented
        raise NotImplementedError("OpenAI client not yet implemented")
