# Data Ingestion Strategy for Complex Queries

## 🎯 **Overview: Why Complex Queries Need Rich Data**

Complex queries like "supply chain forecasting with 2500 TPS" require data that spans multiple domains:

- **API Discovery**: Find relevant endpoints and services
- **Performance Analysis**: Assess capacity and scaling needs
- **Integration Guidance**: Provide best practices and patterns
- **Onboarding Requirements**: Identify access controls and processes
- **Infrastructure Impact**: Understand downstream changes needed

## 🏗️ **Multi-Layer Data Architecture**

### **Layer 1: Core API Documentation**
```
┌─────────────────────────────────────────────────────────────┐
│                    Core API Documentation                   │
├─────────────────────────────────────────────────────────────┤
│ • OpenAPI/Swagger specs                                    │
│ • GraphQL schemas                                          │
│ • SOAP WSDL files                                          │
│ • REST endpoint documentation                              │
│ • API versioning information                               │
└─────────────────────────────────────────────────────────────┘
```

### **Layer 2: Business Context & Metadata**
```
┌─────────────────────────────────────────────────────────────┐
│                Business Context & Metadata                  │
├─────────────────────────────────────────────────────────────┤
│ • Business domain classification                           │
│ • Service ownership and team information                   │
│ • Business criticality and SLAs                           │
│ • Integration patterns and dependencies                    │
│ • Use case examples and scenarios                         │
└─────────────────────────────────────────────────────────────┘
```

### **Layer 3: Performance & Infrastructure**
```
┌─────────────────────────────────────────────────────────────┐
│              Performance & Infrastructure                  │
├─────────────────────────────────────────────────────────────┤
│ • Current TPS capacity and limits                          │
│ • Performance benchmarks and metrics                       │
│ • Scaling requirements and thresholds                      │
│ • Infrastructure costs and resource usage                  │
│ • Monitoring and alerting configurations                   │
└─────────────────────────────────────────────────────────────┘
```

### **Layer 4: Integration & Onboarding**
```
┌─────────────────────────────────────────────────────────────┐
│              Integration & Onboarding                      │
├─────────────────────────────────────────────────────────────┤
│ • Authentication and authorization details                 │
│ • Rate limiting and throttling policies                   │
│ • Required scopes and permissions                         │
│ • Approval processes and timelines                        │
│ • Integration examples and code samples                    │
└─────────────────────────────────────────────────────────────┘
```

## 📊 **Data Ingestion Pipeline**

### **Phase 1: Document Discovery & Collection**

```python
class DocumentDiscoveryService:
    """Discovers and collects documents from various sources"""
    
    async def discover_documents(self) -> List[DocumentSource]:
        sources = [
            # API Documentation
            await self._scan_api_documentation(),
            
            # Integration Guides
            await self._scan_integration_guides(),
            
            # Performance Reports
            await self._scan_performance_reports(),
            
            # Infrastructure Documentation
            await self._scan_infrastructure_docs(),
            
            # Business Process Documents
            await self._scan_business_processes(),
            
            # Team Wikis and Knowledge Bases
            await self._scan_team_knowledge_bases()
        ]
        return sources
    
    async def _scan_api_documentation(self) -> List[DocumentSource]:
        """Scan for API documentation in various formats"""
        return [
            DocumentSource(
                type="openapi",
                location="swagger-ui/",
                patterns=["*.yaml", "*.json"],
                metadata={"category": "api_specs"}
            ),
            DocumentSource(
                type="graphql",
                location="graphql-schemas/",
                patterns=["*.graphql", "*.gql"],
                metadata={"category": "api_specs"}
            ),
            DocumentSource(
                type="soap",
                location="soap-services/",
                patterns=["*.wsdl"],
                metadata={"category": "api_specs"}
            )
        ]
```

### **Phase 2: Intelligent Document Processing**

```python
class IntelligentDocumentProcessor:
    """Processes documents with context-aware extraction"""
    
    async def process_document(self, document: Document) -> ProcessedDocument:
        # 1. Extract structured API information
        api_info = await self._extract_api_information(document)
        
        # 2. Identify business context and domain
        business_context = await self._extract_business_context(document)
        
        # 3. Extract performance and infrastructure details
        performance_info = await self._extract_performance_information(document)
        
        # 4. Identify integration patterns and requirements
        integration_info = await self._extract_integration_information(document)
        
        # 5. Generate comprehensive metadata
        metadata = self._generate_comprehensive_metadata(
            api_info, business_context, performance_info, integration_info
        )
        
        return ProcessedDocument(
            original_document=document,
            api_information=api_info,
            business_context=business_context,
            performance_information=performance_info,
            integration_information=integration_info,
            metadata=metadata
        )
```

### **Phase 3: Multi-Dimensional Chunking**

```python
class MultiDimensionalChunkingService:
    """Creates chunks optimized for different query types"""
    
    async def create_optimized_chunks(
        self, 
        document: ProcessedDocument
    ) -> List[DocumentChunk]:
        
        chunks = []
        
        # 1. API Discovery Chunks
        api_chunks = await self._create_api_discovery_chunks(document)
        chunks.extend(api_chunks)
        
        # 2. Performance Analysis Chunks
        performance_chunks = await self._create_performance_chunks(document)
        chunks.extend(performance_chunks)
        
        # 3. Integration Guidance Chunks
        integration_chunks = await self._create_integration_chunks(document)
        chunks.extend(integration_chunks)
        
        # 4. Onboarding Requirement Chunks
        onboarding_chunks = await self._create_onboarding_chunks(document)
        chunks.extend(onboarding_chunks)
        
        # 5. Infrastructure Impact Chunks
        infrastructure_chunks = await self._create_infrastructure_chunks(document)
        chunks.extend(infrastructure_chunks)
        
        return chunks
    
    async def _create_api_discovery_chunks(
        self, 
        document: ProcessedDocument
    ) -> List[DocumentChunk]:
        """Create chunks optimized for API discovery queries"""
        
        chunks = []
        
        if document.api_information:
            # Endpoint-specific chunks
            for endpoint in document.api_information.endpoints:
                chunk = DocumentChunk(
                    content=self._format_endpoint_content(endpoint),
                    chunk_type="api_discovery",
                    metadata={
                        "endpoint_id": endpoint.id,
                        "method": endpoint.method,
                        "path": endpoint.path,
                        "business_domain": document.business_context.domain,
                        "service_name": document.api_information.service_name,
                        "relevance_tags": ["api_discovery", "endpoints", "integration"]
                    },
                    vector_embedding=None  # Will be generated later
                )
                chunks.append(chunk)
        
        return chunks
```

### **Phase 4: Context-Aware Embedding Generation**

```python
class ContextAwareEmbeddingService:
    """Generates embeddings optimized for different query contexts"""
    
    async def generate_contextual_embeddings(
        self, 
        chunks: List[DocumentChunk]
    ) -> List[DocumentChunk]:
        
        for chunk in chunks:
            # Generate embeddings based on chunk type and context
            if chunk.chunk_type == "api_discovery":
                embedding = await self._generate_api_discovery_embedding(chunk)
            elif chunk.chunk_type == "performance_analysis":
                embedding = await self._generate_performance_embedding(chunk)
            elif chunk.chunk_type == "integration_guidance":
                embedding = await self._generate_integration_embedding(chunk)
            else:
                embedding = await self._generate_general_embedding(chunk)
            
            chunk.vector_embedding = embedding
        
        return chunks
    
    async def _generate_api_discovery_embedding(
        self, 
        chunk: DocumentChunk
    ) -> List[float]:
        """Generate embedding optimized for API discovery queries"""
        
        # Create context-enhanced text for embedding
        enhanced_text = f"""
        API Discovery Context:
        Service: {chunk.metadata.get('service_name', 'Unknown')}
        Business Domain: {chunk.metadata.get('business_domain', 'Unknown')}
        Endpoint: {chunk.metadata.get('method', '')} {chunk.metadata.get('path', '')}
        
        Content:
        {chunk.content}
        
        Use Cases: API integration, service discovery, endpoint identification
        """
        
        return await self.embedding_model.encode(enhanced_text)
```

## 🗄️ **Data Storage Strategy**

### **PostgreSQL (Relational Data)**
```sql
-- Core API Information
CREATE TABLE api_services (
    id UUID PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    system_name VARCHAR(255),
    business_domain VARCHAR(100),
    service_owner VARCHAR(255),
    business_criticality VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_endpoints (
    id UUID PRIMARY KEY,
    service_id UUID REFERENCES api_services(id),
    method VARCHAR(10) NOT NULL,
    path TEXT NOT NULL,
    description TEXT,
    parameters JSONB,
    response_schema JSONB,
    rate_limits JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance and Infrastructure
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY,
    service_id UUID REFERENCES api_services(id),
    metric_type VARCHAR(50), -- TPS, response_time, etc.
    current_value DECIMAL,
    threshold_value DECIMAL,
    unit VARCHAR(20),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE infrastructure_costs (
    id UUID PRIMARY KEY,
    service_id UUID REFERENCES api_services(id),
    cost_type VARCHAR(50), -- compute, storage, network, etc.
    monthly_cost DECIMAL,
    currency VARCHAR(3) DEFAULT 'USD',
    effective_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Integration and Onboarding
CREATE TABLE integration_requirements (
    id UUID PRIMARY KEY,
    service_id UUID REFERENCES api_services(id),
    requirement_type VARCHAR(50), -- auth, scopes, approval, etc.
    requirement_value TEXT,
    is_required BOOLEAN DEFAULT true,
    approval_required BOOLEAN DEFAULT false,
    estimated_timeline_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE integration_patterns (
    id UUID PRIMARY KEY,
    service_id UUID REFERENCES api_services(id),
    pattern_name VARCHAR(255),
    pattern_description TEXT,
    code_examples JSONB,
    best_practices TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Vector Database (Semantic Search)**
```python
# Weaviate Schema Example
class DocumentChunk:
    """Vector database schema for semantic search"""
    
    # Core content
    content: str
    chunk_type: str  # api_discovery, performance_analysis, etc.
    
    # Metadata for filtering
    service_name: str
    business_domain: str
    endpoint_method: Optional[str]
    endpoint_path: Optional[str]
    
    # Relevance tags
    relevance_tags: List[str]
    
    # Performance context
    tps_capacity: Optional[int]
    response_time: Optional[float]
    
    # Integration context
    auth_type: Optional[str]
    required_scopes: List[str]
    approval_required: Optional[bool]
    
    # Business context
    business_criticality: Optional[str]
    service_owner: Optional[str]
    
    # Vector embedding
    vector: List[float]
```

## 🔄 **Data Ingestion Workflow**

### **Automated Ingestion Pipeline**
```python
class AutomatedIngestionPipeline:
    """Orchestrates the complete data ingestion process"""
    
    async def run_ingestion_cycle(self):
        """Run a complete ingestion cycle"""
        
        try:
            # 1. Discover new/changed documents
            new_documents = await self.document_discovery.discover_documents()
            changed_documents = await self.document_discovery.identify_changes()
            
            # 2. Process new documents
            for doc in new_documents:
                processed_doc = await self.document_processor.process_document(doc)
                chunks = await self.chunking_service.create_optimized_chunks(processed_doc)
                chunks = await self.embedding_service.generate_contextual_embeddings(chunks)
                
                # 3. Store in both databases
                await self._store_in_postgresql(processed_doc)
                await self._store_in_vector_db(chunks)
            
            # 4. Update changed documents
            for doc in changed_documents:
                await self._update_existing_document(doc)
            
            # 5. Update search indexes
            await self._update_search_indexes()
            
            # 6. Generate ingestion report
            report = self._generate_ingestion_report(new_documents, changed_documents)
            await self._send_ingestion_report(report)
            
        except Exception as e:
            logger.error(f"Ingestion cycle failed: {str(e)}")
            await self._handle_ingestion_failure(e)
    
    async def _store_in_postgresql(self, document: ProcessedDocument):
        """Store structured data in PostgreSQL"""
        
        # Store service information
        service_id = await self.postgres_client.insert_api_service(
            service_name=document.api_information.service_name,
            system_name=document.api_information.system_name,
            business_domain=document.business_context.domain,
            service_owner=document.business_context.owner
        )
        
        # Store endpoints
        for endpoint in document.api_information.endpoints:
            await self.postgres_client.insert_api_endpoint(
                service_id=service_id,
                method=endpoint.method,
                path=endpoint.path,
                description=endpoint.description,
                parameters=endpoint.parameters
            )
        
        # Store performance metrics
        if document.performance_information:
            for metric in document.performance_information.metrics:
                await self.postgres_client.insert_performance_metric(
                    service_id=service_id,
                    metric_type=metric.type,
                    current_value=metric.current_value,
                    threshold_value=metric.threshold_value
                )
    
    async def _store_in_vector_db(self, chunks: List[DocumentChunk]):
        """Store chunks with embeddings in vector database"""
        
        for chunk in chunks:
            await self.vector_client.insert_document_chunk(
                content=chunk.content,
                chunk_type=chunk.chunk_type,
                metadata=chunk.metadata,
                vector=chunk.vector_embedding
            )
```

## 📊 **Data Quality & Validation**

### **Data Quality Checks**
```python
class DataQualityValidator:
    """Validates data quality during ingestion"""
    
    async def validate_document_quality(self, document: ProcessedDocument) -> ValidationResult:
        """Validate the quality of processed document"""
        
        validation_errors = []
        
        # 1. Completeness checks
        if not document.api_information:
            validation_errors.append("Missing API information")
        
        if not document.business_context:
            validation_errors.append("Missing business context")
        
        # 2. Data consistency checks
        if document.api_information and document.business_context:
            if document.api_information.service_name != document.business_context.service_name:
                validation_errors.append("Service name mismatch between API and business context")
        
        # 3. Required field checks
        if document.api_information:
            for endpoint in document.api_information.endpoints:
                if not endpoint.method or not endpoint.path:
                    validation_errors.append(f"Incomplete endpoint: {endpoint}")
        
        # 4. Business logic validation
        if document.performance_information:
            for metric in document.performance_information.metrics:
                if metric.current_value < 0:
                    validation_errors.append(f"Invalid metric value: {metric}")
        
        return ValidationResult(
            is_valid=len(validation_errors) == 0,
            errors=validation_errors,
            warnings=self._generate_warnings(document)
        )
```

## 🚀 **Real-Time Data Updates**

### **Change Detection & Incremental Updates**
```python
class ChangeDetectionService:
    """Detects changes in source documents and triggers updates"""
    
    async def monitor_for_changes(self):
        """Continuously monitor for document changes"""
        
        while True:
            try:
                # Check for changes in various sources
                api_changes = await self._check_api_documentation_changes()
                performance_changes = await self._check_performance_changes()
                integration_changes = await self._check_integration_changes()
                
                # Trigger updates for changed documents
                if api_changes:
                    await self._update_api_documentation(api_changes)
                
                if performance_changes:
                    await self._update_performance_data(performance_changes)
                
                if integration_changes:
                    await self._update_integration_guidance(integration_changes)
                
                # Wait before next check
                await asyncio.sleep(self.config.change_detection_interval)
                
            except Exception as e:
                logger.error(f"Change detection failed: {str(e)}")
                await asyncio.sleep(self.config.error_retry_interval)
```

## 📈 **Ingestion Performance & Scaling**

### **Parallel Processing & Batching**
```python
class ScalableIngestionService:
    """Handles high-volume document ingestion with parallel processing"""
    
    async def ingest_documents_batch(
        self, 
        documents: List[Document],
        batch_size: int = 100
    ) -> IngestionResult:
        """Ingest documents in parallel batches"""
        
        results = []
        
        # Process documents in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Process batch in parallel
            batch_tasks = [
                self._process_single_document(doc) for doc in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        
        # Generate batch report
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        return IngestionResult(
            total_documents=len(documents),
            successful=len(successful),
            failed=len(failed),
            errors=[str(e) for e in failed],
            processing_time=datetime.now() - start_time
        )
```

## 🎯 **Benefits of This Ingestion Strategy**

### **For Complex Queries**
- **Multi-Dimensional Search**: Find APIs by function, performance, or integration needs
- **Context-Aware Results**: Understand business impact and requirements
- **Comprehensive Coverage**: Get complete picture from single query

### **For Data Quality**
- **Structured Storage**: Relational data for precise filtering
- **Semantic Search**: Vector embeddings for natural language queries
- **Real-Time Updates**: Keep data current and accurate

### **For Performance**
- **Optimized Chunking**: Chunks designed for specific query types
- **Parallel Processing**: High-throughput ingestion pipeline
- **Incremental Updates**: Only process changed documents

### **For Maintenance**
- **Automated Pipeline**: Self-running ingestion cycles
- **Quality Validation**: Ensure data accuracy and completeness
- **Change Detection**: Real-time updates from source systems

This comprehensive ingestion strategy ensures that CatalystAI can handle complex, multi-faceted queries by providing rich, structured, and contextually-aware data that spans all the dimensions needed for intelligent responses.
