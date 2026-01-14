"""
OpenAI Adapter for Evaluation Harness.
"""
import os
from typing import List, Dict, Any
from .base import BaseModelAdapter
# Assuming `openai` package is available or will be installed. 
# Using conditional import to avoid breaking if not installed, but harness implies dependencies.
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from python_dotenv import load_dotenv
load_dotenv()

class OpenAIAdapter(BaseModelAdapter):
    """Adapter for OpenAI models."""

    def __init__(self, model_name: str = "gpt-4o"):
        if OpenAI is None:
            raise ImportError("openai package is required for OpenAIAdapter")
        
        self._model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment.")
            
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompts: List[str]) -> List[str]:
        results = []
        for prompt in prompts:
            try:
                response = self.client.responses.create(
                    model=self._model_name,
                    #instructions="You are a helpful assistant.",
                    input=prompt,
                    temperature=0.0,
                    max_tokens=512
                )
                results.append(response.output_text)
            except Exception as e:
                results.append(f"ERROR: {str(e)}")
        return results

    def model_name(self) -> str:
        return self._model_name

    def model_family(self) -> str:
        return "openai"

    def decoding_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.0,
            "max_tokens": 512
        }
