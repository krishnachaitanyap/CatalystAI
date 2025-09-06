"""
Base classes for CatalystAI RAG Service
Provides consistent interfaces and common functionality
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generic, TypeVar
from dataclasses import dataclass
from datetime import datetime
import asyncio
from functools import wraps
import time

from .exceptions import CatalystAIException

# Type variables for generic services
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')
ConfigT = TypeVar('ConfigT')


def async_timing_decorator(func):
    """Decorator to measure async function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            # Log execution time (could be enhanced with metrics)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            raise e
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry operations on failure"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    continue
            raise last_exception
        return wrapper
    return decorator


@dataclass
class ServiceMetrics:
    """Metrics for service performance monitoring"""
    operation_name: str
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseService(ABC, Generic[InputT, OutputT, ConfigT]):
    """Base class for all services in the RAG system"""
    
    def __init__(self, config: ConfigT):
        self.config = config
        self.metrics: List[ServiceMetrics] = []
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if not self._initialized:
            await self._initialize_impl()
            self._initialized = True
    
    @abstractmethod
    async def _initialize_impl(self) -> None:
        """Implementation-specific initialization"""
        pass
    
    @async_timing_decorator
    async def execute(self, input_data: InputT) -> OutputT:
        """Execute the service with timing and error handling"""
        try:
            await self.initialize()
            result = await self._execute_impl(input_data)
            
            # Record success metrics
            self._record_metrics(True)
            return result
            
        except Exception as e:
            # Record failure metrics
            self._record_metrics(False, str(e))
            raise
    
    @abstractmethod
    async def _execute_impl(self, input_data: InputT) -> OutputT:
        """Implementation-specific execution logic"""
        pass
    
    def _record_metrics(self, success: bool, error_message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record service execution metrics"""
        # This would integrate with actual metrics system
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "service": self.__class__.__name__,
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "config": str(self.config)
        }
    
    def get_metrics(self) -> List[ServiceMetrics]:
        """Get service performance metrics"""
        return self.metrics.copy()


class BaseParser(ABC, Generic[InputT, OutputT]):
    """Base class for document parsers"""
    
    def __init__(self, name: str, supported_types: List[str]):
        self.name = name
        self.supported_types = supported_types
        self._cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    @abstractmethod
    async def parse(self, content: str, metadata: Dict[str, Any]) -> OutputT:
        """Parse document content and return structured data"""
        pass
    
    def can_parse(self, document_type: str) -> bool:
        """Check if this parser can handle the document type"""
        return document_type.lower() in [t.lower() for t in self.supported_types]
    
    def _get_cache_key(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate cache key for content and metadata"""
        import hashlib
        content_hash = hashlib.md5(content.encode()).hexdigest()
        metadata_hash = hashlib.md5(str(sorted(metadata.items())).encode()).hexdigest()
        return f"{self.name}_{content_hash}_{metadata_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[OutputT]:
        """Get parsed result from cache if valid"""
        if cache_key in self._cache:
            cached_item = self._cache[cache_key]
            if time.time() - cached_item['timestamp'] < self._cache_ttl:
                return cached_item['result']
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, result: OutputT) -> None:
        """Cache parsed result with timestamp"""
        self._cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    async def parse_with_caching(self, content: str, metadata: Dict[str, Any]) -> OutputT:
        """Parse document with caching for performance"""
        cache_key = self._get_cache_key(content, metadata)
        
        # Try to get from cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Parse and cache result
        result = await self.parse(content, metadata)
        self._set_cache(cache_key, result)
        
        return result
    
    def clear_cache(self) -> None:
        """Clear the parser cache"""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._cache),
            "cache_ttl": self._cache_ttl,
            "parser_name": self.name
        }


class BaseVectorClient(ABC):
    """Base class for vector database clients"""
    
    @abstractmethod
    async def insert_document(self, document: Dict[str, Any]) -> str:
        """Insert a document into the vector database"""
        pass
    
    @abstractmethod
    async def search_similar(self, query_vector: List[float], limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check vector database health"""
        pass


class BaseDatabaseClient(ABC):
    """Base class for database clients"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a database query"""
        pass
