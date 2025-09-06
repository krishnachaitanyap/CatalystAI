"""
Response models for the RAG service
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SearchResultType(str, Enum):
    ENDPOINT = "endpoint"
    API = "api"
    SERVICE = "service"
    SYSTEM = "system"
    DOCUMENT = "document"

class Citation(BaseModel):
    """Source citation for search results"""
    source_id: str
    source_type: str
    source_url: Optional[str] = None
    chunk_id: str
    content: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class APIMetadata(BaseModel):
    """API metadata for search results"""
    api_id: str
    api_name: str
    api_style: str
    version: Optional[str] = None
    description: Optional[str] = None
    base_url: Optional[str] = None
    documentation_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ServiceMetadata(BaseModel):
    """Service metadata for search results"""
    service_id: str
    service_name: str
    system_name: str
    repository_url: Optional[str] = None
    owners: List[str] = Field(default_factory=list)
    criticality: Optional[str] = None
    domain: Optional[str] = None

class EndpointMetadata(BaseModel):
    """Endpoint metadata for search results"""
    endpoint_id: str
    method: Optional[str] = None
    path: Optional[str] = None
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: List[Dict[str, Any]] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    pii_flagged: bool = False
    rate_limit: Optional[int] = None
    latency_ms_p50: Optional[int] = None
    availability_slo: Optional[float] = None

class SearchResult(BaseModel):
    """Individual search result"""
    result_id: str
    result_type: SearchResultType
    title: str
    content: str
    score: float = Field(..., ge=0.0, le=1.0)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    performance_score: Optional[float] = None
    geographic_score: Optional[float] = None
    freshness_score: Optional[float] = None
    permission_score: Optional[float] = None
    historical_score: Optional[float] = None
    popularity_score: Optional[float] = None
    
    # Metadata
    api_metadata: Optional[APIMetadata] = None
    service_metadata: Optional[ServiceMetadata] = None
    endpoint_metadata: Optional[EndpointMetadata] = None
    
    # Citations
    citations: List[Citation] = Field(default_factory=list)
    
    # Additional properties
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class SearchResults(BaseModel):
    """Complete search results"""
    results: List[SearchResult]
    total_count: int
    search_time_ms: float
    query: str
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    model_used: str
    reranking_applied: bool
    citations_included: bool

class SearchResponse(BaseModel):
    """Search API response"""
    query: str
    results: List[SearchResult]
    total_count: int
    search_time_ms: float
    citations: List[Citation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IngestResult(BaseModel):
    """Document ingestion result"""
    document_id: str
    chunks_created: int
    total_chunks: int
    processing_time_ms: float
    embedding_model: str
    vector_database: str
    status: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float
    dependencies: Dict[str, str] = Field(default_factory=dict)
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

class FeedbackResponse(BaseModel):
    """Feedback submission response"""
    status: str
    feedback_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChunkingResult(BaseModel):
    """Document chunking result"""
    chunks: List[str]
    chunk_count: int
    chunk_size: int
    chunk_overlap: int
    strategy: str
    processing_time_ms: float

class EmbeddingResult(BaseModel):
    """Embedding generation result"""
    embeddings: List[List[float]]
    model: str
    dimension: int
    processing_time_ms: float
    batch_size: int
    normalized: bool

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
