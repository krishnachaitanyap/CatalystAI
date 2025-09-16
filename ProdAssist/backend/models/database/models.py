"""
Database models for ProdAssist
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_specs = relationship("APISpec", back_populates="owner")
    chat_sessions = relationship("ChatSession", back_populates="user")


class APISpec(Base):
    """API Specification model"""
    __tablename__ = "api_specs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    api_type = Column(String(20), nullable=False)  # REST, SOAP
    format = Column(String(20), nullable=False)   # OpenAPI, WSDL, etc.
    seal_id = Column(String(50), nullable=False)
    application = Column(String(100), nullable=False)
    version = Column(String(20), default="1.0.0")
    base_url = Column(String(500))
    spec_content = Column(Text, nullable=False)  # JSON/YAML content
    spec_metadata = Column(JSON)  # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="api_specs")
    chat_sessions = relationship("ChatSession", back_populates="api_spec")


class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    context = Column(JSON)  # Session context and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    api_spec_id = Column(Integer, ForeignKey("api_specs.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    api_spec = relationship("APISpec", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    message_type = Column(String(20), default="text")  # text, markdown, widget
    message_metadata = Column(JSON)  # Additional message metadata
    chain_of_thought = Column(Text)  # LLM reasoning process
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class VectorChunk(Base):
    """Vector database chunk model"""
    __tablename__ = "vector_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(100), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, nullable=False)
    embedding = Column(Text)  # Base64 encoded embedding
    chunk_strategy = Column(String(50), nullable=False)
    api_spec_id = Column(Integer, ForeignKey("api_specs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    api_spec = relationship("APISpec")
