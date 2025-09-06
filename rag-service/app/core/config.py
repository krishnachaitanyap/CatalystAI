"""
Configuration settings for the RAG service
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum

class VectorDatabaseType(str, Enum):
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    PINECONE = "pinecone"

class EmbeddingModel(str, Enum):
    ALL_MINI_LM_L6_V2 = "all-MiniLM-L6-v2"
    E5_SMALL = "e5-small"
    E5_BASE = "e5-base"
    E5_LARGE = "e5-large"

class RerankerModel(str, Enum):
    CROSS_ENCODER_MS_MARCO_L6 = "cross-encoder-ms-marco-MiniLM-L-6-v2"
    CROSS_ENCODER_MS_MARCO_L12 = "cross-encoder-ms-marco-MiniLM-L-12-v2"

class Settings(BaseSettings):
    # Service configuration
    APP_NAME: str = "CatalystAI RAG Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Vector database configuration
    VECTOR_DB_TYPE: VectorDatabaseType = VectorDatabaseType.WEAVIATE
    
    # Weaviate settings
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None
    WEAVIATE_CLASS_NAME: str = "DocumentChunk"
    
    # Qdrant settings
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "document_chunks"
    
    # Pinecone settings
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "catalyst-ai"
    
    # Embedding model configuration
    EMBEDDING_MODEL: EmbeddingModel = EmbeddingModel.E5_SMALL
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_BATCH_SIZE: int = 32
    
    # Reranking configuration
    RERANKER_MODEL: RerankerModel = RerankerModel.CROSS_ENCODER_MS_MARCO_L6
    RERANKER_BATCH_SIZE: int = 16
    
    # Search configuration
    MAX_SEARCH_RESULTS: int = 50
    MAX_RERANK_RESULTS: int = 10
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # PostgreSQL configuration
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/catalyst_ai"
    
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    
    # Model caching
    MODEL_CACHE_DIR: str = "./models"
    ENABLE_MODEL_CACHING: bool = True
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Chunking strategy
    CHUNKING_STRATEGY: str = "recursive"  # recursive, sliding_window, semantic
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
