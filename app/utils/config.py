"""
Configuration module for loading and managing environment variables.
Uses pydantic-settings for type-safe configuration management.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        gemini_api_key: API key for Google Gemini AI
        notebooklm_api_key: API key for NotebookLM (if available)
        host: Server host address
        port: Server port number
        debug: Debug mode flag
        allowed_origins: List of allowed CORS origins
    """
    
    # API Keys
    gemini_api_key: str = ""
    notebooklm_api_key: str = ""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS Configuration
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False
    
    def get_allowed_origins_list(self) -> List[str]:
        """
        Parse allowed origins from comma-separated string to list.
        
     Returns:
        List of allowed origin URLs
        """
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()