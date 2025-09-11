"""
Chunking utilities for API specifications

This module provides configurable chunking strategies for breaking down
API specifications into smaller, searchable pieces for ChromaDB storage.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ChunkingStrategy(Enum):
    """Available chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    ENDPOINT_BASED = "endpoint_based"

@dataclass
class ChunkingConfig:
    """Configuration for chunking parameters"""
    strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC
    chunk_size: int = 512
    chunk_overlap: int = 50
    max_chunks_per_spec: int = 20
    preserve_context: bool = True
    include_metadata: bool = True
    min_chunk_size: int = 100
    max_chunk_size: int = 2048

@dataclass
class Chunk:
    """Represents a single chunk of API specification"""
    content: str
    chunk_type: str
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int
    parent_spec_id: str
    start_position: int = 0
    end_position: int = 0

class APISpecChunker:
    """Configurable chunker for API specifications"""
    
    def __init__(self, config: ChunkingConfig = None):
        """Initialize chunker with configuration"""
        self.config = config or ChunkingConfig()
        self.load_environment()
        
    def load_environment(self):
        """Load chunking configuration from environment variables"""
        self.config.chunk_size = int(os.getenv('CHUNK_SIZE', self.config.chunk_size))
        self.config.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', self.config.chunk_overlap))
        self.config.min_chunk_size = int(os.getenv('MIN_CHUNK_SIZE', self.config.min_chunk_size))
        self.config.max_chunk_size = int(os.getenv('MAX_CHUNK_SIZE', self.config.max_chunk_size))
        
        # Only override strategy if environment variable is explicitly set
        strategy_str = os.getenv('CHUNKING_STRATEGY')
        if strategy_str:
            strategy_str = strategy_str.lower()
            if strategy_str == 'fixed_size':
                self.config.strategy = ChunkingStrategy.FIXED_SIZE
            elif strategy_str == 'hybrid':
                self.config.strategy = ChunkingStrategy.HYBRID
            elif strategy_str == 'endpoint_based':
                self.config.strategy = ChunkingStrategy.ENDPOINT_BASED
            else:
                self.config.strategy = ChunkingStrategy.SEMANTIC
    
    def chunk_api_spec(self, common_spec: Any, spec_id: str) -> List[Chunk]:
        """Main method to chunk an API specification"""
        
        if self.config.strategy == ChunkingStrategy.ENDPOINT_BASED:
            return self._chunk_by_endpoints(common_spec, spec_id)
        elif self.config.strategy == ChunkingStrategy.FIXED_SIZE:
            return self._chunk_fixed_size(common_spec, spec_id)
        elif self.config.strategy == ChunkingStrategy.HYBRID:
            return self._chunk_hybrid(common_spec, spec_id)
        else:  # SEMANTIC
            return self._chunk_semantic(common_spec, spec_id)
    
    def _chunk_by_endpoints(self, common_spec: Any, spec_id: str) -> List[Chunk]:
        """Chunk API spec by logical sections (endpoints, auth, etc.)"""
        chunks = []
        chunk_index = 0
        
        # 1. API Overview chunk
        overview_content = self._create_overview_content(common_spec)
        if len(overview_content) >= self.config.min_chunk_size:
            chunks.append(Chunk(
                content=overview_content,
                chunk_type="overview",
                metadata={
                    "api_name": common_spec.api_name,
                    "version": common_spec.version,
                    "category": common_spec.category,
                    "base_url": common_spec.base_url
                },
                chunk_index=chunk_index,
                total_chunks=0,  # Will be updated later
                parent_spec_id=spec_id
            ))
            chunk_index += 1
        
        # 2. Authentication chunk
        auth_content = self._create_auth_content(common_spec)
        if len(auth_content) >= self.config.min_chunk_size:
            chunks.append(Chunk(
                content=auth_content,
                chunk_type="authentication",
                metadata={
                    "api_name": common_spec.api_name,
                    "auth_type": common_spec.authentication.get('type', 'none')
                },
                chunk_index=chunk_index,
                total_chunks=0,
                parent_spec_id=spec_id
            ))
            chunk_index += 1
        
        # 3. Individual endpoint chunks
        for endpoint in common_spec.endpoints:
            endpoint_content = self._create_endpoint_content(endpoint, common_spec)
            if len(endpoint_content) >= self.config.min_chunk_size:
                chunks.append(Chunk(
                    content=endpoint_content,
                    chunk_type="endpoint",
                    metadata={
                        "api_name": common_spec.api_name,
                        "endpoint_name": endpoint.get('name', ''),
                        "method": endpoint.get('method', ''),
                        "path": endpoint.get('path', ''),
                        "summary": endpoint.get('summary', '')
                    },
                    chunk_index=chunk_index,
                    total_chunks=0,
                    parent_spec_id=spec_id
                ))
                chunk_index += 1
        
        # 4. Data models chunk
        models_content = self._create_models_content(common_spec)
        if len(models_content) >= self.config.min_chunk_size:
            chunks.append(Chunk(
                content=models_content,
                chunk_type="data_models",
                metadata={
                    "api_name": common_spec.api_name,
                    "model_count": len(common_spec.endpoints)  # Rough estimate
                },
                chunk_index=chunk_index,
                total_chunks=0,
                parent_spec_id=spec_id
            ))
            chunk_index += 1
        
        # 5. Integration and examples chunk
        integration_content = self._create_integration_content(common_spec)
        if len(integration_content) >= self.config.min_chunk_size:
            chunks.append(Chunk(
                content=integration_content,
                chunk_type="integration",
                metadata={
                    "api_name": common_spec.api_name,
                    "sealId": common_spec.sealId,
                    "application": common_spec.application,
                    "use_cases": len(common_spec.common_use_cases)
                },
                chunk_index=chunk_index,
                total_chunks=0,
                parent_spec_id=spec_id
            ))
            chunk_index += 1
        
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks[:self.config.max_chunks_per_spec]
    
    def _chunk_semantic(self, common_spec: Any, spec_id: str) -> List[Chunk]:
        """Semantic chunking based on content structure"""
        # Create comprehensive text representation
        full_content = self._create_full_content(common_spec)
        
        # Split by semantic boundaries (paragraphs, sections)
        sections = self._split_by_semantic_boundaries(full_content)
        
        chunks = []
        chunk_index = 0
        
        for section in sections:
            if len(section) >= self.config.min_chunk_size:
                # Further split large sections
                if len(section) > self.config.max_chunk_size:
                    sub_chunks = self._split_large_section(section)
                    for sub_chunk in sub_chunks:
                        chunks.append(Chunk(
                            content=sub_chunk,
                            chunk_type="semantic",
                            metadata={
                                "api_name": common_spec.api_name,
                                "section_type": "semantic_section"
                            },
                            chunk_index=chunk_index,
                            total_chunks=0,
                            parent_spec_id=spec_id
                        ))
                        chunk_index += 1
                else:
                    chunks.append(Chunk(
                        content=section,
                        chunk_type="semantic",
                        metadata={
                            "api_name": common_spec.api_name,
                            "section_type": "semantic_section"
                        },
                        chunk_index=chunk_index,
                        total_chunks=0,
                        parent_spec_id=spec_id
                    ))
                    chunk_index += 1
        
        # Update total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks[:self.config.max_chunks_per_spec]
    
    def _chunk_fixed_size(self, common_spec: Any, spec_id: str) -> List[Chunk]:
        """Fixed-size chunking with overlap"""
        full_content = self._create_full_content(common_spec)
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(full_content):
            end = min(start + self.config.chunk_size, len(full_content))
            chunk_content = full_content[start:end]
            
            # Try to end at sentence boundary
            if end < len(full_content):
                last_period = chunk_content.rfind('.')
                if last_period > self.config.chunk_size * 0.7:  # If period is in last 30%
                    chunk_content = chunk_content[:last_period + 1]
                    end = start + last_period + 1
            
            if len(chunk_content.strip()) >= self.config.min_chunk_size:
                chunks.append(Chunk(
                    content=chunk_content.strip(),
                    chunk_type="fixed_size",
                    metadata={
                        "api_name": common_spec.api_name,
                        "start_pos": start,
                        "end_pos": end
                    },
                    chunk_index=chunk_index,
                    total_chunks=0,
                    parent_spec_id=spec_id,
                    start_position=start,
                    end_position=end
                ))
                chunk_index += 1
            
            # Move start position with overlap, but ensure progress
            new_start = end - self.config.chunk_overlap
            if new_start <= start:  # Prevent infinite loop
                new_start = start + self.config.chunk_size // 2
            
            start = new_start
            if start >= len(full_content):
                break
        
        # Update total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks[:self.config.max_chunks_per_spec]
    
    def _chunk_hybrid(self, common_spec: Any, spec_id: str) -> List[Chunk]:
        """Hybrid approach: endpoint-based + semantic for remaining content"""
        # Start with endpoint-based chunking
        chunks = self._chunk_by_endpoints(common_spec, spec_id)
        
        # If we have space, add semantic chunks for remaining content
        if len(chunks) < self.config.max_chunks_per_spec:
            remaining_chunks = self._chunk_semantic(common_spec, spec_id)
            # Add remaining chunks up to limit
            for chunk in remaining_chunks[len(chunks):]:
                if len(chunks) < self.config.max_chunks_per_spec:
                    chunks.append(chunk)
        
        return chunks
    
    def _create_overview_content(self, common_spec: Any) -> str:
        """Create API overview content"""
        return f"""API Overview: {common_spec.api_name}
Version: {common_spec.version}
Description: {common_spec.description}
Base URL: {common_spec.base_url}
Category: {common_spec.category}
Total Endpoints: {len(common_spec.endpoints)}
Seal ID: {common_spec.sealId}
Application: {common_spec.application}
Tags: {', '.join(common_spec.tags)}
Documentation URL: {common_spec.documentation_url}"""
    
    def _create_auth_content(self, common_spec: Any) -> str:
        """Create authentication content"""
        auth = common_spec.authentication
        return f"""Authentication: {auth.get('type', 'none')}
Description: {auth.get('description', 'No description available')}
Required Headers: {auth.get('headers', {})}
OAuth Scopes: {auth.get('scopes', [])}
API Keys: {auth.get('api_key', {})}
Bearer Token: {auth.get('bearer_token', {})}"""
    
    def _create_endpoint_content(self, endpoint: Dict[str, Any], common_spec: Any) -> str:
        """Create individual endpoint content"""
        return f"""Endpoint: {endpoint.get('name', 'Unnamed')}
Method: {endpoint.get('method', 'GET')}
Path: {endpoint.get('path', '')}
Summary: {endpoint.get('summary', '')}
Description: {endpoint.get('description', '')}
Parameters: {json.dumps(endpoint.get('parameters', []), indent=2)}
Responses: {json.dumps(endpoint.get('responses', {}), indent=2)}
Authentication Required: {endpoint.get('auth_required', False)}
Rate Limiting: {endpoint.get('rate_limit', 'Not specified')}"""
    
    def _create_models_content(self, common_spec: Any) -> str:
        """Create data models content"""
        models_text = "Data Models and Types:\n"
        for endpoint in common_spec.endpoints:
            if 'parameters' in endpoint:
                models_text += f"\nParameters for {endpoint.get('name', '')}:\n"
                models_text += json.dumps(endpoint['parameters'], indent=2)
            if 'responses' in endpoint:
                models_text += f"\nResponses for {endpoint.get('name', '')}:\n"
                models_text += json.dumps(endpoint['responses'], indent=2)
        return models_text
    
    def _create_integration_content(self, common_spec: Any) -> str:
        """Create integration and examples content"""
        return f"""Integration Steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(common_spec.integration_steps))}

Best Practices:
{chr(10).join(f'• {practice}' for practice in common_spec.best_practices)}

Common Use Cases:
{chr(10).join(f'• {use_case}' for use_case in common_spec.common_use_cases)}

Rate Limits: {common_spec.rate_limits.get('description', 'Not specified')}
Seal ID: {common_spec.sealId}
Application: {common_spec.application}"""
    
    def _create_full_content(self, common_spec: Any) -> str:
        """Create full content representation"""
        content_parts = [
            self._create_overview_content(common_spec),
            self._create_auth_content(common_spec),
            self._create_integration_content(common_spec)
        ]
        
        # Add endpoint content
        for endpoint in common_spec.endpoints:
            content_parts.append(self._create_endpoint_content(endpoint, common_spec))
        
        return "\n\n".join(content_parts)
    
    def _split_by_semantic_boundaries(self, content: str) -> List[str]:
        """Split content by semantic boundaries (paragraphs, sections)"""
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        
        sections = []
        for paragraph in paragraphs:
            if len(paragraph.strip()) > 0:
                sections.append(paragraph.strip())
        
        return sections
    
    def _split_large_section(self, section: str) -> List[str]:
        """Split large sections into smaller chunks"""
        if len(section) <= self.config.max_chunk_size:
            return [section]
        
        chunks = []
        start = 0
        
        while start < len(section):
            end = min(start + self.config.max_chunk_size, len(section))
            
            # Try to end at sentence boundary
            if end < len(section):
                last_period = section.rfind('.', start, end)
                if last_period > start + self.config.max_chunk_size * 0.7:
                    end = last_period + 1
            
            chunk = section[start:end].strip()
            if len(chunk) >= self.config.min_chunk_size:
                chunks.append(chunk)
            
            # Move start position with overlap, but ensure progress
            new_start = end - self.config.chunk_overlap
            if new_start <= start:  # Prevent infinite loop
                new_start = start + self.config.max_chunk_size // 2
            
            start = new_start
            if start >= len(section):
                break
        
        return chunks
    
    def get_chunking_metrics(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """Get metrics about the chunking process"""
        if not chunks:
            return {}
        
        total_content_length = sum(len(chunk.content) for chunk in chunks)
        chunk_sizes = [len(chunk.content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_content_length": total_content_length,
            "average_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "chunk_types": list(set(chunk.chunk_type for chunk in chunks)),
            "strategy_used": self.config.strategy.value,
            "config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "max_chunks_per_spec": self.config.max_chunks_per_spec,
                "min_chunk_size": self.config.min_chunk_size,
                "max_chunk_size": self.config.max_chunk_size
            }
        }
