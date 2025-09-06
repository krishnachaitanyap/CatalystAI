# CatalystAI - Enterprise API Discovery & Onboarding Platform

## Product Vision

**CatalystAI** is an LLM-powered API discovery and one-click onboarding platform that provisions access via OIDC, raises Jira tickets to AD/Platform teams, and ranks services using SOLAR-style signals. The platform is designed to be edge/IoT aware and supports both modern API standards and legacy systems.

## Core Value Proposition

- **Intelligent Discovery**: LLM-powered search across all API types (REST, GraphQL, gRPC, SOAP, Event-driven)
- **One-Click Onboarding**: Automated provisioning via OIDC with Jira workflow integration
- **Enterprise Integration**: Seamless integration with existing identity systems (Keycloak, Azure AD) and project management (Jira)
- **Legacy Support**: Full support for SOAP/WSDL and non-Swagger REST APIs
- **Performance-Aware**: SOLAR-style ranking considering latency, regional proximity, and historical success rates

## Target Users

- **API Consumers**: Developers, DevOps engineers, and business users needing API access
- **API Providers**: Platform teams, API owners, and architects
- **DevOps Teams**: Infrastructure and security teams managing API access
- **Business Stakeholders**: Product managers and business analysts

## Technical Architecture

### Technology Stack

#### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: TanStack Query + React Hook Form
- **Build Tool**: Turborepo + pnpm

#### Backend Core
- **Framework**: Spring Boot 3 (Java 21)
- **API**: GraphQL + REST endpoints
- **Security**: Spring Security (Resource Server) with OIDC
- **Data**: Spring Data JPA + MapStruct
- **Observability**: Micrometer + Actuator

#### Workers & Ingestion
- **Framework**: Python 3.11 + FastAPI
- **Queue System**: Celery/RQ for background processing
- **Parsers**: OpenAPI, GraphQL, AsyncAPI, WSDL, Postman, HAR, Confluence

#### Data Layer
- **Primary Database**: PostgreSQL 16 (relational data)
- **Vector Database**: Weaviate, Qdrant, or Pinecone (vector search)
- **Cache/Queue**: Redis
- **Search**: Hybrid approach (BM25 + vector embeddings + re-ranking)

#### Identity & Security
- **Identity Provider**: Keycloak with OIDC
- **Enterprise Integration**: SCIM for Azure AD/Okta
- **Secrets Management**: HashiCorp Vault
- **Policy Engine**: Open Policy Agent (OPA)

#### Infrastructure
- **Containerization**: Docker + docker-compose (local), Kubernetes (production)
- **CI/CD**: GitHub Actions
- **API Gateway**: Kong (optional)
- **Monitoring**: Prometheus + Grafana

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Catalog API   │    │   RAG Service   │
│   (Next.js)     │◄──►│   (Spring)      │◄──►│   (Java/Python) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   PostgreSQL    │    │   Vector DB     │
         │              │   (Relational)  │    │   (Weaviate/    │
         │              └─────────────────┘    │   Qdrant)       │
         │                       │            └─────────────────┘
         ▼                       ▼                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Keycloak      │    │   Jira          │    │   Redis Cache   │
│   (OIDC)       │    │   (Workflow)    │    │   + Queue       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   HashiCorp     │
│   Vault         │
└─────────────────┘
```

## Core Features

### 1. API Discovery & Search

#### Search Capabilities
- **Natural Language Queries**: "I need to get customer balances" → relevant endpoints
- **Hybrid Search**: Combines keyword (BM25), semantic (vector), and structured search
- **Re-ranking**: Cross-encoder models for result relevance
- **Filters**: Environment, region, latency, PII flags, scopes

#### Supported API Types
- **REST APIs**: OpenAPI/Swagger, non-Swagger (discovered via logs/docs)
- **GraphQL**: Schema introspection and operation discovery
- **SOAP**: WSDL parsing with operation and message extraction
- **Event-driven**: AsyncAPI specification support
- **Legacy Systems**: Confluence docs, Postman collections, HAR files

#### Search Results
- **Endpoint Details**: Method, path, parameters, response schemas
- **Service Context**: System, owners, documentation links
- **Performance Metrics**: Latency, availability, rate limits
- **Citations**: Source references with line numbers and context

### 2. Intelligent Ranking (SOLAR-style)

#### Ranking Factors
- **Text Relevance**: Vector similarity + keyword matching
- **Performance**: Latency (P50, P95), availability SLOs
- **Geographic**: Regional proximity and edge awareness
- **Freshness**: Specification update recency
- **Permission Fit**: Scope availability for user
- **Historical Success**: Past selection success rates
- **Popularity**: Call volume and usage patterns

#### Ranking Algorithm
```
Final Score = w1*TextRelevance + w2*Performance + w3*Geography + 
             w4*Freshness + w5*PermissionFit + w6*HistoricalSuccess + w7*Popularity
```

### 3. One-Click Onboarding

#### Onboarding Flow
1. **User Selection**: Choose API endpoint(s) and environment
2. **Scope Assignment**: Automatic scope mapping based on user groups
3. **Jira Ticket Creation**: Automated Epic + child tasks creation
4. **Access Provisioning**: OIDC client creation in Keycloak
5. **Status Tracking**: Real-time updates via SSE/WebSocket

#### Jira Integration
- **Epic Creation**: High-level onboarding request
- **Child Tasks**: 
  - AD Group assignment
  - Gateway configuration
  - Network access
  - Security review
- **Status Updates**: Webhook integration for real-time updates

#### Keycloak Integration
- **Client Creation**: Automatic OIDC client setup
- **Scope Mapping**: Enterprise AD group to scope mapping
- **Token Issuance**: JWT tokens with appropriate scopes

### 4. API Documentation & Testing

#### Documentation Features
- **Interactive Examples**: cURL, JavaScript, Java, Python
- **Schema Visualization**: Request/response schemas
- **Error Handling**: Common error codes and responses
- **Rate Limiting**: Default and custom rate limit information

#### Try-It Console
- **Live Testing**: Execute API calls against sandbox environments
- **Authentication**: OIDC token integration
- **Response Inspection**: Full request/response details
- **History**: Track API call history

### 5. Enterprise Integration

#### Identity Management
- **Keycloak Realm**: Multi-tenant support
- **SCIM Integration**: Azure AD, Okta synchronization
- **Group Mapping**: AD groups to API scopes
- **Service Accounts**: Automated provisioning

#### Security & Compliance
- **PII Detection**: Automatic PII flagging at endpoint level
- **Row-Level Security**: Database-level access control
- **Audit Logging**: Complete audit trail for all actions
- **Rate Limiting**: Tenant-specific rate limiting

## Data Architecture

### Hybrid Database Approach

CatalystAI uses a hybrid database architecture that separates concerns for optimal performance and scalability:

#### PostgreSQL (Relational Data)
- **Purpose**: Store structured business data, relationships, and metadata
- **Tables**: Systems, Services, APIs, Endpoints, Scopes, Documents
- **Benefits**: ACID compliance, complex joins, transaction support
- **Use Cases**: CRUD operations, business logic, reporting

#### Vector Database (Semantic Search)
- **Purpose**: Store and search document embeddings for semantic similarity
- **Options**: Weaviate, Qdrant, or Pinecone
- **Benefits**: Optimized for vector operations, horizontal scaling, specialized indexes
- **Use Cases**: Semantic search, similarity matching, RAG operations

#### Redis (Cache & Queue)
- **Purpose**: Session storage, caching, and message queuing
- **Benefits**: Sub-millisecond response times, pub/sub capabilities
- **Use Cases**: Session management, search result caching, background job queues

### Vector Database Selection

#### Weaviate (Recommended)
- **Pros**: Open-source, GraphQL API, schema validation, multi-tenancy
- **Cons**: Requires more infrastructure management
- **Best For**: Self-hosted deployments, complex schemas

#### Qdrant
- **Pros**: High performance, Rust-based, excellent filtering
- **Cons**: Smaller ecosystem, less documentation
- **Best For**: High-performance requirements, custom filtering

#### Pinecone
- **Pros**: Fully managed, enterprise features, excellent scaling
- **Cons**: Vendor lock-in, higher costs
- **Best For**: Enterprise deployments, managed service preference

### Benefits of Hybrid Architecture

#### Performance
- **Optimized Storage**: Each database optimized for its specific use case
- **Independent Scaling**: Vector search can scale independently of relational data
- **Specialized Indexes**: Vector databases provide optimized similarity search indexes

#### Flexibility
- **Technology Choice**: Can select best vector database for specific requirements
- **Migration Path**: Easy to switch vector databases without affecting business logic
- **Multi-Cloud**: Vector database can be in different cloud/region than PostgreSQL

#### Operational
- **Separation of Concerns**: Clear boundaries between data types
- **Backup Strategies**: Different backup and recovery strategies for each database
- **Monitoring**: Specialized monitoring for each database type

## Data Model

#### Systems
- **Purpose**: Logical grouping of related services
- **Attributes**: Name, domain, criticality, owners
- **Relationships**: Contains multiple services

#### Services
- **Purpose**: Individual microservices or applications
- **Attributes**: Name, repository URL, owners, system association
- **Relationships**: Belongs to system, contains multiple APIs

#### APIs
- **Purpose**: API specifications and metadata
- **Attributes**: Style (REST/GraphQL/SOAP), name, specification reference
- **Relationships**: Belongs to service, contains multiple endpoints

#### Endpoints
- **Purpose**: Individual API operations
- **Attributes**: Method, path, operation ID, scopes, PII flags
- **Relationships**: Belongs to API, associated with scopes

#### Scopes
- **Purpose**: Permission definitions
- **Attributes**: Name, description
- **Relationships**: Associated with endpoints and users

#### Documents
- **Purpose**: Source documentation and specifications
- **Attributes**: Type, URI, checksum, indexing timestamp
- **Relationships**: Associated with APIs

#### Document Chunks
- **Purpose**: Vector searchable content chunks
- **Attributes**: Content, source reference, chunk_id (for vector DB reference)
- **Relationships**: Belongs to document, stored in vector database

### Database Schema

#### PostgreSQL Schema (Relational Data)
The platform uses PostgreSQL for structured business data with the following design principles:
- **Normalization**: Proper relational structure with foreign key relationships
- **Performance**: Strategic indexing on frequently queried fields
- **Scalability**: Efficient query patterns and connection pooling
- **Flexibility**: JSON fields for varying specification formats

#### Vector Database Schema (Semantic Search)
The vector database stores document chunks and embeddings:
- **Collections**: Separate collections for different document types
- **Metadata**: Rich filtering on document properties
- **Indexes**: HNSW or IVFFlat indexes for fast similarity search
- **Scalability**: Horizontal scaling independent of relational data

## API Endpoints

### GraphQL Schema

#### Queries
- `searchApis`: Main search endpoint with ranking and citations
- `getApi`: Detailed API information
- `getEndpoints`: Endpoint listing with filters
- `getSystems`: System hierarchy

#### Mutations
- `createOnboardingRequest`: Initiate onboarding workflow
- `updateApi`: Modify API metadata
- `createFeedback`: Submit search feedback

### REST Endpoints

#### Search
- `GET /api/v1/search`: Search APIs with query parameters
- `GET /api/v1/apis/{id}`: Get API details
- `GET /api/v1/endpoints`: List endpoints with filters

#### Onboarding
- `POST /api/v1/onboarding`: Create onboarding request
- `GET /api/v1/onboarding/{id}`: Get onboarding status
- `GET /api/v1/onboarding/{id}/status`: Stream status updates

#### Admin
- `POST /api/v1/admin/ingest`: Ingest new specifications
- `PUT /api/v1/admin/apis/{id}`: Update API metadata
- `DELETE /api/v1/admin/apis/{id}`: Remove API

## Ingestion Pipeline

### Supported Formats

#### OpenAPI/Swagger
- **Parser**: Standard OpenAPI 3.0+ support
- **Extraction**: Endpoints, schemas, security requirements
- **Validation**: Schema validation and error reporting

#### GraphQL
- **Parser**: Introspection query execution
- **Extraction**: Types, queries, mutations, subscriptions
- **Schema**: GraphQL SDL generation

#### SOAP/WSDL
- **Parser**: Zeep library for WSDL parsing
- **Extraction**: Operations, messages, XSD schemas
- **Examples**: Generated SOAP envelope examples

#### Non-Swagger REST
- **Sources**: Confluence, Markdown, Postman, HAR files
- **Parsing**: Regex patterns for endpoint discovery
- **Validation**: Manual review and approval workflow

#### Postman Collections
- **Format**: Postman v2.1 collection format
- **Extraction**: Requests, environments, variables
- **Conversion**: OpenAPI specification generation

### Ingestion Process

1. **Document Upload**: Via admin interface or API
2. **Format Detection**: Automatic format identification
3. **Parsing**: Format-specific parser execution
4. **Normalization**: Standardized data structure
5. **Validation**: Data quality checks
6. **Indexing**: Database insertion and vector embedding
7. **Notification**: Real-time updates to search index

## Search & Ranking

### Search Pipeline

1. **Query Processing**: Natural language understanding and query expansion
2. **Hybrid Retrieval**: 
   - BM25 search on PostgreSQL (structured data)
   - Vector search on vector database (semantic similarity)
   - Merge and deduplicate results (top 50)
3. **Re-ranking**: Cross-encoder model (top 10)
4. **Signal Application**: Performance, geographic, permission factors
5. **Final Ranking**: Weighted score calculation
6. **Citation Generation**: Source reference mapping with chunk details

### Vector Search

- **Model**: all-MiniLM-L6-v2 or E5-small (768 dimensions)
- **Vector Database**: Weaviate, Qdrant, or Pinecone with HNSW indexes
- **Similarity**: Cosine similarity for semantic matching
- **Performance**: Optimized for sub-100ms response times
- **Scalability**: Independent scaling of vector search infrastructure

### Re-ranking

- **Model**: Cross-encoder for relevance scoring
- **Features**: Query-endpoint semantic similarity
- **Training**: Fine-tuned on domain-specific data
- **Performance**: Batch processing for efficiency

## Onboarding Workflow

### Workflow Steps

1. **Request Initiation**: User selects APIs and environment
2. **Scope Assignment**: Automatic scope mapping
3. **Jira Creation**: Epic and task creation
4. **Approval Process**: Stakeholder approvals
5. **Access Provisioning**: Keycloak client setup
6. **Gateway Configuration**: API gateway setup
7. **Testing**: Sandbox environment testing
8. **Production**: Production access activation

### Jira Templates

#### Epic Template
- **Title**: API Onboarding Request - {Service Name}
- **Description**: Detailed onboarding requirements
- **Labels**: api-onboarding, {environment}, {priority}

#### Task Templates
- **AD Group Assignment**: User group creation and mapping
- **Gateway Configuration**: API gateway routing setup
- **Network Access**: Firewall and network configuration
- **Security Review**: Security assessment and approval

### Status Tracking

- **Real-time Updates**: SSE/WebSocket for live status
- **Milestone Tracking**: Progress through workflow stages
- **Notification System**: Email and in-app notifications
- **Audit Trail**: Complete action history

## Security & Compliance

### Authentication & Authorization

- **OIDC Integration**: Keycloak-based authentication
- **Scope-based Access**: Fine-grained permission control
- **Row-level Security**: Database-level access control
- **API Rate Limiting**: Tenant-specific rate limits

### Data Protection

- **PII Detection**: Automatic sensitive data identification
- **Data Masking**: PII obfuscation in examples
- **Encryption**: Data at rest and in transit
- **Audit Logging**: Complete audit trail

### Compliance Features

- **GDPR Compliance**: Data retention and deletion policies
- **SOC 2**: Security controls and monitoring
- **API Security**: OWASP API Security Top 10 compliance
- **Access Reviews**: Periodic access review workflows

## Monitoring & Observability

### Metrics

- **Application Metrics**: Response times, error rates, throughput
- **Business Metrics**: Search success rates, onboarding completion
- **Infrastructure Metrics**: Database performance, cache hit rates
- **Custom Metrics**: API usage patterns, user engagement

### Logging

- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARN, ERROR
- **Log Aggregation**: Centralized log collection
- **Log Retention**: Configurable retention policies

### Tracing

- **Distributed Tracing**: Request flow across services
- **Performance Analysis**: Bottleneck identification
- **Dependency Mapping**: Service dependency visualization
- **Error Tracking**: Error propagation analysis

### Health Checks

- **Service Health**: Individual service status
- **Dependency Health**: Database, cache, external services
- **Custom Health**: Business logic health indicators
- **Health Dashboard**: Centralized health monitoring

## Performance & Scalability

### Performance Targets

- **Search Response**: < 200ms for 95th percentile
- **Onboarding Creation**: < 5 seconds for ticket creation
- **API Response**: < 100ms for 95th percentile
- **Vector Search**: < 50ms for similarity queries

### Scalability Features

- **Horizontal Scaling**: Stateless service design
- **Database Sharding**: Multi-tenant data isolation
- **Caching Strategy**: Multi-layer caching (Redis, application)
- **Async Processing**: Background job processing

### Optimization Strategies

- **Query Optimization**: Database query tuning
- **Index Strategy**: Strategic database indexing
- **Connection Pooling**: Efficient database connections
- **Batch Processing**: Bulk operations for efficiency

## Deployment & DevOps

### Local Development

- **Docker Compose**: Complete local environment
- **Hot Reloading**: Development server configurations
- **Mock Services**: External service mocking
- **Seed Data**: Development data population

### CI/CD Pipeline

- **Automated Testing**: Unit, integration, and E2E tests
- **Code Quality**: Linting, formatting, security scanning
- **Automated Deployment**: Staging and production deployments
- **Rollback Strategy**: Automated rollback capabilities

### Production Deployment

- **Kubernetes**: Container orchestration
- **Helm Charts**: Application packaging
- **Service Mesh**: Istio for service communication
- **Monitoring Stack**: Prometheus, Grafana, Jaeger

## Testing Strategy

### Test Types

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **Contract Tests**: API contract validation
- **E2E Tests**: Complete user journey testing

### Test Data

- **Mock Services**: External service simulation
- **Test Databases**: Isolated test data
- **API Specifications**: Sample OpenAPI, WSDL, GraphQL
- **User Scenarios**: Realistic user workflows

### Test Automation

- **CI Integration**: Automated test execution
- **Test Reporting**: Comprehensive test results
- **Coverage Metrics**: Code coverage tracking
- **Performance Testing**: Load and stress testing

## Success Metrics

### Technical Metrics

- **Search Accuracy**: Precision@k, MRR (Mean Reciprocal Rank)
- **Response Time**: API response latency
- **Availability**: System uptime and reliability
- **Error Rate**: Error frequency and types

### Business Metrics

- **User Adoption**: Active users and engagement
- **Onboarding Success**: Completion rates and time
- **API Discovery**: Search volume and success rates
- **User Satisfaction**: Feedback scores and ratings

### Operational Metrics

- **Deployment Frequency**: Release cadence
- **Lead Time**: Feature development to production
- **Mean Time to Recovery**: Incident resolution time
- **Change Failure Rate**: Deployment success rate

## Future Roadmap

### Phase 2 Features

- **Graph Visualization**: API dependency mapping
- **Advanced Analytics**: Usage pattern analysis
- **Machine Learning**: Improved ranking algorithms
- **Mobile Application**: Native mobile experience

### Phase 3 Features

- **Edge Computing**: Offline edge bundles
- **AI Assistant**: Conversational API discovery
- **Integration Hub**: Third-party tool integration
- **Advanced Security**: Zero-trust architecture

### Long-term Vision

- **Global API Marketplace**: Cross-organization API sharing
- **AI-Powered Development**: Code generation from APIs
- **Predictive Analytics**: Proactive API recommendations
- **Industry Standards**: Open API discovery protocols

## Conclusion

CatalystAI represents a comprehensive solution for enterprise API discovery and onboarding challenges. By combining modern AI/ML techniques with enterprise-grade security and integration capabilities, the platform provides a seamless experience for both API consumers and providers.

The modular architecture ensures scalability and maintainability, while the focus on user experience and automation drives adoption and efficiency. The platform's ability to handle both modern and legacy API formats makes it suitable for organizations at any stage of their API modernization journey.

With its strong foundation in open standards and enterprise integration patterns, CatalystAI is positioned to become the de facto standard for enterprise API discovery and onboarding.
