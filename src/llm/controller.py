"""
Controller for routing LLM requests to appropriate clients.
"""

from typing import Dict, Type
from .clients.base import LLMClient
from .clients.gemini import GeminiClient
from .clients.openai import OpenAIClient
from .clients.claude import ClaudeClient

class LLMController:
    """Controller to route requests to the desired LLM client."""
    
    _providers: Dict[str, Type[LLMClient]] = {
        'gemini': GeminiClient,
        'openai': OpenAIClient,
        'claude': ClaudeClient
    }
    
    @classmethod
    def get_client(cls, provider: str = "gemini", **kwargs) -> LLMClient:
        """
        Get an instance of the specified LLM client.
        
        Args:
            provider: One of 'gemini', 'openai', 'claude'
            **kwargs: Additional arguments passed to client constructor (e.g., model_name, api_key)
            
        Returns:
            Initialized LLM client instance
        """
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}. Choose from {list(cls._providers.keys())}")
        
        return cls._providers[provider](**kwargs)

def get_llm_client(provider: str = "gemini", **kwargs) -> LLMClient:
    """
    Factory function to get appropriate LLM client.
    Wrapper around LLMController for backward compatibility.
    """
    return LLMController.get_client(provider, **kwargs)
