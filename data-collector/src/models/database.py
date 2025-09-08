"""
Database models for CatalystAI Data Collector

This module defines SQLite database models for:
- User Management
- Applications Management  
- API Specifications Management
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()

class User(Base):
    """User model for authentication and management"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    applications = relationship("Application", back_populates="owner")
    api_specs = relationship("APISpec", back_populates="created_by")

class Application(Base):
    """Application model for managing different applications/projects"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sealid = Column(String(50), nullable=False)  # SEALID identifier
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='active')  # active, inactive, archived
    app_metadata = Column(JSON)  # Additional application metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="applications")
    api_specs = relationship("APISpec", back_populates="application")

class APISpec(Base):
    """API Specification model for managing uploaded API specs"""
    __tablename__ = 'api_specs'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), default='1.0.0')
    description = Column(Text)
    api_type = Column(String(20), nullable=False)  # REST, SOAP, GraphQL, etc.
    format = Column(String(20), nullable=False)   # Swagger, OpenAPI, WSDL, etc.
    base_url = Column(String(255))
    file_path = Column(String(500))  # Path to uploaded file
    file_size = Column(Integer)
    status = Column(String(20), default='draft')  # draft, active, deprecated, archived
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # CommonAPISpec data (stored as JSON for flexibility)
    common_spec_data = Column(JSON)  # Serialized CommonAPISpec
    vectorization_metrics = Column(JSON)  # Metrics from vectorization process
    
    # Processing metadata
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    processing_error = Column(Text)
    chromadb_id = Column(String(100))  # ChromaDB document ID
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="api_specs")
    created_by = relationship("User", back_populates="api_specs")

class FileUpload(Base):
    """File upload tracking model"""
    __tablename__ = 'file_uploads'
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(100), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # REST, SOAP, Postman, etc.
    file_format = Column(String(20), nullable=False)  # Swagger, WSDL, etc.
    file_size = Column(Integer, nullable=False)
    upload_status = Column(String(20), default='uploaded')  # uploaded, processing, completed, failed
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    error_message = Column(Text)
    file_metadata = Column(JSON)  # Extracted metadata
    temp_file_path = Column(String(500))  # Temporary file path
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=True)  # Link to application
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class ProcessingLog(Base):
    """Processing log for tracking API spec processing"""
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    api_spec_id = Column(Integer, ForeignKey('api_specs.id'), nullable=False)
    operation = Column(String(50), nullable=False)  # upload, convert, vectorize, etc.
    status = Column(String(20), nullable=False)  # started, completed, failed
    message = Column(Text)
    details = Column(JSON)  # Additional processing details
    duration_ms = Column(Integer)  # Processing duration in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    api_spec = relationship("APISpec")

# Database configuration
DATABASE_URL = "sqlite:///./catalystai.db"

def create_database():
    """Create database tables"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(engine):
    """Get database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Database manager class
class DatabaseManager:
    """Database manager for CRUD operations"""
    
    def __init__(self):
        self.engine = create_database()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    # User management methods
    def create_user(self, username: str, email: str, full_name: str, password_hash: str, is_admin: bool = False):
        """Create a new user"""
        with self.get_session() as session:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                password_hash=password_hash,
                is_admin=is_admin
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    def get_user_by_username(self, username: str):
        """Get user by username"""
        with self.get_session() as session:
            return session.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        with self.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    # Application management methods
    def create_application(self, name: str, description: str, sealid: str, owner_id: int, app_metadata: Dict = None):
        """Create a new application"""
        with self.get_session() as session:
            application = Application(
                name=name,
                description=description,
                sealid=sealid,
                owner_id=owner_id,
                app_metadata=app_metadata or {}
            )
            session.add(application)
            session.commit()
            session.refresh(application)
            return application
    
    def get_applications_by_user(self, user_id: int):
        """Get all applications for a user"""
        with self.get_session() as session:
            return session.query(Application).filter(Application.owner_id == user_id).all()
    
    def get_application_by_id(self, app_id: int):
        """Get application by ID"""
        with self.get_session() as session:
            return session.query(Application).filter(Application.id == app_id).first()
    
    # API Spec management methods
    def create_api_spec(self, name: str, version: str, description: str, api_type: str, 
                       format: str, base_url: str, file_path: str, file_size: int,
                       application_id: int, created_by_id: int, common_spec_data: Dict = None,
                       status: str = 'active', vectorization_metrics: Dict = None):
        """Create a new API specification"""
        with self.get_session() as session:
            api_spec = APISpec(
                name=name,
                version=version,
                description=description,
                api_type=api_type,
                format=format,
                base_url=base_url,
                file_path=file_path,
                file_size=file_size,
                status=status,
                application_id=application_id,
                created_by_id=created_by_id,
                common_spec_data=common_spec_data or {},
                vectorization_metrics=vectorization_metrics or {}
            )
            session.add(api_spec)
            session.commit()
            session.refresh(api_spec)
            return api_spec
    
    def get_api_specs_by_application(self, application_id: int):
        """Get all API specs for an application"""
        with self.get_session() as session:
            return session.query(APISpec).filter(APISpec.application_id == application_id).all()
    
    def get_api_spec_by_id(self, spec_id: int):
        """Get API spec by ID"""
        with self.get_session() as session:
            return session.query(APISpec).filter(APISpec.id == spec_id).first()
    
    def update_api_spec_status(self, spec_id: int, status: str, processing_status: str = None, error_message: str = None):
        """Update API spec status"""
        with self.get_session() as session:
            api_spec = session.query(APISpec).filter(APISpec.id == spec_id).first()
            if api_spec:
                api_spec.status = status
                if processing_status:
                    api_spec.processing_status = processing_status
                if error_message:
                    api_spec.processing_error = error_message
                session.commit()
                return api_spec
            return None
    
    # File upload management methods
    def create_file_upload(self, file_id: str, filename: str, file_type: str, file_format: str,
                          file_size: int, user_id: int, file_metadata: Dict = None, temp_file_path: str = None, application_id: int = None):
        """Create a new file upload record"""
        with self.get_session() as session:
            file_upload = FileUpload(
                file_id=file_id,
                filename=filename,
                file_type=file_type,
                file_format=file_format,
                file_size=file_size,
                user_id=user_id,
                file_metadata=file_metadata or {},
                temp_file_path=temp_file_path,
                application_id=application_id
            )
            session.add(file_upload)
            session.commit()
            session.refresh(file_upload)
            return file_upload
    
    def get_file_upload_by_id(self, file_id: str):
        """Get file upload by file ID"""
        with self.get_session() as session:
            return session.query(FileUpload).filter(FileUpload.file_id == file_id).first()
    
    def update_file_upload_status(self, file_id: str, upload_status: str = None, processing_status: str = None, error_message: str = None):
        """Update file upload status"""
        with self.get_session() as session:
            file_upload = session.query(FileUpload).filter(FileUpload.file_id == file_id).first()
            if file_upload:
                if upload_status:
                    file_upload.upload_status = upload_status
                if processing_status:
                    file_upload.processing_status = processing_status
                if error_message:
                    file_upload.error_message = error_message
                session.commit()
                return file_upload
            return None
    
    # Processing log methods
    def create_processing_log(self, api_spec_id: int, operation: str, status: str, message: str = None, details: Dict = None, duration_ms: int = None):
        """Create a processing log entry"""
        with self.get_session() as session:
            log = ProcessingLog(
                api_spec_id=api_spec_id,
                operation=operation,
                status=status,
                message=message,
                details=details or {},
                duration_ms=duration_ms
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
