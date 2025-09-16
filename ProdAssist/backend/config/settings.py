"""
ProdAssist Backend Configuration
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "ProdAssist"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./prodassist.db"
    
    # Vector Database
    vector_db_path: str = "./vector_db"
    chunking_strategy: str = "ENDPOINT_BASED"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/prodassist.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
