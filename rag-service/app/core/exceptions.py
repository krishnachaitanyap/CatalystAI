"""
Custom exceptions for CatalystAI RAG Service
Provides consistent error handling across the application
"""

from typing import Optional, Any, Dict


class CatalystAIException(Exception):
    """Base exception for all CatalystAI errors"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ValidationError(CatalystAIException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class ProcessingError(CatalystAIException):
    """Raised when document processing fails"""
    
    def __init__(self, message: str, document_id: Optional[str] = None, stage: Optional[str] = None):
        super().__init__(message, "PROCESSING_ERROR", {"document_id": document_id, "stage": stage})


class SearchError(CatalystAIException):
    """Raised when search operations fail"""
    
    def __init__(self, message: str, query: Optional[str] = None, filters: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SEARCH_ERROR", {"query": query, "filters": filters})


class EmbeddingError(CatalystAIException):
    """Raised when embedding generation fails"""
    
    def __init__(self, message: str, model_name: Optional[str] = None, text_length: Optional[int] = None):
        super().__init__(message, "EMBEDDING_ERROR", {"model_name": model_name, "text_length": text_length})


class ChunkingError(CatalystAIException):
    """Raised when document chunking fails"""
    
    def __init__(self, message: str, document_type: Optional[str] = None, chunk_strategy: Optional[str] = None):
        super().__init__(message, "CHUNKING_ERROR", {"document_type": document_type, "chunk_strategy": chunk_strategy})


class RankingError(CatalystAIException):
    """Raised when result ranking fails"""
    
    def __init__(self, message: str, model_name: Optional[str] = None, result_count: Optional[int] = None):
        super().__init__(message, "RANKING_ERROR", {"model_name": model_name, "result_count": result_count})


class DatabaseError(CatalystAIException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None):
        super().__init__(message, "DATABASE_ERROR", {"operation": operation, "table": table})


class ConfigurationError(CatalystAIException):
    """Raised when configuration is invalid"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Any = None):
        super().__init__(message, "CONFIGURATION_ERROR", {"config_key": config_key, "config_value": config_value})
