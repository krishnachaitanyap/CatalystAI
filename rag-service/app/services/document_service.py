"""
Document processing service for API discovery
Handles different document types and extracts structured API information
"""

import hashlib
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import yaml
from loguru import logger

from app.models.requests import DocumentMetadata, DocumentType
from app.services.parsers import (
    OpenAPIParser,
    GraphQLParser,
    SOAPParser,
    MarkdownParser,
    PostmanParser,
    HARParser
)
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.core.vector_client import VectorClient

class DocumentService:
    """Service for processing and ingesting documents"""
    
    def __init__(self):
        self.parsers = {
            DocumentType.OPENAPI: OpenAPIParser(),
            DocumentType.GRAPHQL: GraphQLParser(),
            DocumentType.SOAP: SOAPParser(),
            DocumentType.WSDL: SOAPParser(),  # WSDL is a type of SOAP
            DocumentType.MARKDOWN: MarkdownParser(),
            DocumentType.CONFLUENCE: MarkdownParser(),  # Confluence uses markdown
            DocumentType.POSTMAN: PostmanParser(),
            DocumentType.HAR: HARParser(),
        }
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
    
    async def process_document(
        self,
        content: bytes,
        filename: str,
        metadata: DocumentMetadata,
        vector_client: VectorClient,
        embedding_model: Any
    ) -> Dict[str, Any]:
        """Process a document and store in vector database"""
        
        start_time = datetime.now()
        
        try:
            # Detect document type if not specified
            if metadata.document_type == DocumentType.UNKNOWN:
                metadata.document_type = self._detect_document_type(filename, content)
            
            # Parse document based on type
            parsed_data = await self._parse_document(content, metadata)
            
            # Generate chunks
            chunks = self.chunking_service.create_chunks(
                content=parsed_data["content"],
                metadata=metadata,
                chunk_size=metadata.chunk_size or 512,
                chunk_overlap=metadata.chunk_overlap or 50
            )
            
            # Generate embeddings for chunks
            embeddings = await self.embedding_service.generate_embeddings(
                texts=[chunk["text"] for chunk in chunks],
                model=embedding_model
            )
            
            # Store in vector database
            chunk_ids = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = await vector_client.store_chunk(
                    content=chunk["text"],
                    embedding=embedding,
                    metadata={
                        **chunk["metadata"],
                        "document_id": metadata.document_id,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "parsed_data": parsed_data
                    }
                )
                chunk_ids.append(chunk_id)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "document_id": metadata.document_id,
                "chunks_created": len(chunks),
                "total_chunks": len(chunks),
                "processing_time_ms": processing_time,
                "embedding_model": str(embedding_model),
                "vector_database": vector_client.get_name(),
                "status": "success",
                "chunk_ids": chunk_ids,
                "parsed_data": parsed_data
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            raise
    
    def _detect_document_type(self, filename: str, content: bytes) -> DocumentType:
        """Detect document type based on filename and content"""
        
        # Check file extension first
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            try:
                yaml_content = yaml.safe_load(content.decode('utf-8'))
                if 'openapi' in yaml_content or 'swagger' in yaml_content:
                    return DocumentType.OPENAPI
            except:
                pass
        
        elif filename.endswith('.json'):
            try:
                json_content = json.loads(content.decode('utf-8'))
                if 'openapi' in json_content or 'swagger' in json_content:
                    return DocumentType.OPENAPI
                elif 'info' in json_content and 'schema' in json_content:
                    return DocumentType.GRAPHQL
                elif 'info' in json_content and 'item' in json_content:
                    return DocumentType.POSTMAN
            except:
                pass
        
        elif filename.endswith('.wsdl') or filename.endswith('.xml'):
            if b'wsdl:' in content or b'<wsdl:' in content:
                return DocumentType.WSDL
            elif b'<soap:' in content or b'<soapenv:' in content:
                return DocumentType.SOAP
        
        elif filename.endswith('.har'):
            return DocumentType.HAR
        
        elif filename.endswith('.md') or filename.endswith('.markdown'):
            return DocumentType.MARKDOWN
        
        # Check content patterns
        content_str = content.decode('utf-8', errors='ignore').lower()
        
        if 'openapi' in content_str or 'swagger' in content_str:
            return DocumentType.OPENAPI
        elif 'graphql' in content_str or 'type ' in content_str:
            return DocumentType.GRAPHQL
        elif 'wsdl' in content_str or 'soap' in content_str:
            return DocumentType.SOAP
        elif 'postman' in content_str or 'collection' in content_str:
            return DocumentType.POSTMAN
        elif 'http' in content_str and ('get' in content_str or 'post' in content_str):
            return DocumentType.MARKDOWN  # Likely API documentation
        
        return DocumentType.UNKNOWN
    
    async def _parse_document(self, content: bytes, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse document using appropriate parser"""
        
        parser = self.parsers.get(metadata.document_type)
        if not parser:
            raise ValueError(f"No parser available for document type: {metadata.document_type}")
        
        content_str = content.decode('utf-8')
        parsed_data = await parser.parse(content_str, metadata)
        
        # Add common metadata
        parsed_data.update({
            "document_type": metadata.document_type.value,
            "filename": metadata.filename,
            "ingested_at": datetime.now().isoformat(),
            "checksum": hashlib.md5(content).hexdigest(),
            "file_size_bytes": len(content)
        })
        
        return parsed_data

class DocumentParser:
    """Base class for document parsers"""
    
    def __init__(self):
        self.api_identification_prompts = self._load_api_identification_prompts()
    
    def _load_api_identification_prompts(self) -> Dict[str, str]:
        """Load prompts for API identification"""
        return {
            "endpoint_extraction": """
            Extract API endpoints from the following content. For each endpoint, identify:
            1. HTTP method (GET, POST, PUT, DELETE, etc.)
            2. Path/URL pattern
            3. Operation ID or name
            4. Summary/description
            5. Parameters (path, query, header, body)
            6. Request/response schemas
            7. Security requirements
            8. Rate limiting information
            9. PII flags (if any sensitive data is handled)
            10. Business domain/category
            
            Format the output as structured JSON with clear endpoint definitions.
            """,
            
            "api_classification": """
            Classify the following API specification:
            1. API style (REST, GraphQL, SOAP, gRPC, Event-driven)
            2. Authentication methods
            3. Data formats (JSON, XML, Protocol Buffers)
            4. Versioning strategy
            5. Base URL patterns
            6. Error handling approach
            7. Documentation standards
            8. Testing patterns
            
            Provide a comprehensive classification with examples.
            """,
            
            "business_context": """
            Analyze the business context of this API:
            1. Primary business domain
            2. User personas and use cases
            3. Data entities and relationships
            4. Business processes supported
            5. Integration patterns
            6. Compliance requirements
            7. Performance expectations
            8. Security considerations
            
            Extract business-relevant information for API discovery.
            """,
            
            "legacy_migration": """
            For legacy API documentation, identify:
            1. Current API patterns and conventions
            2. Deprecated or legacy endpoints
            3. Migration paths and alternatives
            4. Backward compatibility requirements
            5. Modern API standards alignment
            6. Documentation gaps and improvements
            7. Testing and validation needs
            8. Performance optimization opportunities
            
            Focus on modernization and standardization opportunities.
            """
        }
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse document content and extract structured information"""
        raise NotImplementedError("Subclasses must implement parse method")
    
    def _extract_endpoints(self, content: str, prompt_type: str = "endpoint_extraction") -> List[Dict[str, Any]]:
        """Extract endpoints using LLM prompts"""
        # This would integrate with an LLM service for intelligent extraction
        # For now, return basic regex-based extraction
        return self._regex_endpoint_extraction(content)
    
    def _regex_endpoint_extraction(self, content: str) -> List[Dict[str, Any]]:
        """Basic regex-based endpoint extraction as fallback"""
        endpoints = []
        
        # Common HTTP method patterns
        http_methods = r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)'
        
        # Path patterns
        path_patterns = [
            r'`([^`]+)`',  # Code blocks
            r'"([^"]+)"',   # Quoted strings
            r'/([a-zA-Z0-9_\-/{}]+)',  # URL paths
        ]
        
        for pattern in path_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                path = match.group(1)
                if self._looks_like_api_path(path):
                    endpoints.append({
                        "path": path,
                        "method": "GET",  # Default method
                        "description": self._extract_context(content, match.start(), 100),
                        "confidence": 0.7
                    })
        
        return endpoints
    
    def _looks_like_api_path(self, path: str) -> bool:
        """Check if a string looks like an API path"""
        api_indicators = [
            '/api/', '/v1/', '/v2/', '/rest/', '/graphql/',
            '/users/', '/orders/', '/products/', '/auth/',
            '/health/', '/status/', '/metrics/'
        ]
        
        return any(indicator in path.lower() for indicator in api_indicators)
    
    def _extract_context(self, content: str, position: int, context_size: int) -> str:
        """Extract context around a position in the content"""
        start = max(0, position - context_size)
        end = min(len(content), position + context_size)
        return content[start:end].strip()
