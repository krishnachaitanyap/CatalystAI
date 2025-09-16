# ProdAssist

AI-powered API specification management and chat assistant with React UI and Python API backend.

## 🚀 Features

### Frontend (React + TypeScript)
- **Chat Interface**: Interactive chat with markdown support and custom widgets
- **API Specification Management**: Upload and manage REST/SOAP API specifications per SealId and Application
- **Custom Widgets**: Support for charts, buttons, tables, and code blocks
- **Real-time Updates**: Live chat with chain of thought reasoning
- **Responsive Design**: Material-UI components with modern UX

### Backend (FastAPI + Python)
- **SQLite Integration**: User management and API specification storage
- **Chat Management**: Session-based chat with chain of thought tracking
- **LLM Integration**: OpenAI GPT models for intelligent responses
- **CommonAPI Spec Generation**: Convert SOAP and REST APIs to standardized format
- **Vector Database**: ChromaDB with configurable chunking strategies
- **Authentication**: JWT-based security with user management

## 🏗️ Architecture

```
ProdAssist/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Main application pages
│   │   ├── hooks/           # Zustand state management
│   │   ├── services/        # API service layer
│   │   └── types/           # TypeScript type definitions
│   └── package.json
├── backend/                  # FastAPI Python backend
│   ├── app/                 # FastAPI application
│   ├── models/              # Database models and schemas
│   ├── services/            # Business logic services
│   ├── utils/               # Utilities and helpers
│   └── requirements.txt
├── docs/                    # Documentation
├── scripts/                 # Setup and utility scripts
└── setup.sh                # Main setup script
```

## 🛠️ Quick Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd ProdAssist
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure Environment**:
   ```bash
   # Edit backend configuration
   nano backend/.env
   
   # Add your OpenAI API key
   OPENAI_API_KEY=your-openai-api-key-here
   ```

3. **Start Application**:
   ```bash
   ./start_all.sh
   ```

4. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Configuration

### Backend Settings (`backend/.env`)
```env
# Application
APP_NAME=ProdAssist
DEBUG=false

# Database
DATABASE_URL=sqlite:///./prodassist.db

# Vector Database
VECTOR_DB_PATH=./vector_db
CHUNKING_STRATEGY=ENDPOINT_BASED
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Settings (`frontend/.env`)
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📚 Usage

### Default Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Key Features

1. **API Specification Management**:
   - Upload WSDL, OpenAPI, Swagger files
   - Organize by SealId and Application
   - Convert to CommonAPI format
   - Store in both SQLite and Vector DB

2. **Chat Interface**:
   - Ask questions about your APIs
   - Get code examples and explanations
   - Chain of thought reasoning
   - Markdown responses with widgets

3. **Vector Search**:
   - Semantic search across API specifications
   - Configurable chunking strategies
   - Context-aware responses

## 🔌 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### API Specifications
- `GET /api-specs` - List specifications
- `POST /api-specs` - Create specification
- `PUT /api-specs/{id}` - Update specification
- `DELETE /api-specs/{id}` - Delete specification
- `POST /upload` - Upload specification file

### Chat
- `GET /chat/sessions` - List chat sessions
- `POST /chat/sessions` - Create chat session
- `POST /chat/sessions/{id}/messages` - Send message
- `GET /chat/sessions/{id}/history` - Get chat history

### Search
- `POST /search` - Search API specifications

## 🧩 Chunking Strategies

1. **FIXED_SIZE**: Split content into fixed-size chunks
2. **SEMANTIC**: Chunk by semantic sections (endpoints, types)
3. **HYBRID**: Combine semantic and fixed-size approaches
4. **ENDPOINT_BASED**: Chunk by API endpoints (recommended)

## 🎨 Custom Widgets

The chat interface supports custom widgets for rich content:

- **Charts**: Bar charts, line charts, pie charts
- **Tables**: Data tables with sorting and filtering
- **Code Blocks**: Syntax-highlighted code examples
- **Buttons**: Interactive action buttons
- **JSON**: Formatted JSON data

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## 📊 Monitoring & Logging

- Structured logging with configurable levels
- Request/response logging
- Error tracking and reporting
- Performance metrics
- Token usage tracking

## 🚀 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the API documentation at `/docs` endpoint

---

**ProdAssist** - Making API management intelligent and interactive! 🚀
