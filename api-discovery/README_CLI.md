# 🚀 CatalystAI API Discovery & Integration CLI Tool

A powerful command-line tool for discovering and integrating APIs using ChromaDB vector database and OpenAI's intelligent guidance.

## ✨ Features

- **🔍 Intelligent API Discovery**: Find relevant APIs using natural language queries
- **📚 Comprehensive API Database**: Pre-loaded with 50+ popular tools and their specifications
- **🤖 AI-Powered Guidance**: Get detailed integration advice from OpenAI
- **💾 Vector Storage**: Uses ChromaDB for efficient similarity search
- **🛠️ Command-Line Interface**: Easy-to-use CLI for developers and DevOps teams

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection

### 2. Installation

```bash
# Clone the repository
git clone <your-repo>
cd api-discovery

# Install dependencies
pip install -r requirements_api_discovery.txt

# Set up environment variables
cp env.template .env
# Edit .env and add your OpenAI API key
```

### 3. Basic Usage

```bash
# Initialize the database with API data
python api_discovery_simple.py init-db

# Search for APIs
python api_discovery_simple.py search "How do I integrate payment processing?"

# List all stored APIs
python api_discovery_simple.py list-apis

# Run sample queries
python api_discovery_simple.py test
```

## 📖 Command Reference

### `init-db`
Initialize the ChromaDB database with comprehensive API documentation.

```bash
python api_discovery_simple.py init-db
```

### `search <query>`
Search for APIs based on your natural language query.

```bash
python api_discovery_simple.py search "I need to implement user authentication"
python api_discovery_simple.py search "How do I send SMS notifications?" --top-k 3
```

**Options:**
- `--top-k <number>`: Number of results to return (default: 5)

### `list-apis`
Display all APIs currently stored in the database.

```bash
python api_discovery_simple.py list-apis
```

### `test`
Run the system through a series of sample queries to verify functionality.

```bash
python api_discovery_simple.py test
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize OpenAI settings
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=api_documentation
```

### Getting OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Create a new API key
4. Add it to your `.env` file

## 📊 API Database

The tool comes pre-loaded with comprehensive information about 50+ popular APIs, including:

### Categories
- **Payment Processing**: Stripe, PayPal, Square
- **Authentication & Security**: Auth0, Firebase Auth, Okta
- **Communication & Notifications**: Twilio, SendGrid, Mailchimp
- **Maps & Location**: Google Maps, Mapbox, HERE
- **Data & Analytics**: Google Analytics, Mixpanel, Amplitude
- **Team Collaboration**: Slack, Microsoft Teams, Discord
- **Development & DevOps**: GitHub, GitLab, AWS
- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob
- **Workflow Automation**: Zapier, IFTTT, n8n

### API Information Included
- **Endpoints**: Key API endpoints with descriptions
- **Authentication**: Authentication methods and requirements
- **Rate Limits**: API usage limits and throttling
- **Pricing**: Cost structure and pricing tiers
- **Integration Steps**: Step-by-step setup instructions
- **Best Practices**: Security and performance recommendations
- **Use Cases**: Common application scenarios
- **SDK Languages**: Supported programming languages
- **Documentation URLs**: Links to official documentation

## 🔍 How It Works

### 1. Vector Search
- Your query is processed and compared against stored API documentation
- ChromaDB uses semantic similarity to find the most relevant APIs
- Results are ranked by relevance score

### 2. AI Analysis
- Relevant APIs are sent to OpenAI GPT-4
- The AI analyzes your specific use case and requirements
- Provides tailored integration guidance and recommendations

### 3. Comprehensive Output
- **API Recommendations**: Which APIs to use and why
- **Integration Strategy**: Step-by-step implementation approach
- **Best Practices**: Security and performance considerations
- **Common Pitfalls**: What to avoid during integration
- **Next Steps**: Actionable development tasks
- **Cost Considerations**: Pricing and scaling implications

## 💡 Example Queries

### Payment Integration
```bash
python api_discovery_simple.py search "I need to accept credit card payments in my e-commerce app"
```

### User Authentication
```bash
python api_discovery_simple.py search "How do I implement OAuth 2.0 authentication with social login?"
```

### SMS Notifications
```bash
python api_discovery_simple.py search "I want to send SMS notifications to users when they complete an action"
```

### File Storage
```bash
python api_discovery_simple.py search "What's the best way to implement file upload and storage for user-generated content?"
```

### Team Collaboration
```bash
python api_discovery_simple.py search "How can I integrate team chat and notification systems into my application?"
```

## 🛠️ Development

### Project Structure
```
api-discovery/
├── api_discovery_simple.py      # Main CLI tool
├── api_dataset.py               # Comprehensive API dataset
├── requirements_api_discovery.txt # Python dependencies
├── env.template                 # Environment variables template
├── README_CLI.md               # This file
└── chroma_db/                  # ChromaDB storage directory
```

### Adding New APIs

To add new APIs to the database:

1. Edit `api_dataset.py`
2. Add new API entries to the `api_docs` list
3. Follow the existing data structure
4. Re-run `init-db` to update the database

### Customizing OpenAI Prompts

Modify the system and user prompts in the `discover_api_integration` method to customize the AI's response style and focus areas.

## 🚨 Troubleshooting

### Common Issues

**"OPENAI_API_KEY not found"**
- Ensure your `.env` file exists and contains the API key
- Check that the key is properly formatted without quotes

**"ChromaDB connection error"**
- Verify ChromaDB is installed: `pip install chromadb`
- Check file permissions in the `chroma_db` directory

**"OpenAI API error"**
- Verify your API key is valid and has sufficient credits
- Check OpenAI's service status at [status.openai.com](https://status.openai.com)

**"No APIs found in database"**
- Run `init-db` first to populate the database
- Check that the `api_dataset.py` file is accessible

### Performance Tips

- Use specific queries for better results
- Limit results with `--top-k` for faster responses
- Cache frequently used API information locally

## 🔮 Future Enhancements

- **Real-time API Updates**: Connect to live API documentation sources
- **Code Generation**: Generate actual integration code snippets
- **Performance Metrics**: Track query performance and relevance scores
- **Custom Datasets**: Allow users to add their own API documentation
- **Integration Testing**: Test API connectivity and functionality
- **Cost Optimization**: Suggest cost-effective API alternatives

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Areas for Contribution
- Add new APIs to the dataset
- Improve search algorithms
- Enhance OpenAI prompts
- Add new CLI commands
- Improve error handling
- Add tests and documentation

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the example queries for guidance

---

**🎉 Happy API Discovery! 🚀✨**
