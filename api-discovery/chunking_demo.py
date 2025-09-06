#!/usr/bin/env python3
"""
📚 Understanding Chunking in Vector Databases (FAISS/ChromaDB)

This script demonstrates why chunking is essential when adding documents to vector databases
and shows different chunking strategies for optimal search performance.

Why Chunking is Essential:
1. Token Limits: Embedding models have token limits (e.g., 512, 1024, 2048 tokens)
2. Search Precision: Smaller chunks provide more precise search results
3. Memory Efficiency: Prevents memory issues with large documents
4. Context Preservation: Maintains semantic meaning within chunks
5. Retrieval Quality: Better matching of specific information

Chunking Strategies:
1. Fixed-size chunking: Split by character/token count
2. Semantic chunking: Split by sentences/paragraphs
3. Overlapping chunks: Include context from adjacent chunks
4. Hierarchical chunking: Multiple levels of granularity
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class Chunk:
    """Represents a document chunk"""
    text: str
    metadata: Dict[str, Any]
    chunk_id: str
    chunk_index: int
    total_chunks: int

class DocumentChunker:
    """Handles different chunking strategies for documents"""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize the chunker
        
        Args:
            chunk_size: Maximum number of characters per chunk
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def fixed_size_chunking(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split text into fixed-size chunks
        
        This is the simplest chunking strategy but may break sentences.
        """
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            # Try to end at a sentence boundary
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_exclamation = chunk_text.rfind('!')
                last_question = chunk_text.rfind('?')
                
                last_sentence_end = max(last_period, last_exclamation, last_question)
                if last_sentence_end > self.chunk_size * 0.7:  # Only if we don't lose too much
                    chunk_text = chunk_text[:last_sentence_end + 1]
                    end = start + last_sentence_end + 1
            
            chunk = Chunk(
                text=chunk_text.strip(),
                metadata=metadata.copy(),
                chunk_id=f"{metadata.get('api_name', 'unknown')}_chunk_{chunk_index}",
                chunk_index=chunk_index,
                total_chunks=0  # Will be updated later
            )
            chunks.append(chunk)
            
            start = end - self.overlap
            chunk_index += 1
            
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
            
        return chunks
    
    def semantic_chunking(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """
        Split text by semantic boundaries (paragraphs, sections)
        
        This preserves semantic meaning better than fixed-size chunking.
        """
        chunks = []
        
        # Split by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        chunk_index = 0
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunk = Chunk(
                    text=current_chunk.strip(),
                    metadata=metadata.copy(),
                    chunk_id=f"{metadata.get('api_name', 'unknown')}_semantic_{chunk_index}",
                    chunk_index=chunk_index,
                    total_chunks=0  # Will be updated later
                )
                chunks.append(chunk)
                current_chunk = paragraph
                chunk_index += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunk = Chunk(
                text=current_chunk.strip(),
                metadata=metadata.copy(),
                chunk_id=f"{metadata.get('api_name', 'unknown')}_semantic_{chunk_index}",
                chunk_index=chunk_index,
                total_chunks=0  # Will be updated later
            )
            chunks.append(chunk)
        
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
            
        return chunks
    
    def api_specific_chunking(self, api_spec: Dict[str, Any]) -> List[Chunk]:
        """
        Chunk API specifications by logical sections
        
        This is optimized for API documentation structure.
        """
        chunks = []
        chunk_index = 0
        
        # Chunk 1: Basic Information
        basic_info = f"""
API Name: {api_spec['api_name']}
Category: {api_spec['category']}
Description: {api_spec['description']}
Documentation URL: {api_spec.get('documentation_url', 'N/A')}
        """.strip()
        
        chunks.append(Chunk(
            text=basic_info,
            metadata={
                **api_spec,
                'chunk_type': 'basic_info',
                'chunk_section': 'overview'
            },
            chunk_id=f"{api_spec['api_name']}_basic_{chunk_index}",
            chunk_index=chunk_index,
            total_chunks=0  # Will be updated later
        ))
        chunk_index += 1
        
        # Chunk 2: Endpoints
        if api_spec.get('endpoints'):
            endpoints_text = f"""
Endpoints:
{chr(10).join(f"- {endpoint}" for endpoint in api_spec['endpoints'])}
            """.strip()
            
            chunks.append(Chunk(
                text=endpoints_text,
                metadata={
                    **api_spec,
                    'chunk_type': 'endpoints',
                    'chunk_section': 'technical'
                },
                chunk_id=f"{api_spec['api_name']}_endpoints_{chunk_index}",
                chunk_index=chunk_index,
                total_chunks=0  # Will be updated later
            ))
            chunk_index += 1
        
        # Chunk 3: Authentication & Security
        auth_text = f"""
Authentication: {api_spec.get('authentication', 'N/A')}
Rate Limits: {api_spec.get('rate_limits', 'N/A')}
Best Practices: {', '.join(api_spec.get('best_practices', []))}
        """.strip()
        
        chunks.append(Chunk(
            text=auth_text,
            metadata={
                **api_spec,
                'chunk_type': 'authentication',
                'chunk_section': 'security'
            },
            chunk_id=f"{api_spec['api_name']}_auth_{chunk_index}",
            chunk_index=chunk_index,
            total_chunks=0  # Will be updated later
        ))
        chunk_index += 1
        
        # Chunk 4: Integration & Pricing
        integration_text = f"""
Pricing: {api_spec.get('pricing', 'N/A')}
Integration Steps: {', '.join(api_spec.get('integration_steps', []))}
SDK Languages: {', '.join(api_spec.get('sdk_languages', []))}
        """.strip()
        
        chunks.append(Chunk(
            text=integration_text,
            metadata={
                **api_spec,
                'chunk_type': 'integration',
                'chunk_section': 'implementation'
            },
            chunk_id=f"{api_spec['api_name']}_integration_{chunk_index}",
            chunk_index=chunk_index,
            total_chunks=0  # Will be updated later
        ))
        chunk_index += 1
        
        # Chunk 5: Use Cases
        if api_spec.get('common_use_cases'):
            use_cases_text = f"""
Common Use Cases:
{chr(10).join(f"- {use_case}" for use_case in api_spec['common_use_cases'])}
            """.strip()
            
            chunks.append(Chunk(
                text=use_cases_text,
                metadata={
                    **api_spec,
                    'chunk_type': 'use_cases',
                    'chunk_section': 'applications'
                },
                chunk_id=f"{api_spec['api_name']}_use_cases_{chunk_index}",
                chunk_index=chunk_index,
                total_chunks=0  # Will be updated later
            ))
        
        # Update total_chunks for all chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
            
        return chunks

def demonstrate_chunking():
    """Demonstrate different chunking strategies"""
    
    print("📚 **Chunking Demonstration for Vector Databases**")
    print("=" * 60)
    
    # Sample API specification
    sample_api = {
        "api_name": "Stripe Payment API",
        "category": "Payment Processing",
        "description": "Stripe provides APIs for accepting payments, managing subscriptions, and handling financial transactions. It offers comprehensive payment processing with fraud detection, currency conversion, and subscription management.",
        "endpoints": [
            "POST /v1/payment_intents - Create payment intent",
            "GET /v1/payment_intents/{id} - Retrieve payment intent",
            "POST /v1/charges - Create charge",
            "POST /v1/customers - Create customer",
            "POST /v1/subscriptions - Create subscription"
        ],
        "authentication": "Bearer token authentication with secret key",
        "rate_limits": "100 requests per second, 1000 requests per minute",
        "pricing": "2.9% + 30¢ per successful charge",
        "integration_steps": [
            "Create Stripe account and get API keys",
            "Install Stripe library for your language",
            "Initialize Stripe with your secret key",
            "Create payment intents for transactions",
            "Handle webhooks for payment status updates"
        ],
        "best_practices": [
            "Always use HTTPS in production",
            "Implement idempotency keys",
            "Handle webhook signature verification",
            "Store sensitive data securely",
            "Use test mode for development"
        ],
        "common_use_cases": [
            "E-commerce payments",
            "Subscription billing",
            "Marketplace transactions",
            "Digital goods sales",
            "Recurring payments"
        ],
        "sdk_languages": ["Python", "JavaScript", "Java", "Ruby", "PHP", "Go", "C#"],
        "documentation_url": "https://stripe.com/docs/api"
    }
    
    # Create comprehensive text for chunking
    full_text = f"""
API: {sample_api['api_name']}
Category: {sample_api['category']}
Description: {sample_api['description']}
Endpoints: {', '.join(sample_api['endpoints'])}
Authentication: {sample_api['authentication']}
Rate Limits: {sample_api['rate_limits']}
Pricing: {sample_api['pricing']}
Integration Steps: {' '.join(sample_api['integration_steps'])}
Best Practices: {' '.join(sample_api['best_practices'])}
Use Cases: {' '.join(sample_api['common_use_cases'])}
SDK Languages: {', '.join(sample_api['sdk_languages'])}
Documentation: {sample_api['documentation_url']}
    """.strip()
    
    print(f"📄 **Original Document Length**: {len(full_text)} characters")
    print(f"📄 **Original Document**:")
    print(full_text[:200] + "...")
    print()
    
    # Initialize chunker
    chunker = DocumentChunker(chunk_size=300, overlap=50)
    
    # Strategy 1: Fixed-size chunking
    print("🔧 **Strategy 1: Fixed-Size Chunking**")
    print("-" * 40)
    fixed_chunks = chunker.fixed_size_chunking(full_text, sample_api)
    
    for i, chunk in enumerate(fixed_chunks):
        print(f"Chunk {i+1}/{len(fixed_chunks)} ({len(chunk.text)} chars):")
        print(f"  {chunk.text[:100]}...")
        print()
    
    # Strategy 2: Semantic chunking
    print("🔧 **Strategy 2: Semantic Chunking**")
    print("-" * 40)
    semantic_chunks = chunker.semantic_chunking(full_text, sample_api)
    
    for i, chunk in enumerate(semantic_chunks):
        print(f"Chunk {i+1}/{len(semantic_chunks)} ({len(chunk.text)} chars):")
        print(f"  {chunk.text[:100]}...")
        print()
    
    # Strategy 3: API-specific chunking
    print("🔧 **Strategy 3: API-Specific Chunking**")
    print("-" * 40)
    api_chunks = chunker.api_specific_chunking(sample_api)
    
    for i, chunk in enumerate(api_chunks):
        print(f"Chunk {i+1}/{len(api_chunks)} ({len(chunk.text)} chars) - {chunk.metadata['chunk_type']}:")
        print(f"  {chunk.text[:100]}...")
        print()
    
    # Comparison
    print("📊 **Chunking Strategy Comparison**")
    print("=" * 40)
    print(f"Fixed-size chunks: {len(fixed_chunks)} chunks")
    print(f"Semantic chunks: {len(semantic_chunks)} chunks")
    print(f"API-specific chunks: {len(api_chunks)} chunks")
    print()
    
    print("🎯 **Why Each Strategy is Useful:**")
    print("• Fixed-size: Ensures consistent chunk sizes, good for uniform processing")
    print("• Semantic: Preserves meaning, better for natural language queries")
    print("• API-specific: Optimized for API documentation, better search precision")

def explain_chunking_benefits():
    """Explain the benefits of chunking for vector databases"""
    
    print("\n" + "=" * 60)
    print("🤔 **Why Chunking is Essential for Vector Databases**")
    print("=" * 60)
    
    benefits = [
        {
            "title": "1. Token Limit Constraints",
            "description": "Embedding models have token limits (512, 1024, 2048 tokens). Large documents must be split to fit within these limits.",
            "example": "GPT-3 embeddings: 2048 tokens max\nBERT embeddings: 512 tokens max\nLarge documents need chunking"
        },
        {
            "title": "2. Search Precision",
            "description": "Smaller chunks provide more precise search results. Users get specific information rather than entire documents.",
            "example": "Query: 'payment authentication'\nWithout chunking: Returns entire API doc\nWith chunking: Returns specific auth section"
        },
        {
            "title": "3. Memory Efficiency",
            "description": "Prevents memory issues when processing large documents and improves system performance.",
            "example": "Large API docs (10MB+) → Multiple small chunks (1KB each)\nBetter memory usage and faster processing"
        },
        {
            "title": "4. Context Preservation",
            "description": "Maintains semantic meaning within chunks while allowing granular search.",
            "example": "Chunk 1: Authentication methods\nChunk 2: Rate limiting\nChunk 3: Pricing information"
        },
        {
            "title": "5. Retrieval Quality",
            "description": "Better matching of specific information to user queries.",
            "example": "Query: 'Stripe pricing'\nReturns: Only pricing-related chunk\nNot: Entire Stripe documentation"
        },
        {
            "title": "6. Scalability",
            "description": "Allows processing of large document collections without performance degradation.",
            "example": "1000 API docs × 5 chunks each = 5000 searchable units\nBetter than 1000 large documents"
        }
    ]
    
    for benefit in benefits:
        print(f"\n{benefit['title']}")
        print(f"📝 {benefit['description']}")
        print(f"💡 Example: {benefit['example']}")
    
    print("\n" + "=" * 60)
    print("🎯 **Best Practices for Chunking**")
    print("=" * 60)
    
    practices = [
        "• **Chunk Size**: 200-500 characters for optimal balance",
        "• **Overlap**: 10-20% overlap to preserve context",
        "• **Semantic Boundaries**: Split at sentence/paragraph boundaries",
        "• **Metadata**: Include chunk type and section information",
        "• **Hierarchical**: Use multiple levels for different granularities",
        "• **Testing**: Test different chunk sizes for your use case"
    ]
    
    for practice in practices:
        print(practice)

def main():
    """Main function to demonstrate chunking"""
    
    print("🚀 **Vector Database Chunking Demonstration**")
    print("This script explains why chunking is essential for FAISS/ChromaDB")
    print()
    
    # Demonstrate chunking strategies
    demonstrate_chunking()
    
    # Explain benefits
    explain_chunking_benefits()
    
    print("\n" + "=" * 60)
    print("✅ **Summary**")
    print("=" * 60)
    print("Chunking is essential for vector databases because:")
    print("1. Embedding models have token limits")
    print("2. Smaller chunks provide more precise search results")
    print("3. It improves memory efficiency and performance")
    print("4. It preserves semantic context while enabling granular search")
    print("5. It scales better with large document collections")
    print("\n🎯 Choose the chunking strategy that best fits your use case!")

if __name__ == "__main__":
    main()
