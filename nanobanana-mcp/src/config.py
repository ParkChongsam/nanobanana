"""Configuration module for Nanobanana MCP Server."""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the MCP server."""
    
    # Server settings
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "nanobanana")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Google AI settings
    GOOGLE_GENAI_USE_VERTEXAI: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "False").lower() == "true"
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Model settings
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image-preview")
    
    # Image settings
    IMAGE_SAVE_PATH: Path = Path(os.getenv("IMAGE_SAVE_PATH", "./images"))
    AUTO_CLEANUP_HOURS: int = int(os.getenv("AUTO_CLEANUP_HOURS", "24"))
    
    # Safety settings
    SAFETY_THRESHOLD: str = os.getenv("SAFETY_THRESHOLD", "BLOCK_MEDIUM_AND_ABOVE")
    MAX_CANDIDATE_COUNT: int = int(os.getenv("MAX_CANDIDATE_COUNT", "3"))
    
    # Prompt settings
    AUTO_TRANSLATE: bool = os.getenv("AUTO_TRANSLATE", "True").lower() == "true"
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "ko")
    ADD_TEXT_EXCLUSION: bool = os.getenv("ADD_TEXT_EXCLUSION", "True").lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        if cls.GOOGLE_GENAI_USE_VERTEXAI and not cls.GOOGLE_CLOUD_PROJECT:
            raise ValueError("GOOGLE_CLOUD_PROJECT is required when using Vertex AI")
        
        if not cls.GOOGLE_GENAI_USE_VERTEXAI and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when not using Vertex AI")
        
        # Create image directory if it doesn't exist
        cls.IMAGE_SAVE_PATH.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_google_config(cls) -> Dict[str, Any]:
        """Get Google AI configuration dictionary."""
        config = {
            "model": cls.GEMINI_MODEL,
        }
        
        if cls.GOOGLE_GENAI_USE_VERTEXAI:
            config.update({
                "project": cls.GOOGLE_CLOUD_PROJECT,
                "location": cls.GOOGLE_CLOUD_LOCATION,
            })
        else:
            config["api_key"] = cls.GEMINI_API_KEY
            
        return config