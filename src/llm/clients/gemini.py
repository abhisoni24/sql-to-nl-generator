"""
Gemini API client.
"""

from typing import Dict, Any, Optional
import os
from .base import LLMClient

class GeminiClient(LLMClient):
    """Google Gemini API client."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        # Import here to avoid overhead if not used
        print(f"Initializing GeminiClient with model: {model_name}")
        from google import genai
        self.client = genai.Client(api_key=self.api_key)
    
    def _get_api_key(self) -> str:
        """Get Gemini API key from environment."""
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment")
        return api_key
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate SQL using Gemini."""
        try:
            # Generate content using Gemini API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract SQL from response
            sql = response.text.strip()
            
            # Clean up common artifacts
            sql = self._clean_sql(sql)
            
            return {
                'sql': sql,
                'raw_response': response.text,
                'success': True,
                'error': None
            }
        
        except Exception as e:
            return {
                'sql': None,
                'raw_response': None,
                'success': False,
                'error': str(e)
            }
    
    def _clean_sql(self, sql: str) -> str:
        """Remove common formatting artifacts from SQL."""
        # Remove markdown code blocks
        if sql.startswith('```'):
            lines = sql.split('\n')
            sql = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql
        
        # Remove sql/mysql prefix
        sql = sql.replace('```sql', '').replace('```mysql', '').replace('```', '')
        
        # Strip whitespace
        sql = sql.strip()
        
        return sql
