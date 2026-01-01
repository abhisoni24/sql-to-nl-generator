"""
Abstract LLM client for SQL generation testing.
Extensible design supporting Gemini, OpenAI, Claude, and other LLMs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            model_name: Name/identifier of the model
            api_key: API key (if None, will try to load from environment)
        """
        self.model_name = model_name
        self.api_key = api_key or self._get_api_key()
    
    @abstractmethod
    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate SQL from natural language prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional model-specific parameters
        
        Returns:
            Dict containing:
                - 'sql': Generated SQL query
                - 'raw_response': Full response from API
                - 'success': Boolean indicating if generation succeeded
                - 'error': Error message if failed
        """
        pass
    
    def get_schema_prompt(self, nl_task: str) -> str:
        """
        Generate a prompt with schema information.
        
        Args:
            nl_task: Natural language description of the SQL task
        
        Returns:
            Formatted prompt with schema and task
        """
        return f"""You are a SQL expert. Generate the exact raw SQL query to handle the following task:

Task: {nl_task}

Requirements:
1. Return ONLY the SQL query, no explanations or additional text
2. Do not include markdown formatting or code blocks
3. Generate syntactically correct MySQL-compatible SQL

Database Schema:
- users: id (INT), username (VARCHAR), email (VARCHAR), signup_date (DATETIME), is_verified (BOOLEAN), country_code (VARCHAR)
- posts: id (INT), user_id (INT), content (TEXT), posted_at (DATETIME), view_count (INT)
- comments: id (INT), user_id (INT), post_id (INT), comment_text (TEXT), created_at (DATETIME)
- likes: user_id (INT), post_id (INT), liked_at (DATETIME)
- follows: follower_id (INT), followee_id (INT), followed_at (DATETIME)

Foreign Key Relationships:
- posts.user_id → users.id
- comments.user_id → users.id
- comments.post_id → posts.id
- likes.user_id → users.id
- likes.post_id → posts.id
- follows.follower_id → users.id
- follows.followee_id → users.id

SQL Query:"""


class GeminiClient(LLMClient):
    """Google Gemini API client."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
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


class ClaudeClient(LLMClient):
    """Anthropic Claude API client (placeholder for future implementation)."""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        # Will implement when needed
        raise NotImplementedError("Claude client not yet implemented")
    
    def _get_api_key(self) -> str:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        return api_key
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # To be implemented
        raise NotImplementedError("Claude client not yet implemented")


def get_llm_client(provider: str = "gemini", **kwargs) -> LLMClient:
    """
    Factory function to get appropriate LLM client.
    
    Args:
        provider: One of 'gemini', 'openai', 'claude'
        **kwargs: Additional arguments passed to client constructor
    
    Returns:
        Initialized LLM client
    """
    providers = {
        'gemini': GeminiClient,
        'openai': OpenAIClient,
        'claude': ClaudeClient
    }
    
    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from {list(providers.keys())}")
    
    return providers[provider](**kwargs)
