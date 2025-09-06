# 🚀 **CatalystAI API Discovery & Integration CLI Tool**

A powerful command-line tool for discovering and integrating APIs using **ChromaDB** as a vector store with **OpenAI** for intelligent API discovery and integration guidance from a developer perspective.

## 🎯 **What This Tool Does**

- **🔍 Intelligent API Discovery**: Find relevant APIs using natural language queries
- **📚 Comprehensive API Database**: Pre-loaded with 50+ popular tools and their specifications
- **🤖 AI-Powered Guidance**: Get detailed integration advice from OpenAI GPT-4
- **💾 Vector Storage**: Uses ChromaDB for efficient similarity search
- **🛠️ Command-Line Interface**: Easy-to-use CLI for developers and DevOps teams
- **🔒 Secure**: Environment-based configuration with proper security practices

## 🛠️ **Prerequisites**

### **Required Software**
- Python 3.8 or higher
- Internet connection for API calls

### **Required Accounts**
- **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

## 📦 **Installation & Setup**

### **Step 1: Clone the Repository**
```bash
git clone <your-repo-url>
cd api-discovery
```

### **Step 2: Install Dependencies**
```bash
# Install all required packages
pip install -r requirements_api_discovery.txt

# Or install manually
pip install chromadb openai python-dotenv
```

### **Step 3: Environment Configuration**
Create a `.env` file in the project directory:
```bash
# Copy the template
cp env.template .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=api_documentation
```

## 🚀 **Quick Start**

### **Initialize the Database**
```bash
# Initialize ChromaDB with API data
python api_discovery_simple.py init-db
```

### **Search for APIs**
```bash
# Search for payment processing APIs
python api_discovery_simple.py search "How do I integrate payment processing?"

# Search with custom number of results
python api_discovery_simple.py search "I need to implement user authentication" --top-k 3
```

### **List Available APIs**
```bash
# See all APIs in the database
python api_discovery_simple.py list-apis
```

### **Test the System**
```bash
# Run sample queries to verify functionality
python api_discovery_simple.py test
```

## 📖 **Command Reference**

### **`init-db`** - Initialize Database
Initialize the ChromaDB database with comprehensive API documentation.
```bash
python api_discovery_simple.py init-db
```

### **`search <query>`** - Search APIs
Search for APIs based on your natural language query.
```bash
python api_discovery_simple.py search "I need to implement user authentication"
python api_discovery_simple.py search "How do I send SMS notifications?" --top-k 3
```

**Options:**
- `--top-k <number>`: Number of results to return (default: 5)

### **`list-apis`** - List APIs
Display all APIs currently stored in the database.
```bash
python api_discovery_simple.py list-apis
```

### **`test`** - Test System
Run the system through a series of sample queries to verify functionality.
```bash
python api_discovery_simple.py test
```

## 🔍 **Sample API Documentation Included**

### **Payment & E-commerce**
- **Stripe API**: Payment processing, subscriptions, webhooks
- **PayPal API**: Digital payments, international transactions

### **Maps & Location**
- **Google Maps API**: Geocoding, directions, places
- **Mapbox API**: Custom maps, routing, geospatial data

### **Authentication & Security**
- **Auth0 API**: OAuth 2.0, social login, MFA
- **Firebase Auth**: Google authentication, phone auth

### **Communication & Notifications**
- **Twilio API**: SMS, voice, video, WhatsApp
- **SendGrid API**: Email delivery, templates, analytics

### **Team Collaboration**
- **Slack API**: Messaging, webhooks, bot integration
- **Microsoft Teams API**: Chat, meetings, file sharing

### **Development & DevOps**
- **GitHub API**: Repository management, CI/CD integration
- **GitLab API**: Git repositories, project management

### **Cloud Storage**
- **AWS S3 API**: Object storage, file management
- **Google Cloud Storage API**: Cloud storage, data backup

### **Workflow Automation**
- **Zapier API**: App integration, workflow automation
- **IFTTT API**: IoT automation, applet creation

## 🎯 **Example Queries to Try**

### **Payment Integration**
```bash
python api_discovery_simple.py search "I need to accept credit card payments in my e-commerce app"
python api_discovery_simple.py search "How do I implement subscription billing?"
```

### **Authentication & Security**
```bash
python api_discovery_simple.py search "How do I implement OAuth 2.0 authentication with social login?"
python api_discovery_simple.py search "What's the most secure way to handle API keys?"
```

### **Communication & Notifications**
```bash
python api_discovery_simple.py search "How do I send SMS notifications to users?"
python api_discovery_simple.py search "I need to implement email marketing campaigns"
```

### **Location & Maps**
```bash
python api_discovery_simple.py search "I want to add address validation to my form"
python api_discovery_simple.py search "How do I implement route planning in my app?"
```

## 🔧 **Project Structure**

```
api-discovery/
├── api_discovery_simple.py      # 🚀 Main CLI tool
├── api_dataset.py               # 📚 API specifications database
├── requirements_api_discovery.txt # 📦 Python dependencies
├── env.template                 # 🔑 Environment variables template
├── README_CLI.md               # 📖 Comprehensive CLI documentation
├── README.md                   # 📋 This file
├── QUICK_START.md              # ⚡ Quick setup guide
└── chroma_db/                  # 💾 ChromaDB storage (auto-created)
```

## 🔍 **How It Works**

### **1. Vector Search**
- Your query is processed and compared against stored API documentation
- ChromaDB uses semantic similarity to find the most relevant APIs
- Results are ranked by relevance score

### **2. AI Analysis**
- Relevant APIs are sent to OpenAI GPT-4
- The AI analyzes your specific use case and requirements
- Provides tailored integration guidance and recommendations

### **3. Comprehensive Output**
- **API Recommendations**: Which APIs to use and why
- **Integration Strategy**: Step-by-step implementation approach
- **Best Practices**: Security and performance considerations
- **Common Pitfalls**: What to avoid during integration
- **Next Steps**: Actionable development tasks
- **Cost Considerations**: Pricing and scaling implications

## 🚨 **Troubleshooting**

### **Common Issues**

#### **OpenAI API Key Error**
```bash
# Check your .env file exists
ls -la .env

# Verify the key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('OPENAI_API_KEY')[:20] + '...' if os.getenv('OPENAI_API_KEY') else 'Not found')"
```

#### **ChromaDB Connection Issues**
```bash
# Remove existing database and reinitialize
rm -rf chroma_db/
python api_discovery_simple.py init-db
```

#### **Package Installation Issues**
```bash
# Upgrade pip
pip install --upgrade pip

# Install with specific versions
pip install chromadb==0.4.22 openai==1.12.0 python-dotenv==1.0.0
```

### **Performance Tips**
- Use specific queries for better results
- Limit results with `--top-k` for faster responses
- Cache frequently used API information locally

## 🔮 **Future Enhancements**

### **Planned Features**
- **Real-time API Updates**: Live API documentation synchronization
- **Code Generation**: Automatic code snippets and examples
- **Integration Testing**: Test API integrations automatically
- **Cost Analysis**: Include pricing and cost optimization
- **Performance Metrics**: Track API performance and reliability

### **Advanced Capabilities**
- **Multi-modal Search**: Search by code examples, diagrams, or videos
- **Integration Templates**: Pre-built integration patterns
- **API Comparison**: Side-by-side API feature comparison
- **Migration Tools**: Help migrate between different APIs
- **Compliance Check**: Verify API compliance with regulations

## 📚 **Additional Resources**

### **Documentation**
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [CLI Documentation](README_CLI.md)

### **Community**
- [ChromaDB GitHub](https://github.com/chroma-core/chroma)
- [OpenAI Community](https://community.openai.com/)

### **Tutorials**
- [Vector Database Basics](https://docs.trychroma.com/getting-started)
- [OpenAI API Tutorials](https://platform.openai.com/docs/quickstart)

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

### **Areas for Contribution**
- Add new APIs to the dataset
- Improve search algorithms
- Enhance OpenAI prompts
- Add new CLI commands
- Improve error handling
- Add tests and documentation

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎉 **Getting Started**

1. **Clone the repository**
2. **Install dependencies** using `pip install -r requirements_api_discovery.txt`
3. **Set up your OpenAI API key** in the `.env` file
4. **Initialize the database** with `python api_discovery_simple.py init-db`
5. **Start discovering APIs** with `python api_discovery_simple.py search "your query"`

**Happy API Discovery! 🚀✨**

