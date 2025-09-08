"""
Pydantic models for CatalystAI Data Collector API

This module defines Pydantic models for API request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# User models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    is_admin: bool = False

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Application models
class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sealid: str
    app_metadata: Optional[Dict[str, Any]] = None

class ApplicationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    sealid: str
    owner_id: int
    status: str
    app_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ApplicationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    app_metadata: Optional[Dict[str, Any]] = None

# API Spec models
class APISpecCreate(BaseModel):
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    api_type: str
    format: str
    base_url: Optional[str] = None
    application_id: int

class APISpecResponse(BaseModel):
    id: int
    name: str
    version: str
    description: Optional[str]
    api_type: str
    format: str
    base_url: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    status: str
    application_id: int
    created_by_id: int
    processing_status: str
    processing_error: Optional[str]
    chromadb_id: Optional[str]
    common_spec_data: Optional[Dict[str, Any]]  # Add CommonAPISpec data
    vectorization_metrics: Optional[Dict[str, Any]]  # Add metrics data
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class APISpecUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    base_url: Optional[str] = None

# File upload models
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_format: str
    file_size: int
    upload_status: str
    processing_status: str
    error_message: Optional[str]
    file_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class FileUploadStatus(BaseModel):
    file_id: str
    upload_status: str
    processing_status: str
    error_message: Optional[str]

# Processing models
class ProcessingStatus(BaseModel):
    file_id: str
    status: str
    progress: int
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ConvertRequest(BaseModel):
    file_id: str
    show_metrics: bool = False

class ConvertResponse(BaseModel):
    file_id: str
    success: bool
    api_spec_id: Optional[int] = None
    common_spec: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Common response models
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

# List response models
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int

class ApplicationListResponse(BaseModel):
    applications: List[ApplicationResponse]
    total: int
    page: int
    size: int

class APISpecListResponse(BaseModel):
    api_specs: List[APISpecResponse]
    total: int
    page: int
    size: int

class FileUploadListResponse(BaseModel):
    file_uploads: List[FileUploadResponse]
    total: int
    page: int
    size: int
