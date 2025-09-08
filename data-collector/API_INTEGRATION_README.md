# CatalystAI Data Collector API Integration

This document describes the integration between the CatalystAI chat UI and the data-collector backend API.

## Architecture Overview

```
┌─────────────────────┐    HTTP/REST    ┌─────────────────────┐
│   React Frontend    │ ◄─────────────► │   FastAPI Backend   │
│  (catalystai-chat)  │                 │  (data-collector)   │
└─────────────────────┘                 └─────────────────────┘
         │                                        │
         │                                        │
         ▼                                        ▼
┌─────────────────────┐                 ┌─────────────────────┐
│   Chat Interface    │                 │   API Connectors    │
│   API Spec Mgmt     │                 │   WSDL/Swagger      │
└─────────────────────┘                 └─────────────────────┘
```

## Backend API (FastAPI)

### Endpoints

#### 1. File Upload
- **POST** `/upload`
- **Description**: Upload and validate API specification files
- **Request**: Multipart form data with file
- **Response**: File upload confirmation with metadata

#### 2. File Management
- **GET** `/files` - List all uploaded files
- **GET** `/files/{file_id}/status` - Get processing status
- **DELETE** `/files/{file_id}` - Delete uploaded file

#### 3. File Conversion
- **POST** `/convert`
- **Description**: Convert uploaded file to CommonAPISpec format
- **Request**: JSON with file_id and options
- **Response**: Converted API specification and metrics

#### 4. Health Check
- **GET** `/health` - API health status

### Data Flow

1. **Upload**: User uploads WSDL/Swagger file via React UI
2. **Validation**: FastAPI validates file format and structure
3. **Processing**: File is processed by appropriate connector (WSDL/Swagger)
4. **Conversion**: File is converted to CommonAPISpec format
5. **Storage**: Converted data is stored in ChromaDB
6. **Response**: Frontend receives processed API specification

## Frontend Integration

### API Service (`dataCollectorAPI.ts`)

The frontend uses a service layer to communicate with the backend:

```typescript
// Upload file
const uploadResponse = await dataCollectorAPI.uploadFile(file);

// Convert file
const convertResponse = await dataCollectorAPI.convertFile(fileId, showMetrics);

// Get file status
const status = await dataCollectorAPI.getFileStatus(fileId);
```

### Updated Components

#### ApiUploader Component
- **Enhanced Upload**: Now uses real API calls instead of mock data
- **Real Processing**: Files are actually processed by data-collector
- **Error Handling**: Proper error handling for API failures
- **Progress Tracking**: Real-time status updates

#### Integration Points
- **File Upload**: Direct integration with FastAPI upload endpoint
- **File Processing**: Real WSDL/Swagger processing via API
- **Metadata Extraction**: Actual metadata from processed files
- **Error Reporting**: Real error messages from backend processing

## Setup Instructions

### 1. Start the FastAPI Backend

```bash
cd data-collector
./start_api_server.sh
```

The API server will start on `http://localhost:8000`

### 2. Start the React Frontend

```bash
cd catalystai-chat
npm start
```

The React app will start on `http://localhost:3000`

### 3. Environment Configuration

Add to your `.env` file in `catalystai-chat`:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

## API Documentation

Once the FastAPI server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Supported File Types

### WSDL Files
- **Format**: `.wsdl`
- **Processing**: WSDL connector extracts operations, messages, types
- **Output**: SOAP operations with input/output messages

### Swagger/OpenAPI Files
- **Formats**: `.json`, `.yaml`, `.yml`
- **Processing**: Swagger connector extracts endpoints, schemas
- **Output**: REST endpoints with request/response schemas

### Postman Collections
- **Format**: `.json`
- **Processing**: Postman connector extracts requests, responses
- **Output**: API collection with request/response data

## Error Handling

### Backend Errors
- **File Validation**: Invalid file format or structure
- **Processing Errors**: Issues during WSDL/Swagger parsing
- **Storage Errors**: ChromaDB connection or storage issues

### Frontend Errors
- **Network Errors**: API connection failures
- **Upload Errors**: File upload failures
- **Processing Errors**: File processing failures

## Performance Considerations

### File Size Limits
- **Default**: 10MB per file (configurable)
- **Large Files**: Consider chunked upload for very large WSDL files

### Processing Time
- **Small Files**: < 1 second
- **Medium Files**: 1-5 seconds
- **Large Files**: 5-30 seconds

### Concurrent Processing
- **Multiple Files**: Can process multiple files simultaneously
- **Queue Management**: Background task processing for large files

## Security Considerations

### File Upload Security
- **File Type Validation**: Strict validation of file types
- **Content Validation**: Deep validation of file content
- **Size Limits**: Prevent oversized file uploads

### API Security
- **CORS**: Configured for localhost development
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Sanitized error messages

## Troubleshooting

### Common Issues

#### 1. API Connection Failed
- **Check**: FastAPI server is running on port 8000
- **Check**: CORS configuration allows localhost:3000
- **Check**: Network connectivity

#### 2. File Upload Failed
- **Check**: File format is supported
- **Check**: File size is within limits
- **Check**: File content is valid

#### 3. Processing Failed
- **Check**: File structure is correct
- **Check**: Required dependencies are installed
- **Check**: ChromaDB is accessible

### Debug Mode

Enable debug logging by setting:
```env
DEBUG=true
```

## Future Enhancements

### Planned Features
- **Batch Processing**: Process multiple files in batch
- **Progress Tracking**: Real-time progress updates
- **File Versioning**: Track file versions and changes
- **API Caching**: Cache processed results
- **WebSocket Updates**: Real-time status updates

### Integration Improvements
- **Authentication**: Add user authentication
- **Authorization**: Role-based access control
- **Audit Logging**: Track all API operations
- **Metrics**: API usage and performance metrics
