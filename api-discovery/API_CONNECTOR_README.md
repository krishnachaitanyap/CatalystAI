# 🔗 CatalystAI API Connector

A comprehensive connector that converts various API specification formats (Swagger/OpenAPI, WSDL) into a common structure for vector database storage and intelligent API discovery.

## 🚀 Features

### Supported Formats
- **Swagger/OpenAPI 2.0 & 3.0** - JSON and YAML formats
- **WSDL 1.1 & 2.0** - XML format
- **GraphQL Schema** - (Coming soon)
- **AsyncAPI** - (Coming soon)
- **RAML** - (Coming soon)

### Key Capabilities
- **Automatic Format Detection** - Detects API type from file extension and content
- **Common Structure Conversion** - Converts all formats to standardized schema
- **ChromaDB Integration** - Stores converted specs in vector database
- **Comprehensive Metadata** - Extracts authentication, rate limits, endpoints, etc.
- **Intelligent Categorization** - Automatically categorizes APIs by functionality
- **Integration Guidelines** - Generates step-by-step integration instructions
- **Best Practices** - Provides security and implementation best practices

## 📋 Common API Structure

The connector converts all API specifications to a standardized structure:

```python
@dataclass
class CommonAPISpec:
    api_name: str                    # API name/title
    version: str                     # API version
    description: str                 # API description
    base_url: str                    # Base URL/endpoint
    category: str                    # Auto-categorized (payment, auth, etc.)
    endpoints: List[Dict[str, Any]]  # All API endpoints
    authentication: Dict[str, Any]    # Auth methods and schemes
    rate_limits: Dict[str, Any]      # Rate limiting information
    pricing: Optional[str]           # Pricing information
    sdk_languages: List[str]         # Supported SDK languages
    documentation_url: str           # Documentation URL
    integration_steps: List[str]     # Step-by-step integration guide
    best_practices: List[str]        # Security and implementation practices
    common_use_cases: List[str]      # Common use cases
    tags: List[str]                  # API tags
    contact_info: Dict[str, str]     # Contact information
    license_info: Dict[str, str]     # License information
    external_docs: List[Dict[str, str]] # External documentation links
    examples: List[Dict[str, Any]]   # Request/response examples
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- ChromaDB
- Required dependencies

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Dependencies
```
chromadb==0.4.22
openai==1.12.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
pyyaml==6.0.1
lxml==4.9.3
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp env.template .env

# Edit .env file with your API keys
# OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Convert Swagger/OpenAPI File
```bash
# Convert Swagger JSON file
python api_connector.py convert sample_swagger.json

# Convert OpenAPI YAML file
python api_connector.py convert api_spec.yaml --type swagger

# Auto-detect format
python api_connector.py convert api_spec.json
```

### 3. Convert WSDL File
```bash
# Convert WSDL file
python api_connector.py convert service.wsdl --type wsdl

# Auto-detect WSDL
python api_connector.py convert service.xml
```

### 4. Convert from URL
```bash
# Convert from Swagger URL
python api_connector.py convert-url https://api.example.com/swagger.json

# Convert from WSDL URL
python api_connector.py convert-url https://service.example.com/service.wsdl
```

### 5. List Stored APIs
```bash
# List all converted APIs
python api_connector.py list
```

## 📚 Command Reference

### Convert Command
```bash
python api_connector.py convert <file_path> [--type <swagger|wsdl|auto>]
```

**Options:**
- `file_path`: Path to API specification file
- `--type`: API type (swagger, wsdl, auto) - defaults to auto-detect

**Supported File Extensions:**
- Swagger: `.json`, `.yaml`, `.yml`
- WSDL: `.wsdl`, `.xml`

### Convert URL Command
```bash
python api_connector.py convert-url <url> [--type <swagger|wsdl|auto>]
```

**Options:**
- `url`: URL to API specification
- `--type`: API type (swagger, wsdl, auto) - defaults to auto-detect

### List Command
```bash
python api_connector.py list
```

Lists all API specifications stored in ChromaDB with metadata.

## 🔧 API Type Detection

### Automatic Detection
The connector automatically detects API type based on:

1. **File Extension:**
   - `.wsdl`, `.xml` → WSDL
   - `.json`, `.yaml`, `.yml` → Swagger/OpenAPI

2. **Content Analysis:**
   - `<wsdl:` or `<definitions` → WSDL
   - `"swagger"` or `"openapi"` → Swagger/OpenAPI

3. **URL Analysis:**
   - `.wsdl` → WSDL
   - `.json`, `.yaml`, `.yml` → Swagger/OpenAPI

### Manual Override
Use `--type` parameter to override automatic detection:
```bash
python api_connector.py convert file.xml --type swagger
```

## 📊 Swagger/OpenAPI Processing

### Supported Versions
- **OpenAPI 3.0.x** (3.0.0, 3.0.1, 3.0.2, 3.0.3)
- **Swagger 2.0**

### Extracted Information
- **Basic Info**: Title, version, description, contact, license
- **Endpoints**: Paths, methods, parameters, responses
- **Authentication**: Security schemes, OAuth flows, API keys
- **Rate Limits**: From extensions and annotations
- **Examples**: Request/response examples
- **External Docs**: Documentation links

### Authentication Extraction
- **API Key**: Header, query parameter, cookie
- **OAuth 2.0**: Authorization code, client credentials, implicit flows
- **Basic Auth**: Username/password authentication
- **Bearer Token**: JWT and other token-based auth

## 🔧 WSDL Processing

### Supported Versions
- **WSDL 1.1**
- **WSDL 2.0**

### Extracted Information
- **Service Info**: Service name, description, location
- **Operations**: SOAP operations and actions
- **Bindings**: SOAP bindings and protocols
- **Types**: XML schema definitions
- **Messages**: Input/output message definitions

### SOAP-Specific Features
- **SOAP Actions**: Extracted from binding operations
- **Schema Types**: Complex types and elements
- **Authentication**: WS-Security, Basic Auth, Certificate auth
- **Protocols**: SOAP 1.1, SOAP 1.2, HTTP binding

## 🎯 Intelligent Categorization

APIs are automatically categorized based on:

### Category Detection
- **Payment**: stripe, paypal, square, billing, charge
- **Authentication**: auth, oauth, jwt, login, user, identity
- **Communication**: email, sms, notification, message, chat, slack
- **Storage**: storage, file, upload, s3, cloud, bucket
- **Analytics**: analytics, tracking, metrics, stats, report
- **Social**: social, facebook, twitter, linkedin, instagram
- **E-commerce**: shop, store, product, order, cart, inventory
- **Finance**: finance, banking, accounting, transaction, wallet
- **AI**: ai, ml, machine, learning, neural, openai
- **Maps**: map, location, geocoding, directions, places

### Endpoint Analysis
- Analyzes endpoint summaries and descriptions
- Matches against category keywords
- Falls back to "general" category if no match

## 🔗 ChromaDB Integration

### Storage Structure
- **Collection**: `api_specifications`
- **Documents**: Comprehensive text representation
- **Metadata**: Full API specification data
- **IDs**: Unique identifiers with timestamps

### Metadata Conversion
- Complex data structures converted to JSON strings
- Lists and dictionaries preserved as strings
- Timestamps added for tracking

### Retrieval
- Full API specifications retrievable
- Searchable by API name, category, description
- Compatible with vector search and filtering

## 🚀 Integration with API Discovery

### Vector Search Integration
The converted API specifications integrate seamlessly with the intelligent search system:

```bash
# Search converted APIs
python intelligent_search.py "I need payment processing APIs"

# List available APIs
python intelligent_search.py --list-apis
```

### Search Capabilities
- **Semantic Search**: Find APIs by functionality
- **Category Filtering**: Filter by API categories
- **Endpoint Matching**: Match specific endpoint needs
- **Authentication Filtering**: Find APIs with specific auth methods

## 📝 Example Usage

### Convert Sample Files
```bash
# Convert sample Swagger file
python api_connector.py convert sample_swagger.json

# Convert sample WSDL file
python api_connector.py convert sample_wsdl.xml --type wsdl
```

### Convert Real APIs
```bash
# Convert GitHub API
python api_connector.py convert-url https://api.github.com/swagger.json

# Convert Stripe API
python api_connector.py convert-url https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json
```

### List and Search
```bash
# List all converted APIs
python api_connector.py list

# Search for payment APIs
python intelligent_search.py "payment processing APIs for e-commerce"
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION=api_specifications
```

### Custom Categories
Extend the categorization logic by modifying the `_categorize_api` method in `SwaggerConnector`:

```python
def _categorize_api(self, title: str, endpoints: List[Dict[str, Any]]) -> str:
    # Add your custom category logic here
    custom_categories = {
        'blockchain': ['blockchain', 'crypto', 'bitcoin', 'ethereum'],
        'iot': ['iot', 'internet of things', 'sensor', 'device']
    }
    # ... existing logic
```

## 🐛 Troubleshooting

### Common Issues

#### 1. File Parsing Errors
```
Error: Error parsing Swagger file: Expecting value: line 1 column 1 (char 0)
```
**Solution**: Check file format and encoding. Ensure JSON/YAML is valid.

#### 2. WSDL Namespace Issues
```
Error: Error parsing WSDL file: namespace not found
```
**Solution**: WSDL file may have custom namespaces. Check namespace declarations.

#### 3. ChromaDB Connection Issues
```
Error: Error initializing ChromaDB: Connection refused
```
**Solution**: Ensure ChromaDB is running and accessible.

#### 4. Missing Dependencies
```
ModuleNotFoundError: No module named 'yaml'
```
**Solution**: Install missing dependencies: `pip install pyyaml lxml`

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=1
python api_connector.py convert sample_swagger.json
```

## 🔮 Future Enhancements

### Planned Features
- **GraphQL Schema Support** - Parse GraphQL schema files
- **AsyncAPI Support** - Process AsyncAPI specifications
- **RAML Support** - Handle RAML API specifications
- **Batch Processing** - Convert multiple files at once
- **API Versioning** - Handle multiple API versions
- **Custom Extractors** - Plugin system for custom formats
- **Validation** - Validate converted specifications
- **Export Options** - Export to different formats

### Integration Improvements
- **Real-time Updates** - Monitor API spec changes
- **Webhook Integration** - Automatic conversion triggers
- **API Gateway Integration** - Direct integration with API gateways
- **Documentation Generation** - Generate documentation from specs

## 📚 Resources

### Documentation
- [Swagger/OpenAPI Specification](https://swagger.io/specification/)
- [WSDL Specification](https://www.w3.org/TR/wsdl)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Sample Files
- `sample_swagger.json` - Sample Swagger 2.0 specification
- `sample_wsdl.xml` - Sample WSDL 1.1 specification

### Related Tools
- `intelligent_search.py` - Intelligent API search system
- `api_onboard_agent.py` - API onboarding agent
- `api_integration_manager.py` - API integration management

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd api-discovery

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 api_connector.py
```

### Adding New Formats
1. Create new connector class inheriting from base connector
2. Implement format-specific parsing methods
3. Add format detection logic
4. Update command-line interface
5. Add tests and documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation
- Contact the development team

---

**🔗 CatalystAI API Connector** - Convert any API specification to a common structure for intelligent discovery and integration.
