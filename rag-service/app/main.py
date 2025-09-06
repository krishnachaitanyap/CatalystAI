"""
CatalystAI RAG Service - Main Application
Handles document ingestion, embedding generation, and semantic search
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from loguru import logger

from app.core.config import settings
from app.core.dependencies import get_vector_client, get_embedding_model
from app.services.document_service import DocumentService
from app.services.search_service import SearchService
from app.services.embedding_service import EmbeddingService
from app.models.requests import (
    SearchRequest,
    IngestRequest,
    DocumentMetadata,
    SearchResponse
)
from app.models.responses import HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title="CatalystAI RAG Service",
    description="RAG and vector search service for API discovery",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
search_service = SearchService()
embedding_service = EmbeddingService()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="rag-service",
        version="1.0.0"
    )

@app.post("/api/v1/ingest", response_model=dict)
async def ingest_document(
    file: UploadFile = File(...),
    metadata: DocumentMetadata = Depends(),
    vector_client = Depends(get_vector_client),
    embedding_model = Depends(get_embedding_model)
):
    """
    Ingest a document and generate embeddings
    
    Supports:
    - OpenAPI/Swagger specs
    - GraphQL schemas
    - SOAP/WSDL files
    - Markdown/Confluence docs
    - Postman collections
    - HAR files
    """
    try:
        logger.info(f"Ingesting document: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Process document based on type
        result = await document_service.process_document(
            content=content,
            filename=file.filename,
            metadata=metadata,
            vector_client=vector_client,
            embedding_model=embedding_model
        )
        
        return {
            "status": "success",
            "document_id": result.document_id,
            "chunks_created": result.chunks_created,
            "message": f"Successfully ingested {file.filename}"
        }
        
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_apis(
    request: SearchRequest,
    vector_client = Depends(get_vector_client),
    embedding_model = Depends(get_embedding_model)
):
    """
    Search for APIs using hybrid approach:
    1. Vector similarity search
    2. Keyword/BM25 search
    3. Re-ranking with cross-encoder
    4. Signal-based scoring
    """
    try:
        logger.info(f"Processing search query: {request.query}")
        
        # Perform hybrid search
        results = await search_service.hybrid_search(
            query=request.query,
            filters=request.filters,
            limit=request.limit,
            vector_client=vector_client,
            embedding_model=embedding_model
        )
        
        return SearchResponse(
            query=request.query,
            results=results.results,
            total_count=results.total_count,
            search_time_ms=results.search_time_ms,
            citations=results.citations
        )
        
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search/stream")
async def search_apis_stream(
    request: SearchRequest,
    vector_client = Depends(get_vector_client),
    embedding_model = Depends(get_embedding_model)
):
    """
    Stream search results for real-time updates
    """
    try:
        async def generate_results():
            async for chunk in search_service.stream_search(
                query=request.query,
                filters=request.filters,
                limit=request.limit,
                vector_client=vector_client,
                embedding_model=embedding_model
            ):
                yield f"data: {chunk.json()}\n\n"
        
        return StreamingResponse(
            generate_results(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        logger.error(f"Error during stream search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback")
async def submit_search_feedback(
    query: str,
    chosen_result_id: str,
    candidate_ids: list[str],
    label: str,  # "good" or "bad"
    user_id: str
):
    """
    Submit feedback for search results to improve ranking
    """
    try:
        await search_service.record_feedback(
            query=query,
            chosen_result_id=chosen_result_id,
            candidate_ids=candidate_ids,
            label=label,
            user_id=user_id
        )
        
        return {"status": "success", "message": "Feedback recorded"}
        
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models")
async def list_available_models():
    """List available embedding and reranking models"""
    return {
        "embedding_models": [
            "all-MiniLM-L6-v2",
            "e5-small",
            "e5-base",
            "e5-large"
        ],
        "reranking_models": [
            "cross-encoder-ms-marco-MiniLM-L-6-v2",
            "cross-encoder-ms-marco-MiniLM-L-12-v2"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
