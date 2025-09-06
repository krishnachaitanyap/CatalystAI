"""
API Identification Prompts for CatalystAI
Comprehensive prompts for LLM-based API discovery and classification
"""

from typing import Dict, List, Any

class APIIdentificationPrompts:
    """Collection of prompts for API identification and classification"""
    
    @staticmethod
    def get_endpoint_extraction_prompt() -> str:
        """Prompt for extracting API endpoints from documentation"""
        return """
        You are an expert API analyst. Extract API endpoints from the following content.
        
        For each endpoint, identify and provide:
        
        1. **HTTP Method**: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
        2. **Path/URL Pattern**: The endpoint path with parameters
        3. **Operation ID/Name**: Unique identifier for the operation
        4. **Summary**: Brief description of what the endpoint does
        5. **Description**: Detailed explanation of functionality
        6. **Parameters**: 
           - Path parameters (required/optional)
           - Query parameters (required/optional)
           - Header parameters
           - Request body schema
        7. **Response Schemas**: Expected response formats and status codes
        8. **Security Requirements**: Authentication, authorization, scopes
        9. **Rate Limiting**: Any rate limiting information
        10. **PII Flags**: Whether the endpoint handles sensitive data
        11. **Business Domain**: Category/domain of the operation
        12. **Dependencies**: Other services or APIs this depends on
        
        Format your response as structured JSON with clear endpoint definitions.
        Be thorough and accurate in your analysis.
        
        Content to analyze:
        {content}
        """
    
    @staticmethod
    def get_api_classification_prompt() -> str:
        """Prompt for classifying API specifications"""
        return """
        You are an expert API architect. Classify the following API specification.
        
        Provide a comprehensive classification covering:
        
        1. **API Style**: REST, GraphQL, SOAP, gRPC, Event-driven, or hybrid
        2. **Authentication Methods**: 
           - OAuth 2.0 flows
           - API keys
           - JWT tokens
           - Basic auth
           - Custom schemes
        3. **Data Formats**: JSON, XML, Protocol Buffers, MessagePack, etc.
        4. **Versioning Strategy**: 
           - URL versioning (/v1, /v2)
           - Header versioning
           - Query parameter versioning
           - Content negotiation
        5. **Base URL Patterns**: Common URL structures and conventions
        6. **Error Handling Approach**: 
           - HTTP status codes
           - Error response formats
           - Error categorization
        7. **Documentation Standards**: 
           - OpenAPI/Swagger
           - GraphQL introspection
           - Custom documentation
        8. **Testing Patterns**: 
           - Test endpoints
           - Mock data
           - Testing utilities
        9. **Performance Characteristics**: 
           - Expected response times
           - Rate limiting
           - Caching strategies
        10. **Security Features**: 
            - CORS policies
            - Input validation
            - Data encryption
            - Audit logging
        
        Provide examples and evidence from the specification to support your classification.
        
        API Specification to classify:
        {content}
        """
    
    @staticmethod
    def get_business_context_prompt() -> str:
        """Prompt for analyzing business context of APIs"""
        return """
        You are a business analyst specializing in API ecosystems. Analyze the business context of this API.
        
        Extract and analyze:
        
        1. **Primary Business Domain**: 
           - Industry sector (banking, healthcare, e-commerce, etc.)
           - Business function (customer management, payments, reporting, etc.)
           - Core business processes supported
        
        2. **User Personas and Use Cases**:
           - Primary users (developers, business users, end customers)
           - Common use cases and workflows
           - Integration scenarios
        
        3. **Data Entities and Relationships**:
           - Core business objects
           - Data hierarchies and dependencies
           - Master data management
        
        4. **Business Processes Supported**:
           - Workflow steps
           - Business rules and validations
           - Process automation opportunities
        
        5. **Integration Patterns**:
           - System-to-system integration
           - Third-party service integration
           - Data synchronization patterns
        
        6. **Compliance Requirements**:
           - Regulatory frameworks (GDPR, HIPAA, PCI-DSS, etc.)
           - Industry standards
           - Audit and reporting requirements
        
        7. **Performance Expectations**:
           - Business SLAs
           - Peak usage patterns
           - Scalability requirements
        
        8. **Security Considerations**:
           - Data sensitivity levels
           - Access control requirements
           - Threat modeling considerations
        
        9. **Business Value Metrics**:
           - Cost savings
           - Efficiency improvements
           - Revenue generation opportunities
        
        10. **Strategic Alignment**:
            - Business objectives supported
            - Digital transformation initiatives
            - Competitive advantages
        
        Provide business-relevant insights that would help stakeholders understand the API's value and impact.
        
        API Content to analyze:
        {content}
        """
    
    @staticmethod
    def get_legacy_migration_prompt() -> str:
        """Prompt for analyzing legacy APIs for migration"""
        return """
        You are an API modernization expert. Analyze this legacy API documentation for migration opportunities.
        
        Assess and provide recommendations for:
        
        1. **Current API Patterns and Conventions**:
           - Legacy patterns identified
           - Outdated standards in use
           - Technical debt indicators
        
        2. **Deprecated or Legacy Endpoints**:
           - Endpoints marked as deprecated
           - Unused or low-usage endpoints
           - Endpoints with security vulnerabilities
        
        3. **Migration Paths and Alternatives**:
           - Modern API standards to adopt
           - Alternative approaches for each legacy pattern
           - Backward compatibility strategies
        
        4. **Backward Compatibility Requirements**:
           - Breaking changes assessment
           - Version migration strategies
           - Client update requirements
        
        5. **Modern API Standards Alignment**:
           - OpenAPI 3.0+ compliance
           - GraphQL adoption opportunities
           - Event-driven architecture possibilities
        
        6. **Documentation Gaps and Improvements**:
           - Missing documentation areas
           - Documentation quality improvements
           - Interactive documentation opportunities
        
        7. **Testing and Validation Needs**:
           - Test coverage gaps
           - Automated testing opportunities
           - Performance testing requirements
        
        8. **Performance Optimization Opportunities**:
           - Bottlenecks identification
           - Caching strategies
           - Response time improvements
        
        9. **Security Modernization**:
           - Authentication improvements
           - Authorization enhancements
           - Security best practices implementation
        
        10. **Monitoring and Observability**:
            - Logging improvements
            - Metrics collection
            - Alerting and monitoring
        
        11. **Cost Optimization**:
            - Infrastructure improvements
            - Resource utilization optimization
            - Operational efficiency gains
        
        12. **Risk Assessment**:
            - Migration risks
            - Business impact assessment
            - Rollback strategies
        
        Provide a prioritized roadmap for modernization with estimated effort and business value.
        
        Legacy API Documentation to analyze:
        {content}
        """
    
    @staticmethod
    def get_api_discovery_prompt() -> str:
        """Prompt for discovering APIs from various sources"""
        return """
        You are an API discovery specialist. Analyze the following content to discover and catalog APIs.
        
        Discover and catalog:
        
        1. **API Endpoints**:
           - HTTP methods and paths
           - URL patterns and conventions
           - Parameter structures
        
        2. **API Specifications**:
           - OpenAPI/Swagger documents
           - GraphQL schemas
           - SOAP/WSDL definitions
           - Custom specification formats
        
        3. **API Documentation**:
           - Technical documentation
           - User guides and tutorials
           - Code examples and samples
           - Integration guides
        
        4. **API Metadata**:
           - Service names and descriptions
           - Version information
           - Owner and contact details
           - Tags and categories
        
        5. **Integration Points**:
           - Webhook endpoints
           - Callback URLs
           - Event subscriptions
           - Data synchronization points
        
        6. **Authentication and Security**:
           - Authentication methods
           - API keys and tokens
           - OAuth flows
           - Security requirements
        
        7. **Data Models**:
           - Request/response schemas
           - Data types and formats
           - Validation rules
           - Business entities
        
        8. **Performance Characteristics**:
           - Response time expectations
           - Rate limiting information
           - Caching strategies
           - Scalability indicators
        
        9. **Business Context**:
           - Use cases and scenarios
           - Business processes supported
           - User personas
           - Value propositions
        
        10. **Technical Details**:
            - Programming languages
            - Frameworks and libraries
            - Infrastructure requirements
            - Deployment patterns
        
        Provide a comprehensive catalog of discovered APIs with all relevant details.
        
        Content to analyze for API discovery:
        {content}
        """
    
    @staticmethod
    def get_api_quality_assessment_prompt() -> str:
        """Prompt for assessing API quality and maturity"""
        return """
        You are an API quality expert. Assess the quality and maturity of this API.
        
        Evaluate and score:
        
        1. **API Design Quality** (0-10):
           - RESTful principles adherence
           - Resource naming conventions
           - HTTP method usage
           - Status code usage
           - Error handling
        
        2. **Documentation Quality** (0-10):
           - Completeness of documentation
           - Code examples quality
           - Interactive documentation
           - API reference accuracy
           - Getting started guides
        
        3. **Security Implementation** (0-10):
           - Authentication mechanisms
           - Authorization controls
           - Input validation
           - Data encryption
           - Security headers
        
        4. **Performance and Reliability** (0-10):
           - Response time optimization
           - Rate limiting implementation
           - Caching strategies
           - Error handling
           - Availability guarantees
        
        5. **Developer Experience** (0-10):
           - SDK availability
           - Code generation
           - Testing tools
           - Debugging support
           - Community resources
        
        6. **Standards Compliance** (0-10):
           - OpenAPI specification
           - GraphQL standards
           - Industry best practices
           - Regulatory compliance
           - Accessibility standards
        
        7. **Monitoring and Observability** (0-10):
           - Logging implementation
           - Metrics collection
           - Alerting systems
           - Performance monitoring
           - Error tracking
        
        8. **Testing and Validation** (0-10):
           - Test coverage
           - Automated testing
           - Performance testing
           - Security testing
           - Integration testing
        
        9. **Versioning and Evolution** (0-10):
           - Versioning strategy
           - Backward compatibility
           - Deprecation policies
           - Migration guides
           - Change management
        
        10. **Business Value** (0-10):
            - Problem solving capability
            - User adoption potential
            - Integration ease
            - Cost effectiveness
            - Strategic alignment
        
        Provide an overall quality score and specific recommendations for improvement.
        
        API to assess:
        {content}
        """
    
    @staticmethod
    def get_api_integration_guide_prompt() -> str:
        """Prompt for generating API integration guides"""
        return """
        You are an API integration expert. Create a comprehensive integration guide for this API.
        
        Generate an integration guide covering:
        
        1. **Getting Started**:
           - Prerequisites and requirements
           - Account setup and API key generation
           - Environment configuration
           - First API call
        
        2. **Authentication Setup**:
           - Authentication methods explained
           - Token generation and management
           - Security best practices
           - Common authentication errors
        
        3. **Core Concepts**:
           - API architecture overview
           - Data models and schemas
           - Request/response patterns
           - Error handling strategies
        
        4. **Integration Patterns**:
           - Synchronous vs asynchronous calls
           - Webhook implementation
           - Batch operations
           - Real-time data streaming
        
        5. **Code Examples**:
           - cURL examples
           - JavaScript/Node.js examples
           - Python examples
           - Java examples
           - Other language examples
        
        6. **SDK Usage**:
           - Available SDKs
           - Installation and setup
           - Basic usage examples
           - Advanced features
        
        7. **Testing and Debugging**:
           - Testing strategies
           - Common issues and solutions
           - Debugging tools
           - Performance testing
        
        8. **Best Practices**:
           - Rate limiting considerations
           - Error handling patterns
           - Security recommendations
           - Performance optimization
        
        9. **Troubleshooting**:
           - Common error codes
           - Debugging steps
           - Support resources
           - Community forums
        
        10. **Advanced Topics**:
            - Webhook security
            - Data validation
            - Caching strategies
            - Monitoring and alerting
        
        Make the guide practical and easy to follow for developers of all skill levels.
        
        API to create integration guide for:
        {content}
        """
    
    @staticmethod
    def get_all_prompts() -> Dict[str, str]:
        """Get all available prompts"""
        return {
            "endpoint_extraction": APIIdentificationPrompts.get_endpoint_extraction_prompt(),
            "api_classification": APIIdentificationPrompts.get_api_classification_prompt(),
            "business_context": APIIdentificationPrompts.get_business_context_prompt(),
            "legacy_migration": APIIdentificationPrompts.get_legacy_migration_prompt(),
            "api_discovery": APIIdentificationPrompts.get_api_discovery_prompt(),
            "api_quality_assessment": APIIdentificationPrompts.get_api_quality_assessment_prompt(),
            "api_integration_guide": APIIdentificationPrompts.get_api_integration_guide_prompt()
        }
    
    @staticmethod
    def get_prompt_by_name(prompt_name: str) -> str:
        """Get a specific prompt by name"""
        prompts = APIIdentificationPrompts.get_all_prompts()
        return prompts.get(prompt_name, "Prompt not found")
    
    @staticmethod
    def get_prompt_names() -> List[str]:
        """Get list of all available prompt names"""
        return list(APIIdentificationPrompts.get_all_prompts().keys())
