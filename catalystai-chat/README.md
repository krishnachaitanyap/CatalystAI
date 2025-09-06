# CatalystAI Chat Interface

A comprehensive React application for API discovery, integration guidance, and API specification management.

## 🚀 Features

### 💬 Chat Interface
- **Intelligent API Discovery**: Ask questions about API discovery, integration best practices, and performance optimization
- **Real-time Responses**: Get comprehensive, actionable insights powered by AI
- **Clean UI**: Modern, responsive design with smooth interactions
- **Chat Management**: Clear chat history and scroll to bottom functionality

### 📋 API Spec Management
- **Application Management**: Create and manage applications with SEALID support (default: 105961)
- **Multi-format Upload**: Support for REST (Swagger/OpenAPI), SOAP (WSDL/XSD), and Postman Collections
- **File Validation**: Real-time validation at UI level with detailed error reporting
- **CommonAPISpec Editor**: Comprehensive editor for all CommonAPISpec attributes
- **Multiple File Upload**: Upload and manage multiple API specifications simultaneously

## 🏗️ Technology Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Heroicons** for icons
- **Context API** for state management
- **Modern ES6+** features

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd catalystai-chat
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📱 Application Structure

```
src/
├── components/
│   ├── ChatInterface.tsx      # Main chat interface
│   ├── ChatMessage.tsx        # Individual message component
│   ├── ChatInput.tsx          # Message input component
│   ├── ApiSpecManagement.tsx  # Main API spec management
│   ├── ApplicationManager.tsx # Application management
│   ├── ApiUploader.tsx        # File upload interface
│   └── ApiSpecEditor.tsx      # CommonAPISpec editor
├── contexts/
│   └── ChatContext.tsx        # Chat state management
├── types/
│   └── chat.ts                # TypeScript interfaces
└── data/
    └── sampleData.ts          # Sample data
```

## 💡 Usage

### Chat Interface
1. **Ask Questions**: Type your questions about API discovery, integration, or best practices
2. **Get Insights**: Receive comprehensive, AI-powered responses
3. **Clear Chat**: Use the "Clear Chat" button to start fresh

### API Spec Management

#### 1. Application Management
- **View Applications**: See all applications under SEALID 105961
- **Create Application**: Add new applications with name, description, and SEALID
- **Manage APIs**: Click "Manage APIs" to upload specifications

#### 2. File Upload
- **Supported Formats**:
  - **REST APIs**: `.json`, `.yaml`, `.yml` (Swagger/OpenAPI)
  - **SOAP APIs**: `.wsdl`, `.xsd`
  - **Postman Collections**: `.json`
- **Validation**: Real-time validation with detailed error messages
- **Multiple Files**: Upload multiple files simultaneously
- **Drag & Drop**: Drag files directly onto the upload area

#### 3. API Specification Editor
- **Basic Info**: Edit API name, version, description, base URL, category
- **Endpoints**: View and manage API endpoints
- **Authentication**: Configure authentication methods and settings
- **Advanced**: Set SDK languages, tags, contact information

## 🔍 File Validation

The application performs comprehensive validation:

### JSON Files
- **Structure Validation**: Checks for required fields (swagger/openapi, info, paths)
- **Format Validation**: Ensures valid JSON syntax
- **Content Validation**: Validates Swagger/OpenAPI and Postman collection structure

### XML Files
- **XML Declaration**: Checks for proper XML declaration
- **WSDL Validation**: Validates WSDL definitions element
- **XSD Validation**: Validates XSD schema element

### YAML Files
- **Basic Validation**: Checks file format (basic implementation)

## 📋 CommonAPISpec Attributes

The editor supports all CommonAPISpec attributes:

- **Basic Information**: API name, version, description, base URL, category
- **Endpoints**: Path, method, parameters, request/response bodies
- **Authentication**: Type, schemes, scopes, URLs
- **Rate Limits**: Per second/minute/hour/day limits
- **SDK Languages**: Python, JavaScript, Java, C#, Go, Ruby, PHP, Swift, Kotlin
- **Integration Steps**: Step-by-step integration guidance
- **Best Practices**: Recommended practices and patterns
- **Contact Information**: Support contact details
- **License Information**: License name and URL

## 🛠️ Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Style

- **TypeScript**: Strict type checking enabled
- **ESLint**: Code linting with React rules
- **Prettier**: Code formatting (if configured)
- **Tailwind CSS**: Utility-first CSS framework

## 🎨 Customization

### Styling
- **Tailwind Config**: Modify colors, fonts, and spacing in `tailwind.config.js`
- **CSS Variables**: Custom properties for theming
- **Component Classes**: Utility classes for consistent styling

### Sample Data
- **Questions**: Add new sample questions in `src/data/sampleData.ts`
- **Responses**: Customize mock responses in `ChatContext.tsx`
- **Metadata**: Extend response metadata structure

### API Integration
- **Real API**: Replace mock responses with actual CatalystAI API calls
- **Authentication**: Add user authentication and session management
- **WebSocket**: Implement real-time chat updates

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 640px - Single column layout
- **Tablet**: 640px - 1024px - Optimized spacing
- **Desktop**: > 1024px - Full feature layout

### Mobile Features
- Touch-friendly buttons and inputs
- Swipe gestures for navigation
- Optimized keyboard handling
- Responsive typography scaling

## 🚀 Deployment

### Build Process
```bash
# Create optimized build
npm run build

# Serve static files
npx serve -s build
```

### Deployment Options
- **Netlify**: Drag and drop deployment
- **Vercel**: Git-based deployment
- **AWS S3**: Static website hosting
- **Docker**: Containerized deployment

## 🔮 Future Enhancements

### Planned Features
- **Real-time Updates**: WebSocket integration
- **File Uploads**: Document and image sharing
- **Voice Input**: Speech-to-text capabilities
- **Multi-language**: Internationalization support
- **Advanced Analytics**: Usage tracking and insights

### Integration Possibilities
- **Jira**: Automatic ticket creation
- **Slack**: Team notifications
- **GitHub**: Repository integration
- **CI/CD**: Automated deployment pipelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- **Email**: support@catalystai.com
- **Documentation**: [API Documentation](https://docs.catalystai.com)
- **Issues**: [GitHub Issues](https://github.com/catalystai/issues)

---

**Built with ❤️ for the CatalystAI platform**