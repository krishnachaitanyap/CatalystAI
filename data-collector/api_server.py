from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import json
from pathlib import Path
import asyncio
from datetime import datetime
import hashlib
import secrets

# Import our existing connectors
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from connectors.api_connector import APIConnectorManager, WSDLConnector, SwaggerConnector, CommonAPISpec
from models.database import DatabaseManager, User, Application, APISpec, FileUpload
from services.llm_service import LLMQueryService
from models.schemas import (
    UserCreate, UserResponse, UserLogin,
    ApplicationCreate, ApplicationResponse, ApplicationUpdate,
    APISpecCreate, APISpecResponse, APISpecUpdate,
    FileUploadResponse, FileUploadStatus, ProcessingStatus,
    ConvertRequest, ConvertResponse, SuccessResponse, ErrorResponse,
    UserListResponse, ApplicationListResponse, APISpecListResponse, FileUploadListResponse,
    AskRequest, AskResponse
)

app = FastAPI(
    title="CatalystAI Data Collector API",
    description="API for processing and converting API specifications (WSDL, Swagger, OpenAPI)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API connector manager for startup loading
api_connector_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global api_connector_manager
    
    print("🚀 Starting CatalystAI Data Collector API...")
    
    # Initialize database
    print("📊 Initializing database...")
    from models.database import create_database
    create_database()
    
    # Initialize API connector manager
    print("🔧 Initializing API connector manager...")
    from utils.chunking import ChunkingConfig, ChunkingStrategy
    
    # Use ENDPOINT_BASED chunking for better organization
    chunking_config = ChunkingConfig(
        strategy=ChunkingStrategy.ENDPOINT_BASED,
        chunk_size=512,
        chunk_overlap=50,
        max_chunks_per_spec=20,
        min_chunk_size=100,
        max_chunk_size=2048
    )
    
    api_connector_manager = APIConnectorManager(chunking_config)
    api_connector_manager.load_environment()
    
    # Load JSON files from output directory into vector database
    print("📂 Loading JSON files from output directory...")
    loaded_count = api_connector_manager.load_json_files_from_output("output")
    
    if loaded_count > 0:
        print(f"✅ Loaded {loaded_count} JSON files into vector database")
    else:
        print("ℹ️ No JSON files found in output directory")
    
    print("🎉 Startup completed successfully!")

# Initialize database manager
db_manager = DatabaseManager()

# Initialize LLM service
llm_service = LLMQueryService()

# Security
security = HTTPBearer()

# In-memory storage for demo (in production, use a database)
file_storage = {}
processing_status = {}

# Authentication helpers
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token (simplified for demo)"""
    # In production, implement proper JWT token validation
    # For now, we'll use a simple approach
    token = credentials.credentials
    # This is a simplified implementation - in production use proper JWT
    if token == "demo-token":
        return db_manager.get_user_by_username("demo_user")
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.get("/")
async def root():
    return {"message": "CatalystAI Data Collector API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/files/{file_id}/status", response_model=ProcessingStatus)
async def get_file_status(file_id: str):
    """Get processing status for a specific file"""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    status_info = processing_status.get(file_id, {"status": "unknown", "progress": 0, "message": ""})
    return ProcessingStatus(
        file_id=file_id,
        status=status_info["status"],
        progress=status_info["progress"],
        message=status_info["message"],
        result=status_info.get("result"),
        error=status_info.get("error")
    )

@app.post("/convert", response_model=ConvertResponse)
async def convert_file(request: ConvertRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """Convert uploaded file to CommonAPISpec format"""
    try:
        # Get file from database
        with db_manager.get_session() as session:
            file_upload = session.query(FileUpload).filter(
                FileUpload.file_id == request.file_id,
                FileUpload.user_id == current_user.id
            ).first()
            
            if not file_upload:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Update status to processing
            file_upload.processing_status = "processing"
            session.commit()
            
            # Initialize connector manager
            manager = APIConnectorManager()
            
            # Determine API type based on file format
            api_type = "wsdl" if file_upload.file_format in ["WSDL", "XSD"] else "swagger"
            
            # Convert file
            success = manager.convert_and_store(
                file_upload.temp_file_path,
                api_type,
                metrics=request.show_metrics
            )
            
            if success:
                # Get the converted CommonAPISpec
                common_spec = manager.get_last_converted_spec()
                metrics = manager.get_last_metrics() if request.show_metrics else None
                
                # Create APISpec record if application_id is provided
                api_spec_id = None
                if file_upload.application_id and common_spec:
                    api_spec = db_manager.create_api_spec(
                        name=common_spec.api_name,
                        version=common_spec.version,
                        description=common_spec.description,
                        api_type=common_spec.category.upper(),
                        format=file_upload.file_format,
                        base_url=common_spec.base_url,
                        file_path=file_upload.temp_file_path,
                        file_size=file_upload.file_size,
                        status='active',
                        application_id=file_upload.application_id,
                        created_by_id=current_user.id,
                        common_spec_data=common_spec.__dict__,
                        vectorization_metrics=metrics
                    )
                    api_spec_id = api_spec.id
                
                # Update status to completed
                file_upload.processing_status = "completed"
                session.commit()
                
                return ConvertResponse(
                    file_id=request.file_id,
                    success=True,
                    api_spec_id=api_spec_id,
                    common_spec=common_spec.__dict__ if common_spec else None,
                    metrics=metrics
                )
            else:
                # Update status to failed
                file_upload.processing_status = "failed"
                file_upload.error_message = "Conversion failed"
                session.commit()
                
                return ConvertResponse(
                    file_id=request.file_id,
                    success=False,
                    error="Failed to convert file"
                )
                
    except Exception as e:
        # Update status to failed
        with db_manager.get_session() as session:
            file_upload = session.query(FileUpload).filter(
                FileUpload.file_id == request.file_id,
                FileUpload.user_id == current_user.id
            ).first()
            if file_upload:
                file_upload.processing_status = "failed"
                file_upload.error_message = str(e)
                session.commit()
        
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, current_user: User = Depends(get_current_user)):
    """Ask questions about all available API documentation using LLM"""
    try:
        # Get all API specs from the database (global search)
        relevant_api_specs = []
        
        with db_manager.get_session() as session:
            query = session.query(APISpec)
            
            # Only apply filters if specifically requested
            if request.application_id:
                query = query.filter(APISpec.application_id == request.application_id)
                
            if request.api_spec_id:
                query = query.filter(APISpec.id == request.api_spec_id)
                
            api_specs = query.all()
            
            # Convert to response format
            for spec in api_specs:
                relevant_api_specs.append(APISpecResponse.from_orm(spec))
        
        # Use LLM service to generate answer (searches all available docs)
        result = llm_service.ask_question(
            question=request.question,
            application_id=request.application_id,
            api_spec_id=request.api_spec_id,
            max_results=request.max_results
        )
        
        # Add relevant API specs to result
        result['relevant_api_specs'] = relevant_api_specs
        
        return AskResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    if file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_storage[file_id]
    
    # Delete temporary file
    try:
        os.unlink(file_info["file_path"])
    except:
        pass
    
    # Remove from storage
    del file_storage[file_id]
    if file_id in processing_status:
        del processing_status[file_id]
    
    return {"message": "File deleted successfully"}

# Helper functions
def determine_file_type(filename: str, content: bytes) -> tuple[str, str, bool, str]:
    """Determine file type and format"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.json'):
        if 'swagger' in filename_lower or 'openapi' in filename_lower:
            return 'REST', 'Swagger', True, ''
        elif 'postman' in filename_lower:
            return 'Postman', 'Postman Collection', True, ''
        else:
            # Try to detect from content
            try:
                json_content = json.loads(content.decode('utf-8'))
                if 'swagger' in json_content or 'openapi' in json_content:
                    return 'REST', 'Swagger', True, ''
                elif 'info' in json_content and 'item' in json_content:
                    return 'Postman', 'Postman Collection', True, ''
            except:
                pass
            return 'REST', 'Swagger', True, ''  # Default to Swagger for JSON
    
    elif filename_lower.endswith(('.yaml', '.yml')):
        return 'REST', 'OpenAPI', True, ''
    
    elif filename_lower.endswith('.wsdl') or (filename_lower.endswith('.xml') and 'wsdl' in filename_lower):
        return 'SOAP', 'WSDL', True, ''
    
    elif filename_lower.endswith('.xsd') or (filename_lower.endswith('.xml') and 'xsd' in filename_lower):
        return 'SOAP', 'XSD', True, ''
    
    else:
        return 'Unknown', 'Unknown', False, 'Unsupported file type'

async def extract_file_metadata(filename: str, content: bytes, file_type: str, file_format: str) -> Dict[str, Any]:
    """Extract metadata from file content"""
    try:
        if file_type == 'REST' and file_format in ['Swagger', 'OpenAPI']:
            json_content = json.loads(content.decode('utf-8'))
            return {
                "name": json_content.get("info", {}).get("title", filename.split('.')[0]),
                "version": json_content.get("info", {}).get("version", "1.0.0"),
                "description": json_content.get("info", {}).get("description", f"{file_format} specification"),
                "base_url": json_content.get("servers", [{}])[0].get("url", json_content.get("host", "https://api.example.com"))
            }
        elif file_type == 'SOAP' and file_format == 'WSDL':
            content_str = content.decode('utf-8')
            # Extract WSDL metadata
            import re
            name_match = re.search(r'<wsdl:definitions[^>]*name="([^"]*)"[^>]*>', content_str, re.IGNORECASE)
            target_ns_match = re.search(r'targetNamespace="([^"]*)"', content_str)
            
            return {
                "name": name_match.group(1) if name_match else filename.split('.')[0],
                "version": "1.0.0",
                "description": f"WSDL specification",
                "base_url": target_ns_match.group(1) if target_ns_match else "https://api.example.com"
            }
        elif file_type == 'Postman':
            json_content = json.loads(content.decode('utf-8'))
            return {
                "name": json_content.get("info", {}).get("name", filename.split('.')[0]),
                "version": json_content.get("info", {}).get("schema", "2.1.0"),
                "description": json_content.get("info", {}).get("description", "Postman collection"),
                "base_url": "https://api.example.com"
            }
        else:
            return {
                "name": filename.split('.')[0],
                "version": "1.0.0",
                "description": f"{file_format} specification",
                "base_url": "https://api.example.com"
            }
    except Exception as e:
        return {
            "name": filename.split('.')[0],
            "version": "1.0.0",
            "description": f"{file_format} specification",
            "base_url": "https://api.example.com"
        }

# User Management Endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db_manager.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        existing_email = db_manager.get_user_by_username(user.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create user
        hashed_password = hash_password(user.password)
        new_user = db_manager.create_user(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            password_hash=hashed_password,
            is_admin=user.is_admin
        )
        
        return UserResponse.from_orm(new_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@app.get("/users/", response_model=UserListResponse)
async def list_users(page: int = 1, size: int = 10, current_user: User = Depends(get_current_user)):
    """List all users (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This is a simplified implementation - in production, implement proper pagination
    with db_manager.get_session() as session:
        users = session.query(User).offset((page - 1) * size).limit(size).all()
        total = session.query(User).count()
        
        return UserListResponse(
            users=[UserResponse.from_orm(user) for user in users],
            total=total,
            page=page,
            size=size
        )

# Application Management Endpoints
@app.post("/applications/", response_model=ApplicationResponse)
async def create_application(application: ApplicationCreate, current_user: User = Depends(get_current_user)):
    """Create a new application"""
    try:
        new_app = db_manager.create_application(
            name=application.name,
            description=application.description,
            sealid=application.sealid,
            owner_id=current_user.id,
            app_metadata=application.app_metadata
        )
        
        return ApplicationResponse.from_orm(new_app)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")

@app.get("/applications/", response_model=ApplicationListResponse)
async def list_applications(page: int = 1, size: int = 10, current_user: User = Depends(get_current_user)):
    """List user's applications"""
    applications = db_manager.get_applications_by_user(current_user.id)
    
    # Simple pagination
    start = (page - 1) * size
    end = start + size
    paginated_apps = applications[start:end]
    
    return ApplicationListResponse(
        applications=[ApplicationResponse.from_orm(app) for app in paginated_apps],
        total=len(applications),
        page=page,
        size=size
    )

@app.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: int, current_user: User = Depends(get_current_user)):
    """Get application by ID"""
    application = db_manager.get_application_by_id(app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if user owns the application
    if application.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ApplicationResponse.from_orm(application)

@app.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(app_id: int, application_update: ApplicationUpdate, current_user: User = Depends(get_current_user)):
    """Update application"""
    application = db_manager.get_application_by_id(app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check if user owns the application
    if application.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update application
    with db_manager.get_session() as session:
        if application_update.name:
            application.name = application_update.name
        if application_update.description:
            application.description = application_update.description
        if application_update.status:
            application.status = application_update.status
        if application_update.metadata:
            application.metadata = application_update.metadata
        
        session.commit()
        session.refresh(application)
        
        return ApplicationResponse.from_orm(application)

# API Spec Management Endpoints
@app.get("/applications/{app_id}/api-specs", response_model=APISpecListResponse)
async def list_api_specs(app_id: int, page: int = 1, size: int = 10, current_user: User = Depends(get_current_user)):
    """List API specs for an application"""
    # Check if user has access to the application
    application = db_manager.get_application_by_id(app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    api_specs = db_manager.get_api_specs_by_application(app_id)
    
    # Simple pagination
    start = (page - 1) * size
    end = start + size
    paginated_specs = api_specs[start:end]
    
    return APISpecListResponse(
        api_specs=[APISpecResponse.from_orm(spec) for spec in paginated_specs],
        total=len(api_specs),
        page=page,
        size=size
    )

@app.get("/api-specs/{spec_id}", response_model=APISpecResponse)
async def get_api_spec(spec_id: int, current_user: User = Depends(get_current_user)):
    """Get API spec by ID"""
    api_spec = db_manager.get_api_spec_by_id(spec_id)
    if not api_spec:
        raise HTTPException(status_code=404, detail="API spec not found")
    
    # Check if user has access to the application
    application = db_manager.get_application_by_id(api_spec.application_id)
    if application.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return APISpecResponse.from_orm(api_spec)

@app.put("/api-specs/{spec_id}", response_model=APISpecResponse)
async def update_api_spec(spec_id: int, spec_update: APISpecUpdate, current_user: User = Depends(get_current_user)):
    """Update API spec"""
    api_spec = db_manager.get_api_spec_by_id(spec_id)
    if not api_spec:
        raise HTTPException(status_code=404, detail="API spec not found")
    
    # Check if user has access to the application
    application = db_manager.get_application_by_id(api_spec.application_id)
    if application.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update API spec
    with db_manager.get_session() as session:
        if spec_update.name:
            api_spec.name = spec_update.name
        if spec_update.version:
            api_spec.version = spec_update.version
        if spec_update.description:
            api_spec.description = spec_update.description
        if spec_update.status:
            api_spec.status = spec_update.status
        if spec_update.base_url:
            api_spec.base_url = spec_update.base_url
        
        session.commit()
        session.refresh(api_spec)
        
        return APISpecResponse.from_orm(api_spec)

# Enhanced File Upload with Database Integration
@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...), 
    application_id: int = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and validate API specification files"""
    try:
        # Generate unique file ID
        file_id = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Determine file type and format
        file_type, file_format, is_valid, error = determine_file_type(file.filename, content)
        
        if not is_valid:
            os.unlink(tmp_file_path)
            raise HTTPException(status_code=400, detail=error)
        
        # Extract metadata
        metadata = await extract_file_metadata(file.filename, content, file_type, file_format)
        
        # Store file information in database
        file_upload = db_manager.create_file_upload(
            file_id=file_id,
            filename=file.filename,
            file_type=file_type,
            file_format=file_format,
            file_size=len(content),
            user_id=current_user.id,
            file_metadata=metadata,
            temp_file_path=tmp_file_path,
            application_id=application_id
        )
        
        # Store in memory for backward compatibility
        file_storage[file_id] = {
            "filename": file.filename,
            "file_path": tmp_file_path,
            "file_type": file_type,
            "file_format": file_format,
            "file_size": len(content),
            "upload_time": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        processing_status[file_id] = {
            "status": "uploaded",
            "progress": 0,
            "message": "File uploaded successfully"
        }
        
        return FileUploadResponse.from_orm(file_upload)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files", response_model=FileUploadListResponse)
async def list_files(page: int = 1, size: int = 10, current_user: User = Depends(get_current_user)):
    """List all uploaded files for current user"""
    with db_manager.get_session() as session:
        file_uploads = session.query(FileUpload).filter(FileUpload.user_id == current_user.id).offset((page - 1) * size).limit(size).all()
        total = session.query(FileUpload).filter(FileUpload.user_id == current_user.id).count()
        
        return FileUploadListResponse(
            file_uploads=[FileUploadResponse.from_orm(fu) for fu in file_uploads],
            total=total,
            page=page,
            size=size
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
