# 🔗 Data Collector

A comprehensive Python tool for converting various API specification formats (Swagger/OpenAPI, WSDL) into a common structure for vector database storage and intelligent API discovery.

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

## 📁 Project Structure

```
data-collector/
├── src/
│   ├── connectors/          # API specification connectors
│   │   ├── __init__.py
│   │   ├── swagger_connector.py
│   │   ├── wsdl_connector.py
│   │   └── api_connector.py
│   ├── models/             # Data models and schemas
│   │   ├── __init__.py
│   │   ├── common_spec.py
│   │   └── base_models.py
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── chunking_demo.py
│   │   └── helpers.py
│   └── __init__.py
├── data/                   # Data storage directory
├── samples/                # Sample API specifications
│   ├── sample_swagger.json
│   └── sample_wsdl.xml
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt         # Python dependencies
├── setup.py               # Package setup
├── README.md              # This file
└── .env.template          # Environment template
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- ChromaDB
- Required dependencies

### Install from Source
```bash
# Clone the repository
git clone <repository-url>
cd data-collector

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Install Dependencies Only
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your API keys
# OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Convert Swagger/OpenAPI File
```bash
# Convert Swagger JSON file
python src/connectors/api_connector.py convert samples/sample_swagger.json

# Convert OpenAPI YAML file
python src/connectors/api_connector.py convert api_spec.yaml --type swagger

# Auto-detect format
python src/connectors/api_connector.py convert api_spec.json
```

### 3. Convert WSDL File
```bash
# Convert WSDL file
python src/connectors/api_connector.py convert samples/sample_wsdl.xml --type wsdl

# Auto-detect WSDL
python src/connectors/api_connector.py convert service.xml
```

### 4. Convert from URL
```bash
# Convert from Swagger URL
python src/connectors/api_connector.py convert-url https://api.example.com/swagger.json

# Convert from WSDL URL
python src/connectors/api_connector.py convert-url https://service.example.com/service.wsdl
```

### 5. List Stored APIs
```bash
# List all converted APIs
python src/connectors/api_connector.py list
```

## 📚 API Reference

### SwaggerConnector
```python
from src.connectors.swagger_connector import SwaggerConnector

connector = SwaggerConnector()

# Parse Swagger file
spec = connector.parse_swagger_file("api_spec.json")

# Parse from URL
spec = connector.parse_swagger_url("https://api.example.com/swagger.json")
```

### WSDLConnector
```python
from src.connectors.wsdl_connector import WSDLConnector

connector = WSDLConnector()

# Parse WSDL file
spec = connector.parse_wsdl_file("service.wsdl")

# Parse from URL
spec = connector.parse_wsdl_url("https://service.example.com/service.wsdl")
```

### APIConnectorManager
```python
from src.connectors.api_connector import APIConnectorManager

manager = APIConnectorManager()
manager.load_environment()
manager.initialize_chromadb()

# Convert and store
success = manager.convert_and_store("api_spec.json", "swagger")
```

## 🔧 Common API Structure

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
    sealId: str = "105961"          # Seal ID for the API specification (default: 105961)
    application: str = "PROFILE"     # Application name (default: PROFILE)
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

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_swagger_connector.py
```

### Test Sample Files
```bash
# Test with sample Swagger file
python src/connectors/api_connector.py convert samples/sample_swagger.json

# Test with sample WSDL file
python src/connectors/api_connector.py convert samples/sample_wsdl.xml --type wsdl
```

## 📝 Development

### Code Style
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Adding New Connectors
1. Create new connector class in `src/connectors/`
2. Implement format-specific parsing methods
3. Add format detection logic
4. Update the main connector manager
5. Add tests and documentation

## 🔧 Configuration

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
Extend the categorization logic by modifying the `_categorize_api` method:

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
- `samples/sample_swagger.json` - Sample Swagger 2.0 specification
- `samples/sample_wsdl.xml` - Sample WSDL 1.1 specification

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd data-collector

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest

# Run linting
flake8 src/
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

**🔗 Data Collector** - Convert any API specification to a common structure for intelligent discovery and integration.
