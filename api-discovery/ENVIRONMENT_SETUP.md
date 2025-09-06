# 🔧 **Environment Configuration Guide**

This guide helps you set up the environment configuration for the CatalystAI API Discovery System.

## 🚀 **Quick Setup**

### **Option 1: Interactive Setup (Recommended)**
```bash
python setup_env.py
```
This will guide you through setting up all required and optional configuration.

### **Option 2: Manual Setup**
```bash
# Copy the template
cp env.template .env

# Edit the file with your API keys
nano .env  # or use your preferred editor
```

### **Option 3: Check Current Configuration**
```bash
python setup_env.py --check
```

## 🔑 **Required API Keys**

### **OpenAI API Key (Required)**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

## 🔗 **Optional API Keys (For Enhanced Features)**

### **Google Search API**
- **Purpose**: Better web search for API onboarding
- **Get from**: [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- **Cost**: Free tier available

### **GitHub API Token**
- **Purpose**: Access to GitHub repositories and API documentation
- **Get from**: [GitHub Settings > Tokens](https://github.com/settings/tokens)
- **Cost**: Free

### **Bing Search API**
- **Purpose**: Alternative search engine for web scraping
- **Get from**: [Microsoft Bing Web Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api)
- **Cost**: Free tier available

### **RapidAPI Key**
- **Purpose**: Access to additional API data sources
- **Get from**: [RapidAPI](https://rapidapi.com/)
- **Cost**: Varies by API

## ⚙️ **Configuration Sections**

### **🤖 OpenAI Configuration**
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4                    # gpt-4 or gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3                # 0.0 (focused) to 1.0 (creative)
OPENAI_MAX_TOKENS=2000                # Maximum response length
```

### **💾 ChromaDB Configuration**
```bash
CHROMA_PERSIST_DIRECTORY=./chroma_db  # Database storage location
CHROMA_COLLECTION_NAME=api_documentation
CHROMA_DISTANCE_FUNCTION=cosine       # cosine, euclidean, manhattan
```

### **🔍 Search Configuration**
```bash
TOP_K_RESULTS=5                       # Number of search results
EMBEDDING_MODEL=all-MiniLM-L6-v2      # Embedding model
SEARCH_TIMEOUT=10                     # Search timeout
```

### **🌐 Web Search Configuration**
```bash
WEB_SEARCH_TIMEOUT=15                 # Web request timeout
WEB_SEARCH_DELAY=2                    # Delay between requests
WEB_SEARCH_MAX_RETRIES=3              # Retry attempts
```

### **🔒 Security Settings**
```bash
ENCRYPT_API_KEYS=false               # Encrypt stored keys
ENABLE_RATE_LIMITING=true            # Rate limiting
MAX_REQUESTS_PER_MINUTE=60           # Rate limit
```

### **📊 Logging and Monitoring**
```bash
LOG_LEVEL=INFO                       # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/api_discovery.log    # Log file location
ENABLE_METRICS=true                  # Performance metrics
```

## 📁 **Directory Structure**

The system will create these directories automatically:
```
api-discovery/
├── .env                              # Your configuration file
├── chroma_db/                        # ChromaDB database
├── api_specs/                        # API specification files
├── exports/                          # Exported data
├── backups/                          # Database backups
├── logs/                             # Log files
└── temp/                             # Temporary files
```

## 🔧 **Environment Variables Reference**

### **Required Variables**
- `OPENAI_API_KEY`: Your OpenAI API key

### **Core Configuration**
- `OPENAI_MODEL`: AI model to use
- `OPENAI_TEMPERATURE`: Response creativity
- `OPENAI_MAX_TOKENS`: Response length limit
- `CHROMA_PERSIST_DIRECTORY`: Database location
- `CHROMA_COLLECTION_NAME`: Database collection name
- `TOP_K_RESULTS`: Number of search results

### **Optional Enhancements**
- `GOOGLE_SEARCH_API_KEY`: Better web search
- `GITHUB_API_TOKEN`: GitHub integration
- `BING_SEARCH_API_KEY`: Alternative search
- `RAPIDAPI_KEY`: Additional API sources

### **Performance & Security**
- `ENABLE_CACHING`: Response caching
- `ENABLE_RATE_LIMITING`: Rate limiting
- `MAX_REQUESTS_PER_MINUTE`: Rate limit
- `LOG_LEVEL`: Logging detail level

### **Advanced Features**
- `ENABLE_WEBHOOKS`: Webhook notifications
- `ENABLE_EMAIL_NOTIFICATIONS`: Email alerts
- `ENABLE_SLACK_INTEGRATION`: Slack notifications
- `ENABLE_DISCORD_INTEGRATION`: Discord notifications

### **Custom Service Configuration**
- `CUSTOM_SERVICE_ENABLED`: Enable custom service integration
- `CUSTOM_SERVICE_API_KEY`: API key for custom service
- `CUSTOM_SERVICE_ENDPOINT`: Custom service API endpoint
- `CUSTOM_SERVICE_TIMEOUT`: Timeout for custom service requests
- `CUSTOM_SERVICE_RETRY_ATTEMPTS`: Number of retry attempts

## 🚨 **Security Best Practices**

### **1. Keep .env Secure**
- Never commit `.env` to version control
- Use different keys for development and production
- Regularly rotate your API keys

### **2. Monitor Usage**
- Check your OpenAI usage dashboard
- Set up billing alerts
- Monitor rate limits

### **3. Environment Separation**
- Use different API keys per environment
- Separate development and production databases
- Use different log levels per environment

## 🔍 **Troubleshooting**

### **Common Issues**

#### **"OPENAI_API_KEY not found"**
```bash
# Check if .env exists
ls -la .env

# Verify the key is set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key:', os.getenv('OPENAI_API_KEY')[:20] + '...' if os.getenv('OPENAI_API_KEY') else 'Not found')"
```

#### **"ChromaDB connection error"**
```bash
# Check database directory
ls -la chroma_db/

# Reset database if needed
rm -rf chroma_db/
python api_discovery_simple.py init-db
```

#### **"Web search failed"**
```bash
# Check internet connection
ping google.com

# Verify web search settings in .env
grep WEB_SEARCH .env
```

### **Configuration Validation**
```bash
# Check your configuration
python setup_env.py --check

# Test OpenAI connection
python -c "import openai; from dotenv import load_dotenv; load_dotenv(); openai.api_key = os.getenv('OPENAI_API_KEY'); print('OpenAI connection:', 'OK' if openai.api_key else 'Failed')"
```

## 📝 **Example .env File**

Here's a minimal working configuration:

```bash
# Required
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Core settings
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000

# Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=api_documentation

# Search
TOP_K_RESULTS=5
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Environment
ENVIRONMENT=development
DEBUG_MODE=true
LOG_LEVEL=INFO
```

## 🎯 **Next Steps**

After setting up your environment:

1. **Test the configuration**:
   ```bash
   python setup_env.py --check
   ```

2. **Initialize the database**:
   ```bash
   python api_discovery_simple.py init-db
   ```

3. **Try a search**:
   ```bash
   python api_discovery_simple.py search "payment processing"
   ```

4. **Onboard a new API**:
   ```bash
   python api_onboard_agent.py onboard "Stripe API"
   ```

---

**🔧 Happy configuring! 🚀✨**
