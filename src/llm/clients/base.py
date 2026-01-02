"""
Abstract LLM client for SQL generation testing.
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
