# Vector Database Configuration Examples

## ChromaDB Configuration

```python
# Default ChromaDB configuration
chromadb_config = {
    "type": "chromadb",
    "chunking_strategy": "endpoint_based",
    "max_chunk_size": 1000,
    "chunk_overlap": 200,
    "embedding_model": "text-embedding-ada-002",
    "persist_directory": "./data/vector_db",
    "collection_name": "api_specifications"
}

# Advanced ChromaDB configuration
chromadb_advanced_config = {
    "type": "chromadb",
    "chunking_strategy": "hybrid",
    "max_chunk_size": 2000,
    "chunk_overlap": 400,
    "embedding_model": "text-embedding-3-large",
    "persist_directory": "/opt/prodassist/data/vector_db",
    "collection_name": "api_specifications_v2"
}
```

## OpenSearch Configuration

```python
# Default OpenSearch configuration
opensearch_config = {
    "type": "opensearch",
    "chunking_strategy": "endpoint_based",
    "max_chunk_size": 1000,
    "chunk_overlap": 200,
    "embedding_model": "text-embedding-ada-002",
    "host": "localhost",
    "port": 9200,
    "username": "admin",
    "password": "admin",
    "use_ssl": True,
    "verify_certs": False,
    "index_name": "api_spec_chunks"
}

# Production OpenSearch configuration
opensearch_production_config = {
    "type": "opensearch",
    "chunking_strategy": "semantic",
    "max_chunk_size": 1500,
    "chunk_overlap": 300,
    "embedding_model": "text-embedding-3-large",
    "host": "opensearch-cluster.example.com",
    "port": 443,
    "username": "prodassist_user",
    "password": "secure_password",
    "use_ssl": True,
    "verify_certs": True,
    "index_name": "prodassist_api_specs",
    "timeout": 60,
    "max_retries": 5
}
```

## Environment-based Configuration

```python
import os

# Load configuration from environment variables
def get_vector_db_config():
    db_type = os.getenv('VECTOR_DB_TYPE', 'chromadb')
    
    if db_type == 'chromadb':
        return {
            "type": "chromadb",
            "chunking_strategy": os.getenv('CHUNKING_STRATEGY', 'endpoint_based'),
            "max_chunk_size": int(os.getenv('MAX_CHUNK_SIZE', '1000')),
            "chunk_overlap": int(os.getenv('CHUNK_OVERLAP', '200')),
            "embedding_model": os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002'),
            "persist_directory": os.getenv('CHROMADB_PATH', './data/vector_db'),
            "collection_name": os.getenv('COLLECTION_NAME', 'api_specifications')
        }
    elif db_type == 'opensearch':
        return {
            "type": "opensearch",
            "chunking_strategy": os.getenv('CHUNKING_STRATEGY', 'endpoint_based'),
            "max_chunk_size": int(os.getenv('MAX_CHUNK_SIZE', '1000')),
            "chunk_overlap": int(os.getenv('CHUNK_OVERLAP', '200')),
            "embedding_model": os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002'),
            "host": os.getenv('OPENSEARCH_HOST', 'localhost'),
            "port": int(os.getenv('OPENSEARCH_PORT', '9200')),
            "username": os.getenv('OPENSEARCH_USERNAME', 'admin'),
            "password": os.getenv('OPENSEARCH_PASSWORD', 'admin'),
            "use_ssl": os.getenv('OPENSEARCH_SSL', 'true').lower() == 'true',
            "verify_certs": os.getenv('OPENSEARCH_VERIFY_CERTS', 'false').lower() == 'true',
            "index_name": os.getenv('OPENSEARCH_INDEX', 'api_spec_chunks')
        }
    else:
        raise ValueError(f"Unsupported vector database type: {db_type}")
```

## Usage Examples

### Basic Usage with ChromaDB

```python
from services.api_spec.api_spec_service import APISpecService

# Initialize with ChromaDB
api_service = APISpecService(vector_db_config={
    "type": "chromadb",
    "chunking_strategy": "endpoint_based"
})

# Initialize vector database
await api_service.initialize_vector_database()

# Create API spec
spec_data = APISpecCreate(
    name="My API",
    spec_content="<wsdl>...</wsdl>",
    format="wsdl",
    api_type=APIType.SOAP
)

result = await api_service.create_api_spec(spec_data)
```

### Advanced Usage with OpenSearch

```python
from services.api_spec.api_spec_service import APISpecService

# Initialize with OpenSearch
api_service = APISpecService(vector_db_config={
    "type": "opensearch",
    "host": "localhost",
    "port": 9200,
    "username": "admin",
    "password": "admin",
    "chunking_strategy": "semantic"
})

# Initialize vector database
await api_service.initialize_vector_database()

# Search API specifications
results = await api_service.search_api_specifications(
    query="authentication endpoint",
    filters={"seal_id": "105961", "application": "PROFILE"},
    limit=5
)

# Get vector database statistics
stats = await api_service.get_vector_db_stats()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Unique API specs: {stats['unique_api_specs']}")
```

## Chunking Strategies

### 1. ENDPOINT_BASED (Recommended)
- Chunks by API endpoints
- Each endpoint becomes a separate chunk
- Best for API documentation and search
- Includes comprehensive endpoint information

### 2. SEMANTIC
- Chunks by semantic boundaries
- Groups related content together
- Good for natural language queries
- Preserves context relationships

### 3. HYBRID
- Combines semantic and fixed-size chunking
- Splits large semantic chunks by size
- Balances context and performance
- Good for mixed content types

### 4. FIXED_SIZE
- Chunks by fixed character count
- Simple and predictable
- Good for uniform content
- May break semantic boundaries

## Index Management

### ChromaDB Collections
- Collections serve as indices
- Automatically created when needed
- Metadata stored with documents
- No explicit index management required

### OpenSearch Indices
- Explicit index creation required
- Configurable mapping and settings
- Supports complex queries and aggregations
- Better for production environments

## Performance Considerations

### ChromaDB
- Good for development and small-scale deployments
- File-based storage
- Easy to set up and manage
- Limited scalability

### OpenSearch
- Better for production and large-scale deployments
- Distributed and scalable
- Advanced search capabilities
- Requires more setup and maintenance
