"""
FastAPI application for ProdAssist backend
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import json

from config.settings import settings
from models.database.database import get_db, init_db
from models.database.models import User, APISpec, ChatSession, ChatMessage
from models.schemas.schemas import (
    UserCreate, UserUpdate, User as UserSchema,
    APISpecCreate, APISpecUpdate, APISpec as APISpecSchema,
    ChatSessionCreate, ChatSessionUpdate, ChatSession as ChatSessionSchema,
    ChatMessageCreate, ChatMessage as ChatMessageSchema,
    Token, LLMRequest, LLMResponse, SearchRequest, SearchResult,
    FileUploadResponse
)
from services.user_service import UserService
from services.api_spec.api_spec_service import APISpecService
from services.chat_service import ChatService
from services.llm.llm_service import LLMService
from services.vector_db.vector_db_factory import VectorDatabaseManager
from utils.security import (
    get_current_user, get_current_active_user, get_current_admin_user,
    create_access_token, verify_password
)
from utils.logging import setup_logging, get_logger

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ProdAssist - AI-powered API specification management and chat assistant",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize services
api_spec_service = APISpecService()
llm_service = LLMService()

# Initialize vector database manager
vector_db_config = {
    'type': 'chromadb',
    'chunking_strategy': 'endpoint_based',
    'max_chunk_size': 1000,
    'chunk_overlap': 200,
    'embedding_model': 'text-embedding-ada-002',
    'persist_directory': './vector_db',
    'collection_name': 'api_specifications'
}
vector_service = VectorDatabaseManager(vector_db_config)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting up...")
    logger.info(f"📊 Database: {settings.database_url}")
    logger.info(f"🔍 Vector DB: {settings.vector_db_path}")
    logger.info(f"🤖 LLM Model: {settings.llm_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"👋 {settings.app_name} shutting down...")


# Authentication endpoints
@app.post("/auth/login", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    user_service = UserService(db)
    user = user_service.authenticate_user(username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/register", response_model=UserSchema)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    if user_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if user_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = user_service.create_user(user_data.dict())
    return user


# User management endpoints
@app.get("/users/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@app.put("/users/me", response_model=UserSchema)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@app.get("/users", response_model=List[UserSchema])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    user_service = UserService(db)
    return user_service.get_all_users(skip=skip, limit=limit)


# API Specification endpoints
@app.post("/api-specs", response_model=APISpecSchema)
async def create_api_spec(
    spec_data: APISpecCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new API specification"""
    
    # Validate format
    if not api_spec_service.validate_spec_format(spec_data.spec_content, spec_data.format):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {spec_data.format} format"
        )
    
    # Convert to CommonAPI format
    common_api_spec = api_spec_service.create_api_spec(spec_data)
    
    # Save to database
    db_spec = APISpec(
        name=common_api_spec['api_name'],
        description=common_api_spec['description'],
        api_type=spec_data.api_type.value,
        format=spec_data.format,
        seal_id=spec_data.seal_id,
        application=spec_data.application,
        version=spec_data.version,
        base_url=spec_data.base_url,
        spec_content=json.dumps(common_api_spec),
        metadata=spec_data.metadata,
        owner_id=current_user.id
    )
    
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    
    # Add to vector database
    try:
        vector_service.vector_service.add_api_specification(common_api_spec)
        logger.info(f"✅ Added API spec {db_spec.id} to vector database")
    except Exception as e:
        logger.error(f"❌ Error adding to vector DB: {str(e)}")
    
    return db_spec


@app.get("/api-specs", response_model=List[APISpecSchema])
async def get_api_specs(
    skip: int = 0,
    limit: int = 100,
    seal_id: Optional[str] = None,
    application: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get API specifications with optional filtering"""
    
    query = db.query(APISpec).filter(APISpec.is_active == True)
    
    # Filter by user (non-admin users only see their own specs)
    if not current_user.is_admin:
        query = query.filter(APISpec.owner_id == current_user.id)
    
    # Apply filters
    if seal_id:
        query = query.filter(APISpec.seal_id == seal_id)
    if application:
        query = query.filter(APISpec.application == application)
    
    return query.offset(skip).limit(limit).all()


@app.get("/api-specs/{spec_id}", response_model=APISpecSchema)
async def get_api_spec(
    spec_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific API specification"""
    
    query = db.query(APISpec).filter(APISpec.id == spec_id, APISpec.is_active == True)
    
    # Non-admin users can only see their own specs
    if not current_user.is_admin:
        query = query.filter(APISpec.owner_id == current_user.id)
    
    spec = query.first()
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API specification not found"
        )
    
    return spec


@app.put("/api-specs/{spec_id}", response_model=APISpecSchema)
async def update_api_spec(
    spec_id: int,
    spec_data: APISpecUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update API specification"""
    
    query = db.query(APISpec).filter(APISpec.id == spec_id, APISpec.is_active == True)
    
    # Non-admin users can only update their own specs
    if not current_user.is_admin:
        query = query.filter(APISpec.owner_id == current_user.id)
    
    spec = query.first()
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API specification not found"
        )
    
    # Update spec
    update_data = spec_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(spec, updated_at=datetime.utcnow())
    
    db.commit()
    db.refresh(spec)
    
    return spec


@app.delete("/api-specs/{spec_id}")
async def delete_api_spec(
    spec_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete API specification"""
    
    query = db.query(APISpec).filter(APISpec.id == spec_id, APISpec.is_active == True)
    
    # Non-admin users can only delete their own specs
    if not current_user.is_admin:
        query = query.filter(APISpec.owner_id == current_user.id)
    
    spec = query.first()
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API specification not found"
        )
    
    # Soft delete
    spec.is_active = False
    db.commit()
    
    # Remove from vector database
    try:
        vector_service.vector_service.delete_api_specification(str(spec_id))
        logger.info(f"✅ Removed API spec {spec_id} from vector database")
    except Exception as e:
        logger.error(f"❌ Error removing from vector DB: {str(e)}")
    
    return {"message": "API specification deleted successfully"}


# File upload endpoint
@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    seal_id: str = None,
    application: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """Upload API specification file"""
    
    if not seal_id or not application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="seal_id and application are required"
        )
    
    # Read file content
    content = await file.read()
    content_str = content.decode('utf-8')
    
    # Determine format from file extension
    file_extension = file.filename.split('.')[-1].lower()
    format_mapping = {
        'json': 'openapi',
        'yaml': 'openapi',
        'yml': 'openapi',
        'wsdl': 'wsdl',
        'xml': 'wsdl'
    }
    
    format_type = format_mapping.get(file_extension, 'openapi')
    
    # Validate format
    if not api_spec_service.validate_spec_format(content_str, format_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {format_type} format"
        )
    
    return FileUploadResponse(
        filename=file.filename,
        file_type=format_type,
        size=len(content),
        message="File uploaded successfully"
    )


# Chat endpoints
@app.post("/chat/sessions", response_model=ChatSessionSchema)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new chat session"""
    chat_service = ChatService(db)
    return chat_service.create_chat_session(current_user.id, session_data)


@app.get("/chat/sessions", response_model=List[ChatSessionSchema])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions"""
    chat_service = ChatService(db)
    return chat_service.get_user_chat_sessions(current_user.id, skip=skip, limit=limit)


@app.get("/chat/sessions/{session_id}", response_model=ChatSessionSchema)
async def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific chat session"""
    chat_service = ChatService(db)
    session = chat_service.get_chat_session(session_id, current_user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    return session


@app.post("/chat/sessions/{session_id}/messages", response_model=ChatMessageSchema)
async def send_message(
    session_id: int,
    message: str,
    include_chain_of_thought: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send message and get AI response"""
    chat_service = ChatService(db)
    
    try:
        response = chat_service.generate_response(
            session_id=session_id,
            user_id=current_user.id,
            user_message=message,
            include_chain_of_thought=include_chain_of_thought
        )
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageSchema])
async def get_chat_messages(
    session_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat messages for a session"""
    chat_service = ChatService(db)
    return chat_service.get_session_messages(session_id, current_user.id, limit=limit)


@app.get("/chat/sessions/{session_id}/history")
async def get_chat_history(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get complete chat history"""
    chat_service = ChatService(db)
    return chat_service.get_chat_history(session_id, current_user.id)


# Search endpoint
@app.post("/search", response_model=List[SearchResult])
async def search_api_specs(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Search API specifications using vector similarity"""
    
    try:
        results = vector_service.vector_service.search_api_specifications(
            query=search_request.query,
            api_spec_ids=search_request.api_spec_ids,
            limit=search_request.limit
        )
        
        return [
            SearchResult(
                content=result['content'],
                metadata=result['metadata'],
                score=result['score'],
                api_spec_id=result['api_spec_id']
            )
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"❌ Error in search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


# LLM endpoint
@app.post("/llm/generate", response_model=LLMResponse)
async def generate_llm_response(
    request: LLMRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate LLM response directly"""
    try:
        response = llm_service.generate_response(
            prompt=request.prompt,
            context=request.context,
            include_chain_of_thought=request.include_chain_of_thought
        )
        return response
    except Exception as e:
        logger.error(f"❌ Error in LLM generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM generation failed"
        )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
