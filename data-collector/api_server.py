from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import json
from pathlib import Path
import asyncio
from datetime import datetime

# Import our existing connectors
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from connectors.api_connector import APIConnectorManager, WSDLConnector, SwaggerConnector
from connectors.common_spec import CommonAPISpec

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

# Pydantic models
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    file_format: str
    status: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

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
    common_spec: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# In-memory storage for demo (in production, use a database)
file_storage = {}
processing_status = {}

@app.get("/")
async def root():
    return {"message": "CatalystAI Data Collector API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
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
        
        # Store file information
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
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_type=file_type,
            file_format=file_format,
            status="uploaded",
            message="File uploaded and validated successfully",
            metadata=metadata
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files")
async def list_files():
    """List all uploaded files"""
    files = []
    for file_id, file_info in file_storage.items():
        status_info = processing_status.get(file_id, {"status": "unknown", "progress": 0, "message": ""})
        files.append({
            "file_id": file_id,
            "filename": file_info["filename"],
            "file_type": file_info["file_type"],
            "file_format": file_info["file_format"],
            "file_size": file_info["file_size"],
            "upload_time": file_info["upload_time"],
            "status": status_info["status"],
            "progress": status_info["progress"],
            "message": status_info["message"],
            "metadata": file_info["metadata"]
        })
    return {"files": files}

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
async def convert_file(request: ConvertRequest, background_tasks: BackgroundTasks):
    """Convert uploaded file to CommonAPISpec format"""
    if request.file_id not in file_storage:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = file_storage[request.file_id]
    
    # Update status to processing
    processing_status[request.file_id] = {
        "status": "processing",
        "progress": 10,
        "message": "Starting conversion..."
    }
    
    try:
        # Initialize connector manager
        manager = APIConnectorManager()
        
        # Determine API type based on file format
        api_type = "wsdl" if file_info["file_format"] in ["WSDL", "XSD"] else "swagger"
        
        # Convert file
        success = manager.convert_and_store(
            file_info["file_path"],
            api_type,
            verbose=False,
            metrics=request.show_metrics
        )
        
        if success:
            # Get the converted CommonAPISpec
            common_spec = manager.get_last_converted_spec()
            metrics = manager.get_last_metrics() if request.show_metrics else None
            
            # Update status to completed
            processing_status[request.file_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Conversion completed successfully",
                "result": {
                    "common_spec": common_spec.__dict__ if common_spec else None,
                    "metrics": metrics
                }
            }
            
            return ConvertResponse(
                file_id=request.file_id,
                success=True,
                common_spec=common_spec.__dict__ if common_spec else None,
                metrics=metrics
            )
        else:
            processing_status[request.file_id] = {
                "status": "failed",
                "progress": 0,
                "message": "Conversion failed",
                "error": "Failed to convert file"
            }
            
            return ConvertResponse(
                file_id=request.file_id,
                success=False,
                error="Failed to convert file"
            )
            
    except Exception as e:
        processing_status[request.file_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Conversion error: {str(e)}",
            "error": str(e)
        }
        
        return ConvertResponse(
            file_id=request.file_id,
            success=False,
            error=str(e)
        )

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
    
    elif filename_lower.endswith('.wsdl'):
        return 'SOAP', 'WSDL', True, ''
    
    elif filename_lower.endswith('.xsd'):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
