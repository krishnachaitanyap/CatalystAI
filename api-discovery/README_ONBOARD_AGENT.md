# 🚀 **CatalystAI API Onboard Agent**

A powerful agent that automatically discovers and onboards new APIs by searching the web, extracting specifications, and integrating them into the ChromaDB database for use with the API discovery system.

## ✨ **Features**

- **🔍 Web Search**: Automatically searches for API documentation across the web
- **🤖 AI-Powered Extraction**: Uses OpenAI to intelligently extract API specifications
- **📋 Structured Output**: Converts web content into our standardized API format
- **🔗 ChromaDB Integration**: Seamlessly integrates with the existing API discovery system
- **📊 Consolidation**: Merges multiple sources into comprehensive API specifications
- **💾 File Export**: Saves API specifications as JSON files for review and sharing

## 🛠️ **Prerequisites**

- Python 3.8+
- OpenAI API key
- Internet connection for web search
- Existing API discovery system (optional)

## 📦 **Installation**

The API Onboard Agent uses the same dependencies as the main API discovery system:

```bash
pip install -r requirements_api_discovery.txt
```

## 🚀 **Quick Start**

### **1. Onboard a New API**
```bash
# Onboard Stripe API
python api_onboard_agent.py onboard "Stripe API"

# Onboard with file output
python api_onboard_agent.py onboard "Google Maps API" --output-file maps_api.json
```

### **2. Search Existing APIs**
```bash
# Search for payment processing APIs
python api_onboard_agent.py search "payment processing" --limit 5
```

## 📖 **Command Reference**

### **`onboard <product_name>`** - Onboard New API
Searches the web for API documentation and extracts comprehensive specifications.

```bash
python api_onboard_agent.py onboard "Stripe API"
python api_onboard_agent.py onboard "Auth0 API" --output-file auth0_spec.json
```

**Options:**
- `--output-file <filename>`: Save API specification to JSON file

### **`search <query>`** - Search Existing APIs
Search through existing APIs in the dataset.

```bash
python api_onboard_agent.py search "authentication"
python api_onboard_agent.py search "payment processing" --limit 3
```

**Options:**
- `--limit <number>`: Number of results to return (default: 5)

## 🔧 **Integration with API Discovery System**

### **Step 1: Onboard New API**
```bash
python api_onboard_agent.py onboard "New API Name" --output-file new_api.json
```

### **Step 2: Add to ChromaDB**
```bash
python api_integration_manager.py add new_api.json
```

### **Step 3: Use in Discovery**
```bash
python api_discovery_simple.py search "your query"
```

## 🔍 **How It Works**

### **1. Web Search**
- Searches Google for official API documentation
- Filters results for API-related content
- Identifies most relevant documentation sources

### **2. Content Extraction**
- Downloads and parses web pages
- Extracts text content from HTML
- Handles various documentation formats

### **3. AI-Powered Analysis**
- Uses OpenAI GPT-4 to analyze content
- Extracts structured API specifications
- Identifies endpoints, authentication, pricing, etc.

### **4. Data Consolidation**
- Merges information from multiple sources
- Resolves conflicts and inconsistencies
- Creates comprehensive API specification

### **5. Format Standardization**
- Converts to our application-specific format
- Ensures compatibility with ChromaDB
- Maintains consistency with existing APIs

## 📋 **API Specification Format**

The agent extracts and standardizes API information into this format:

```json
{
  "api_name": "API Name",
  "category": "Category (e.g., Payment Processing)",
  "description": "Comprehensive description",
  "endpoints": [
    "POST /v1/payments - Create payment",
    "GET /v1/payments/{id} - Retrieve payment"
  ],
  "authentication": "OAuth 2.0 with Bearer token",
  "rate_limits": "1000 requests per minute",
  "pricing": "2.9% + 30¢ per transaction",
  "integration_steps": [
    "1. Create account and get API keys",
    "2. Install SDK for your language",
    "3. Initialize client with credentials"
  ],
  "best_practices": [
    "Always use HTTPS in production",
    "Implement proper error handling",
    "Store credentials securely"
  ],
  "common_use_cases": [
    "E-commerce payments",
    "Subscription billing",
    "Marketplace transactions"
  ],
  "sdk_languages": ["Python", "JavaScript", "Java"],
  "documentation_url": "https://api.example.com/docs"
}
```

## 🎯 **Example Use Cases**

### **Onboarding Payment APIs**
```bash
# Onboard multiple payment providers
python api_onboard_agent.py onboard "Stripe API" --output-file stripe.json
python api_onboard_agent.py onboard "PayPal API" --output-file paypal.json
python api_onboard_agent.py onboard "Square API" --output-file square.json

# Add to ChromaDB
python api_integration_manager.py add stripe.json
python api_integration_manager.py add paypal.json
python api_integration_manager.py add square.json
```

### **Onboarding Authentication APIs**
```bash
# Onboard authentication providers
python api_onboard_agent.py onboard "Auth0 API" --output-file auth0.json
python api_onboard_agent.py onboard "Firebase Auth API" --output-file firebase_auth.json

# Add to ChromaDB
python api_integration_manager.py add auth0.json
python api_integration_manager.py add firebase_auth.json
```

### **Batch Processing**
```bash
# Create a folder for API specifications
mkdir api_specs

# Onboard multiple APIs
python api_onboard_agent.py onboard "Slack API" --output-file api_specs/slack.json
python api_onboard_agent.py onboard "Twilio API" --output-file api_specs/twilio.json
python api_onboard_agent.py onboard "SendGrid API" --output-file api_specs/sendgrid.json

# Add all to ChromaDB at once
python api_integration_manager.py add-multiple api_specs/
```

## 🔗 **Integration Manager Commands**

### **Add Single API**
```bash
python api_integration_manager.py add api_spec.json
```

### **Add Multiple APIs**
```bash
python api_integration_manager.py add-multiple api_specs_folder/
```

### **List All APIs**
```bash
python api_integration_manager.py list
```

### **Database Statistics**
```bash
python api_integration_manager.py stats
```

### **Remove API**
```bash
python api_integration_manager.py remove "API Name"
```

## 🚨 **Troubleshooting**

### **Web Search Issues**
- **Rate Limiting**: The agent includes delays between requests
- **Blocked Requests**: Uses realistic user agent headers
- **No Results**: Try different search terms or product names

### **AI Extraction Issues**
- **Token Limits**: Content is automatically truncated if too long
- **JSON Parsing**: AI responses are validated and cleaned
- **Missing Information**: Uses "N/A" for unavailable data

### **ChromaDB Integration Issues**
- **Duplicate APIs**: Each API gets a unique timestamp-based ID
- **Metadata Format**: All complex data is converted to strings
- **Collection Issues**: Automatically creates collection if missing

## 🔮 **Future Enhancements**

### **Planned Features**
- **Multiple Search Engines**: Support for Bing, DuckDuckGo, etc.
- **API Documentation Parsers**: Direct parsing of OpenAPI/Swagger specs
- **Real-time Updates**: Monitor API documentation for changes
- **Quality Scoring**: Rate the quality of extracted specifications
- **Batch Processing**: Onboard multiple APIs in parallel

### **Advanced Capabilities**
- **Code Example Extraction**: Extract code snippets from documentation
- **Version Management**: Track API versions and changes
- **Compliance Checking**: Verify API compliance with standards
- **Performance Analysis**: Analyze API performance characteristics
- **Integration Testing**: Test API connectivity automatically

## 📚 **Additional Resources**

### **Related Tools**
- [API Discovery CLI](README_CLI.md) - Main API discovery tool
- [API Integration Manager](api_integration_manager.py) - ChromaDB management
- [API Dataset](api_dataset.py) - Existing API specifications

### **Documentation**
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/)

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

### **Areas for Contribution**
- Improve web search algorithms
- Enhance AI extraction prompts
- Add support for more documentation formats
- Improve error handling and resilience
- Add tests and documentation

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎉 **Getting Started**

1. **Set up environment** with OpenAI API key
2. **Onboard your first API**: `python api_onboard_agent.py onboard "API Name"`
3. **Add to ChromaDB**: `python api_integration_manager.py add api_spec.json`
4. **Discover APIs**: `python api_discovery_simple.py search "your query"`

**Happy API Onboarding! 🚀✨**
