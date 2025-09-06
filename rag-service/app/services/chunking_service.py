"""
Document chunking service for vector search
Handles different chunking strategies for optimal retrieval
"""

import re
from typing import List, Dict, Any, Optional
from loguru import logger

from app.models.requests import DocumentMetadata

class ChunkingService:
    """Service for creating document chunks for vector search"""
    
    def __init__(self):
        self.default_chunk_size = 512
        self.default_overlap = 50
    
    def create_chunks(
        self,
        content: str,
        metadata: DocumentMetadata,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        strategy: str = "recursive"
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from document content
        
        Args:
            content: Document content to chunk
            metadata: Document metadata
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy (recursive, sliding_window, semantic)
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        
        chunk_size = chunk_size or self.default_chunk_size
        chunk_overlap = chunk_overlap or self.default_overlap
        
        try:
            if strategy == "recursive":
                chunks = self._recursive_chunking(content, chunk_size, chunk_overlap)
            elif strategy == "sliding_window":
                chunks = self._sliding_window_chunking(content, chunk_size, chunk_overlap)
            elif strategy == "semantic":
                chunks = self._semantic_chunking(content, chunk_size, chunk_overlap)
            else:
                logger.warning(f"Unknown chunking strategy: {strategy}, falling back to recursive")
                chunks = self._recursive_chunking(content, chunk_size, chunk_overlap)
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                chunk["metadata"] = {
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk["text"]),
                    "strategy": strategy,
                    "document_type": metadata.document_type.value,
                    "system_name": metadata.system_name,
                    "service_name": metadata.service_name,
                    "api_name": metadata.api_name,
                    "tags": metadata.tags,
                    "environment": metadata.environment.value,
                    "owners": metadata.owners
                }
            
            logger.info(f"Created {len(chunks)} chunks using {strategy} strategy")
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks: {str(e)}")
            # Fallback to simple chunking
            return self._simple_chunking(content, chunk_size)
    
    def _recursive_chunking(
        self,
        content: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """Recursive chunking that respects document structure"""
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', content)
        
        current_chunk = ""
        chunk_start = 0
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "start_pos": chunk_start,
                    "end_pos": chunk_start + len(current_chunk)
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = overlap_text + paragraph
                chunk_start = chunk_start + len(current_chunk) - len(overlap_text)
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    chunk_start = content.find(paragraph)
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start_pos": chunk_start,
                "end_pos": chunk_start + len(current_chunk)
            })
        
        return chunks
    
    def _sliding_window_chunking(
        self,
        content: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """Sliding window chunking with fixed overlap"""
        
        chunks = []
        step = chunk_size - chunk_overlap
        
        for i in range(0, len(content), step):
            chunk_text = content[i:i + chunk_size]
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "start_pos": i,
                    "end_pos": min(i + chunk_size, len(content))
                })
        
        return chunks
    
    def _semantic_chunking(
        self,
        content: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """Semantic chunking that tries to keep related content together"""
        
        # This is a simplified semantic chunking approach
        # In production, you might use more sophisticated NLP techniques
        
        chunks = []
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', content)
        
        current_chunk = ""
        chunk_start = 0
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "start_pos": chunk_start,
                    "end_pos": chunk_start + len(current_chunk)
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = overlap_text + sentence
                chunk_start = chunk_start + len(current_chunk) - len(overlap_text)
            else:
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
                    chunk_start = content.find(sentence)
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start_pos": chunk_start,
                "end_pos": chunk_start + len(current_chunk)
            })
        
        return chunks
    
    def _simple_chunking(
        self,
        content: str,
        chunk_size: int
    ) -> List[Dict[str, Any]]:
        """Simple chunking as fallback"""
        
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk_text = content[i:i + chunk_size]
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "start_pos": i,
                    "end_pos": min(i + chunk_size, len(content)),
                    "metadata": {
                        "chunk_index": len(chunks),
                        "total_chunks": -1,  # Unknown
                        "chunk_size": len(chunk_text),
                        "strategy": "simple_fallback",
                        "error": "Fallback chunking used"
                    }
                })
        
        return chunks
    
    def merge_chunks(
        self,
        chunks: List[Dict[str, Any]],
        merge_threshold: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Merge small chunks that are below threshold
        
        Args:
            chunks: List of chunks to merge
            merge_threshold: Minimum chunk size before merging
            
        Returns:
            List of merged chunks
        """
        
        if not chunks:
            return []
        
        merged_chunks = []
        current_chunk = chunks[0].copy()
        
        for next_chunk in chunks[1:]:
            # If current chunk is small and merging wouldn't exceed max size
            if (len(current_chunk["text"]) < merge_threshold and 
                len(current_chunk["text"]) + len(next_chunk["text"]) <= self.default_chunk_size):
                
                # Merge chunks
                current_chunk["text"] += "\n\n" + next_chunk["text"]
                current_chunk["end_pos"] = next_chunk["end_pos"]
                current_chunk["metadata"]["chunk_size"] = len(current_chunk["text"])
            else:
                # Save current chunk and start new one
                merged_chunks.append(current_chunk)
                current_chunk = next_chunk.copy()
        
        # Add final chunk
        merged_chunks.append(current_chunk)
        
        # Update total chunks count
        for chunk in merged_chunks:
            chunk["metadata"]["total_chunks"] = len(merged_chunks)
        
        return merged_chunks
    
    def validate_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate chunk quality and provide statistics
        
        Args:
            chunks: List of chunks to validate
            
        Returns:
            Validation results and statistics
        """
        
        if not chunks:
            return {"valid": False, "error": "No chunks provided"}
        
        total_chunks = len(chunks)
        total_text_length = sum(len(chunk["text"]) for chunk in chunks)
        avg_chunk_size = total_text_length / total_chunks
        
        # Check for empty chunks
        empty_chunks = [i for i, chunk in enumerate(chunks) if not chunk["text"].strip()]
        
        # Check for very small chunks
        small_chunks = [i for i, chunk in enumerate(chunks) if len(chunk["text"]) < 50]
        
        # Check for very large chunks
        large_chunks = [i for i, chunk in enumerate(chunks) if len(chunk["text"]) > 1000]
        
        validation_result = {
            "valid": True,
            "total_chunks": total_chunks,
            "total_text_length": total_text_length,
            "avg_chunk_size": avg_chunk_size,
            "empty_chunks": empty_chunks,
            "small_chunks": small_chunks,
            "large_chunks": large_chunks,
            "warnings": []
        }
        
        if empty_chunks:
            validation_result["warnings"].append(f"Found {len(empty_chunks)} empty chunks")
            validation_result["valid"] = False
        
        if small_chunks:
            validation_result["warnings"].append(f"Found {len(small_chunks)} very small chunks")
        
        if large_chunks:
            validation_result["warnings"].append(f"Found {len(large_chunks)} very large chunks")
        
        return validation_result
