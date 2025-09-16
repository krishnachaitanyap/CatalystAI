"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class APIType(str, Enum):
    REST = "REST"
    SOAP = "SOAP"


class ChunkingStrategy(str, Enum):
    FIXED_SIZE = "FIXED_SIZE"
    SEMANTIC = "SEMANTIC"
    HYBRID = "HYBRID"
    ENDPOINT_BASED = "ENDPOINT_BASED"


# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# API Spec Schemas
class APISpecBase(BaseModel):
    name: str
    description: Optional[str] = None
    api_type: APIType
    format: str
    seal_id: str
    application: str
    version: str = "1.0.0"
    base_url: Optional[str] = None
    spec_content: str
    metadata: Optional[Dict[str, Any]] = None


class APISpecCreate(APISpecBase):
    pass


class APISpecUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    base_url: Optional[str] = None
    spec_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class APISpec(APISpecBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    owner_id: int
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessageBase(BaseModel):
    content: str
    role: str = "user"
    message_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessage(ChatMessageBase):
    id: int
    chain_of_thought: Optional[str] = None
    tokens_used: int = 0
    created_at: datetime
    session_id: int
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatSessionCreate(ChatSessionBase):
    api_spec_id: Optional[int] = None


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatSession(ChatSessionBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_id: int
    api_spec_id: Optional[int] = None
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True


# Vector Chunk Schemas
class VectorChunkBase(BaseModel):
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    chunk_strategy: ChunkingStrategy


class VectorChunkCreate(VectorChunkBase):
    api_spec_id: int


class VectorChunk(VectorChunkBase):
    id: int
    embedding: Optional[str] = None
    created_at: datetime
    api_spec_id: int
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# LLM Schemas
class LLMRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    include_chain_of_thought: bool = True
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class LLMResponse(BaseModel):
    response: str
    chain_of_thought: Optional[str] = None
    tokens_used: int
    model_used: str


# File Upload Schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_type: str
    size: int
    message: str


# Search Schemas
class SearchRequest(BaseModel):
    query: str
    api_spec_ids: Optional[List[int]] = None
    limit: int = 10


class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float
    api_spec_id: int
