#!/bin/bash

# ProdAssist Setup Script
# This script sets up the complete ProdAssist application

set -e

echo "🚀 Setting up ProdAssist..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is not installed. Please install Node.js 16 or higher."
        exit 1
    fi
    
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating environment configuration..."
        cp env.example .env
        print_warning "Please update .env file with your configuration"
    fi
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p vector_db
    
    print_success "Backend setup completed"
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating frontend environment configuration..."
        echo "REACT_APP_API_URL=http://localhost:8000" > .env
    fi
    
    print_success "Frontend setup completed"
    cd ..
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Backend startup script
    cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ProdAssist Backend..."
cd backend
source venv/bin/activate
python main.py
EOF
    
    # Frontend startup script
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ProdAssist Frontend..."
cd frontend
npm start
EOF
    
    # Full startup script
    cat > start_all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting ProdAssist..."

# Start backend in background
echo "Starting backend..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ ProdAssist is starting..."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    
    # Make scripts executable
    chmod +x start_backend.sh
    chmod +x start_frontend.sh
    chmod +x start_all.sh
    
    print_success "Startup scripts created"
}

# Create documentation
create_documentation() {
    print_status "Creating documentation..."
    
    cat > README.md << 'EOF'
# ProdAssist

AI-powered API specification management and chat assistant.

## Features

- **Chat Interface**: Interactive chat with markdown support and custom widgets
- **API Specification Management**: Support for REST and SOAP APIs
- **Vector Database**: Configurable chunking strategies for efficient search
- **LLM Integration**: OpenAI GPT models for intelligent responses
- **User Management**: Secure authentication and user management
- **Real-time Chat**: Chain of thought reasoning and token tracking

## Quick Start

1. **Setup**: Run the setup script
   ```bash
   ./setup.sh
   ```

2. **Start All Services**:
   ```bash
   ./start_all.sh
   ```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Default Credentials

- Username: `admin`
- Password: `admin123`

## Configuration

### Backend Configuration

Edit `backend/.env`:
```env
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./prodassist.db
VECTOR_DB_PATH=./vector_db
CHUNKING_STRATEGY=ENDPOINT_BASED
```

### Frontend Configuration

Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000
```

## Architecture

- **Backend**: FastAPI with SQLite database and ChromaDB vector storage
- **Frontend**: React with TypeScript, Material-UI, and Zustand state management
- **LLM**: OpenAI GPT models for chat responses
- **Vector DB**: ChromaDB for semantic search and retrieval

## Development

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

## API Endpoints

- `POST /auth/login` - User authentication
- `GET /api-specs` - List API specifications
- `POST /api-specs` - Create API specification
- `POST /chat/sessions` - Create chat session
- `POST /chat/sessions/{id}/messages` - Send message
- `POST /search` - Search API specifications

## License

MIT License
EOF
    
    print_success "Documentation created"
}

# Main setup function
main() {
    echo "🎯 ProdAssist Setup Script"
    echo "=========================="
    
    check_python
    check_node
    setup_backend
    setup_frontend
    create_startup_scripts
    create_documentation
    
    echo ""
    print_success "🎉 ProdAssist setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update backend/.env with your OpenAI API key"
    echo "2. Run './start_all.sh' to start all services"
    echo "3. Open http://localhost:3000 in your browser"
    echo ""
    echo "Default admin credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
}

# Run main function
main "$@"
