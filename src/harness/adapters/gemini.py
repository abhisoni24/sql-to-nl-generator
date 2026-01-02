"""
Gemini Adapter for Evaluation Harness.
"""
import os
import time
from typing import List, Dict, Any
from .base import BaseModelAdapter
from google import genai
from google.genai import types

class GeminiAdapter(BaseModelAdapter):
    """Adapter for Google Gemini models via Google GenAI SDK."""

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self._model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment.")
        
        # Initialize client
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompts: List[str]) -> List[str]:
        results = []
        for prompt in prompts:
            try:
                # Explicit decoding parameters as per requirements
                response = self.client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        max_output_tokens=512
                    )
                )
                if response.text:
                    results.append(response.text)
                else:
                    results.append("") # Handle empty response safely
            except Exception as e:
                # Log error verbatim as requested, but we need to return something
                # "Fail loudly" or "Log API errors" - Harness requirement 9 says "Log API errors verbatim".
                # It also says "Do not silently skip prompts".
                # For now, I will append the error string so it's visible in the raw output.
                results.append(f"ERROR: {str(e)}")
        return results

    def model_name(self) -> str:
        return self._model_name

    def model_family(self) -> str:
        return "google"

    def decoding_config(self) -> Dict[str, Any]:
        return {
            "temperature": 0.0,
            "max_tokens": 512
        }
