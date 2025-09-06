"""
Request models for the RAG service
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class DocumentType(str, Enum):
    OPENAPI = "openapi"
    GRAPHQL = "graphql"
    SOAP = "soap"
    MARKDOWN = "markdown"
    CONFLUENCE = "confluence"
    POSTMAN = "postman"
    HAR = "har"
    WSDL = "wsdl"
    UNKNOWN = "unknown"

class Environment(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"
    SANDBOX = "sandbox"

class APIStyle(str, Enum):
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    SOAP = "soap"
    EVENT = "event"

class SearchFilter(BaseModel):
    """Search filters for API discovery"""
    environments: Optional[List[Environment]] = None
    api_styles: Optional[List[APIStyle]] = None
    systems: Optional[List[str]] = None
    services: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    pii_flagged: Optional[bool] = None
    regions: Optional[List[str]] = None
    latency_max_ms: Optional[int] = None
    availability_min: Optional[float] = None
    scope_ids: Optional[List[str]] = None

class SearchRequest(BaseModel):
    """Search request for API discovery"""
    query: str = Field(..., description="Natural language search query")
    filters: Optional[SearchFilter] = None
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Result offset for pagination")
    include_citations: bool = Field(default=True, description="Include source citations")
    include_metadata: bool = Field(default=True, description="Include API metadata")
    rerank: bool = Field(default=True, description="Enable re-ranking with cross-encoder")

class DocumentMetadata(BaseModel):
    """Metadata for document ingestion"""
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: DocumentType
    source_url: Optional[str] = None
    system_name: Optional[str] = None
    service_name: Optional[str] = None
    api_name: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    environment: Environment = Environment.DEV
    owners: List[str] = Field(default_factory=list)
    criticality: Optional[str] = None
    domain: Optional[str] = None
    version: Optional[str] = None
    last_updated: Optional[datetime] = None
    checksum: Optional[str] = None
    file_size_bytes: Optional[int] = None
    language: Optional[str] = None
    custom_properties: Dict[str, Any] = Field(default_factory=dict)

class IngestRequest(BaseModel):
    """Document ingestion request"""
    metadata: DocumentMetadata
    content: str = Field(..., description="Document content or file path")
    filename: Optional[str] = None
    content_type: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    embedding_model: Optional[str] = None
    force_reprocess: bool = Field(default=False, description="Force reprocessing even if unchanged")

class FeedbackRequest(BaseModel):
    """Search feedback for improving ranking"""
    query: str = Field(..., description="Original search query")
    chosen_result_id: str = Field(..., description="ID of the chosen result")
    candidate_ids: List[str] = Field(..., description="IDs of all candidate results")
    label: str = Field(..., description="Feedback label: 'good' or 'bad'")
    user_id: str = Field(..., description="User ID providing feedback")
    context: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChunkingRequest(BaseModel):
    """Request for custom document chunking"""
    content: str = Field(..., description="Document content to chunk")
    chunk_size: int = Field(default=512, ge=100, le=2048)
    chunk_overlap: int = Field(default=50, ge=0, le=200)
    strategy: str = Field(default="recursive", description="Chunking strategy")
    preserve_headers: bool = Field(default=True, description="Preserve document structure")
    semantic_chunking: bool = Field(default=False, description="Use semantic chunking")

class EmbeddingRequest(BaseModel):
    """Request for generating embeddings"""
    texts: List[str] = Field(..., description="Texts to embed")
    model: Optional[str] = None
    normalize: bool = Field(default=True, description="Normalize embeddings")
    batch_size: Optional[int] = None
