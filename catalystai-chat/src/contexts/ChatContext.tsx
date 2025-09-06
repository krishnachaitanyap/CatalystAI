import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { ChatState, ChatContextType, ChatMessage } from '../types/chat';
import { sampleMessages } from '../data/sampleData';

// Initial state
const initialState: ChatState = {
  messages: sampleMessages,
  isLoading: false,
  error: null,
};

// Action types
type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_CHAT' }
  | { type: 'LOAD_SAMPLE_DATA' };

// Reducer function
function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        error: null,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'CLEAR_CHAT':
      return {
        ...state,
        messages: [],
        error: null,
      };
    case 'LOAD_SAMPLE_DATA':
      return {
        ...state,
        messages: sampleMessages,
        error: null,
      };
    default:
      return state;
  }
}

// Create context
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Provider component
export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
    };

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // For demo purposes, we'll generate a mock response
      // In a real app, this would call the CatalystAI API
      const mockResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: generateMockResponse(message),
        timestamp: new Date(),
        metadata: generateMockMetadata(message),
      };

      dispatch({ type: 'ADD_MESSAGE', payload: mockResponse });
    } catch (error) {
      dispatch({ 
        type: 'SET_ERROR', 
        payload: error instanceof Error ? error.message : 'Failed to send message' 
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const clearChat = () => {
    dispatch({ type: 'CLEAR_CHAT' });
  };

  const value: ChatContextType = {
    state,
    sendMessage,
    clearChat,
    isLoading: state.isLoading,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

// Custom hook to use the chat context
export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

// Mock response generation for demo purposes
function generateMockResponse(message: string): string {
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes('payment') || lowerMessage.includes('e-commerce')) {
    return `💳 **Payment API Integration Options**

I've identified several payment APIs that would work well for your e-commerce application:

## 🔍 **Recommended Payment APIs**

### 1. **Stripe API** (95% relevance)
- **Service**: Payment Processing
- **Features**: Credit cards, digital wallets, subscriptions
- **Integration**: REST API with webhooks
- **Documentation**: Comprehensive with SDKs

### 2. **PayPal API** (92% relevance)
- **Service**: Digital Payments
- **Features**: PayPal, Venmo, credit cards
- **Integration**: REST API with OAuth
- **Global**: Available in 200+ countries

### 3. **Square API** (88% relevance)
- **Service**: Payment & POS
- **Features**: In-person and online payments
- **Integration**: REST API with webhooks
- **Hardware**: POS devices available

## 🚀 **Onboarding Requirements**
- **Stripe**: Self-service, immediate access
- **PayPal**: Business verification required (1-3 days)
- **Square**: Business verification (2-5 days)

## 📚 **Integration Best Practices**
• Implement webhook handling for payment status updates
• Use idempotency keys to prevent duplicate charges
• Implement proper error handling and retry logic
• Follow PCI DSS compliance guidelines

Ready to proceed with payment integration!`;
  }
  
  if (lowerMessage.includes('authentication') || lowerMessage.includes('oauth')) {
    return `🔐 **OAuth 2.0 Authentication Implementation**

Here's a comprehensive guide to implementing OAuth 2.0 authentication:

## 🔑 **OAuth 2.0 Flow Types**

### 1. **Authorization Code Flow** (Recommended for web apps)
- **Security**: Most secure, refresh token support
- **Implementation**: Server-side code exchange
- **Use Case**: Web applications with backend

### 2. **Implicit Flow** (For SPA)
- **Security**: Less secure, no refresh token
- **Implementation**: Client-side token handling
- **Use Case**: Single Page Applications

### 3. **Client Credentials Flow** (For machine-to-machine)
- **Security**: High security, no user context
- **Implementation**: Direct token request
- **Use Case**: API-to-API communication

## 🚀 **Implementation Steps**
1. Register your application with the OAuth provider
2. Implement the chosen OAuth flow
3. Handle token storage securely
4. Implement token refresh logic
5. Add proper error handling

## 📚 **Security Best Practices**
• Store tokens securely (httpOnly cookies, secure storage)
• Implement token refresh before expiration
• Validate tokens on the server side
• Use HTTPS for all OAuth communications
• Implement proper logout and token revocation

Need help with a specific OAuth provider or flow?`;
  }
  
  if (lowerMessage.includes('analytics') || lowerMessage.includes('dashboard')) {
    return `📊 **Data Analytics Dashboard APIs**

I've identified the best APIs for building your analytics dashboard:

## 🔍 **Recommended Analytics APIs**

### 1. **Google Analytics API** (95% relevance)
- **Service**: Web Analytics
- **Features**: Page views, user behavior, conversions
- **Integration**: REST API with OAuth 2.0
- **Real-time**: Live data streaming available

### 2. **Mixpanel API** (92% relevance)
- **Service**: Event Analytics
- **Features**: Custom events, funnel analysis, A/B testing
- **Integration**: REST API with simple authentication
- **Flexibility**: Highly customizable tracking

### 3. **Amplitude API** (88% relevance)
- **Service**: Product Analytics
- **Features**: User journeys, retention analysis, cohorts
- **Integration**: REST API with batch processing
- **Insights**: AI-powered insights and recommendations

## 🚀 **Onboarding Requirements**
- **Google Analytics**: Google account, property setup
- **Mixpanel**: Account creation, project setup
- **Amplitude**: Account creation, data source configuration

## 📚 **Integration Best Practices**
• Implement proper data validation and sanitization
• Use batch processing for high-volume data
• Implement rate limiting and error handling
• Set up webhooks for real-time updates
• Follow data privacy regulations (GDPR, CCPA)

Ready to build your analytics dashboard!`;
  }
  
  if (lowerMessage.includes('scaling') || lowerMessage.includes('performance') || lowerMessage.includes('concurrent')) {
    return `⚡ **Service Scaling & Performance Optimization**

I've analyzed your scaling requirements and here's a comprehensive plan:

## 🔍 **Current Architecture Assessment**

### **Performance Bottlenecks Identified**
- **Database Connections**: Connection pool limits
- **API Rate Limiting**: Current thresholds too low
- **Caching Strategy**: Insufficient cache layers
- **Load Balancing**: Single point of failure

### **Scaling Requirements Analysis**
- **Target**: 10,000 concurrent users
- **Current Capacity**: 2,500 concurrent users
- **Scaling Factor**: 4x capacity increase needed
- **Performance Critical**: Yes - user experience dependent

## 🚀 **Recommended Scaling Solutions**

### 1. **Horizontal Scaling**
• **Application Servers**: Deploy across multiple instances
• **Load Balancers**: Implement HAProxy or Nginx
• **Database**: Add read replicas and sharding
• **Caching**: Redis cluster for session management

### 2. **Infrastructure Improvements**
• **Auto-scaling Groups**: AWS Auto Scaling or Kubernetes HPA
• **CDN Integration**: CloudFront or Cloudflare for static assets
• **Database Optimization**: Query optimization and indexing
• **Monitoring**: Prometheus + Grafana for metrics

### 3. **Performance Optimizations**
• **Connection Pooling**: Optimize database connections
• **Request Batching**: Reduce API call overhead
• **Async Processing**: Implement background job queues
• **Caching Strategy**: Multi-layer caching approach

## 📊 **Estimated Infrastructure Costs**
- **Additional Compute**: $3,000-8,000/month
- **Load Balancers**: $1,000-2,000/month
- **Database Scaling**: $2,000-5,000/month
- **CDN & Caching**: $500-1,500/month
- **Monitoring Tools**: $300-800/month

## 🔄 **Implementation Timeline**
- **Phase 1** (Weeks 1-2): Infrastructure setup and load balancers
- **Phase 2** (Weeks 3-4): Database scaling and optimization
- **Phase 3** (Weeks 5-6): Performance testing and tuning
- **Phase 4** (Weeks 7-8): Monitoring and alerting setup

## 🎯 **Actionable Next Steps**
• **Immediate**: Set up performance monitoring and baseline metrics
• **Week 1**: Engage infrastructure team for capacity planning
• **Week 2**: Begin load balancer and auto-scaling configuration
• **Week 3**: Start database optimization and read replica setup

Ready to scale your service to handle 10,000 concurrent users!`;
  }
  
  if (lowerMessage.includes('search') || lowerMessage.includes('find')) {
    return `🔍 **Search & Discovery API Solutions**

I've identified the best search and discovery APIs for your application:

## 🔍 **Recommended Search APIs**

### 1. **Elasticsearch API** (95% relevance)
- **Service**: Full-text Search Engine
- **Features**: Advanced search, filtering, aggregation
- **Integration**: REST API with JSON queries
- **Scalability**: Handles millions of documents

### 2. **Algolia Search API** (92% relevance)
- **Service**: Hosted Search Solution
- **Features**: Typo tolerance, faceted search, analytics
- **Integration**: REST API with SDKs
- **Performance**: Sub-50ms response times

### 3. **Typesense API** (88% relevance)
- **Service**: Open-source Search Engine
- **Features**: Fast search, filtering, ranking
- **Integration**: REST API and GraphQL
- **Self-hosted**: Full control over data

## 🚀 **Onboarding Requirements**
- **Elasticsearch**: Self-hosted setup (2-3 days)
- **Algolia**: Account creation, immediate access
- **Typesense**: Self-hosted setup (1-2 days)

## 📚 **Integration Best Practices**
• Implement search result caching for performance
• Use faceted search for better user experience
• Implement search analytics for optimization
• Set up proper indexing strategies
• Handle search result pagination efficiently

Ready to implement powerful search functionality!`;
  }
  
  if (lowerMessage.includes('file') || lowerMessage.includes('upload') || lowerMessage.includes('storage')) {
    return `📁 **File Upload & Storage API Solutions**

I've identified the best file handling APIs for your application:

## 🔍 **Recommended File Storage APIs**

### 1. **AWS S3 API** (95% relevance)
- **Service**: Object Storage
- **Features**: Unlimited storage, versioning, lifecycle policies
- **Integration**: REST API with AWS SDKs
- **Scalability**: Handles petabytes of data

### 2. **Google Cloud Storage API** (92% relevance)
- **Service**: Object Storage
- **Features**: Multi-region, encryption, access control
- **Integration**: REST API with Google Cloud SDKs
- **Global**: Available in multiple regions

### 3. **Azure Blob Storage API** (88% relevance)
- **Service**: Object Storage
- **Features**: Tiered storage, backup, disaster recovery
- **Integration**: REST API with Azure SDKs
- **Enterprise**: Strong enterprise features

## 🚀 **Onboarding Requirements**
- **AWS S3**: Account setup, IAM configuration (1-2 days)
- **Google Cloud**: Project setup, service account (1-2 days)
- **Azure**: Subscription setup, storage account (1-2 days)

## 📚 **Integration Best Practices**
• Implement multipart uploads for large files
• Use presigned URLs for secure file access
• Implement proper file validation and sanitization
• Set up CDN integration for fast file delivery
• Implement file versioning and backup strategies

Ready to handle file uploads and storage!`;
  }
  
  if (lowerMessage.includes('notification') || lowerMessage.includes('real-time') || lowerMessage.includes('websocket')) {
    return `🔔 **Real-time Notification & WebSocket Solutions**

I've identified the best real-time communication APIs for your application:

## 🔍 **Recommended Real-time APIs**

### 1. **Socket.io API** (95% relevance)
- **Service**: Real-time Communication
- **Features**: WebSocket fallback, room management, scaling
- **Integration**: Node.js library with client SDKs
- **Scalability**: Horizontal scaling support

### 2. **Pusher API** (92% relevance)
- **Service**: Hosted Real-time Platform
- **Features**: Channels, events, presence, webhooks
- **Integration**: REST API with client libraries
- **Reliability**: 99.9% uptime SLA

### 3. **Ably API** (88% relevance)
- **Service**: Real-time Messaging Platform
- **Features**: Pub/sub, presence, history, push notifications
- **Integration**: REST API with SDKs
- **Global**: Multi-region deployment

## 🚀 **Onboarding Requirements**
- **Socket.io**: Self-hosted setup (1-2 days)
- **Pusher**: Account creation, immediate access
- **Ably**: Account creation, immediate access

## 📚 **Integration Best Practices**
• Implement connection pooling and reconnection logic
• Use channels for organized message routing
• Implement presence detection for user status
• Set up proper error handling and fallbacks
• Monitor connection health and performance

Ready to implement real-time notifications!`;
  }
  
  if (lowerMessage.includes('security') || lowerMessage.includes('authentication') || lowerMessage.includes('authorization')) {
    return `🔒 **Security & Authentication API Solutions**

I've identified the best security and authentication APIs for your application:

## 🔍 **Recommended Security APIs**

### 1. **Auth0 API** (95% relevance)
- **Service**: Identity & Access Management
- **Features**: OAuth 2.0, OIDC, MFA, social login
- **Integration**: REST API with SDKs
- **Compliance**: SOC 2, GDPR, HIPAA

### 2. **Okta API** (92% relevance)
- **Service**: Identity Platform
- **Features**: SSO, MFA, lifecycle management
- **Integration**: REST API with SDKs
- **Enterprise**: Strong enterprise features

### 3. **Firebase Auth API** (88% relevance)
- **Service**: Authentication Service
- **Features**: Email/password, social login, phone auth
- **Integration**: REST API with client SDKs
- **Google**: Native Google integration

## 🚀 **Onboarding Requirements**
- **Auth0**: Account setup, application configuration (1-2 days)
- **Okta**: Account setup, application configuration (2-3 days)
- **Firebase**: Project setup, configuration (1 day)

## 📚 **Integration Best Practices**
• Implement proper token validation and refresh
• Use secure session management
• Implement role-based access control (RBAC)
• Set up audit logging and monitoring
• Follow OWASP security guidelines

Ready to secure your application!`;
  }
  
  if (lowerMessage.includes('cache') || lowerMessage.includes('performance') || lowerMessage.includes('optimization')) {
    return `⚡ **Caching & Performance Optimization APIs**

I've identified the best caching and performance APIs for your application:

## 🔍 **Recommended Caching APIs**

### 1. **Redis API** (95% relevance)
- **Service**: In-Memory Data Store
- **Features**: Key-value storage, pub/sub, transactions
- **Integration**: Multiple client libraries
- **Performance**: Sub-millisecond response times

### 2. **Memcached API** (92% relevance)
- **Service**: Distributed Memory Caching
- **Features**: Simple key-value storage, high performance
- **Integration**: Multiple client libraries
- **Scalability**: Horizontal scaling support

### 3. **Hazelcast API** (88% relevance)
- **Service**: In-Memory Computing Platform
- **Features**: Distributed caching, clustering, persistence
- **Integration**: Java, .NET, Node.js clients
- **Enterprise**: Strong enterprise features

## 🚀 **Onboarding Requirements**
- **Redis**: Self-hosted setup (1-2 days)
- **Memcached**: Self-hosted setup (1 day)
- **Hazelcast**: Self-hosted setup (2-3 days)

## 📚 **Integration Best Practices**
• Implement cache invalidation strategies
• Use cache warming for critical data
• Monitor cache hit rates and performance
• Implement cache fallback mechanisms
• Use appropriate TTL values for different data types

Ready to optimize your application performance!`;
  }
  
  // Enhanced default response with comprehensive information
  return `🤖 **CatalystAI Comprehensive Analysis**

I've analyzed your query and here's a detailed breakdown:

## 📊 **Query Analysis**
- **Primary Intent**: API Discovery and Integration Guidance
- **Business Context**: Application development and system integration
- **Complexity Level**: Multi-dimensional requirement analysis

## 🔍 **Comprehensive Recommendations**

### **API Discovery Strategy**
• **Multi-dimensional Search**: API functionality, performance, security, and integration patterns
• **Context-Aware Matching**: Business requirements, technical constraints, and scalability needs
• **Performance Analysis**: TPS requirements, response times, and infrastructure impact

### **Integration Best Practices**
• **Architecture Patterns**: Microservices, event-driven, and API-first approaches
• **Security Implementation**: OAuth 2.0, JWT, and secure communication protocols
• **Performance Optimization**: Caching, load balancing, and horizontal scaling

### **Development Workflow**
• **API Onboarding**: Access controls, rate limits, and approval processes
• **Testing Strategy**: Unit, integration, and performance testing approaches
• **Deployment Pipeline**: CI/CD, monitoring, and rollback strategies

## 🚀 **Next Steps**
• **Provide Specific Requirements**: Include performance targets, security needs, and business context
• **Define Integration Scope**: Specify which systems need to be connected
• **Set Timeline Expectations**: Include development and deployment milestones
• **Identify Constraints**: Mention technical limitations and compliance requirements

## 💡 **Pro Tips**
• **Start with Discovery**: Use CatalystAI to find the right APIs for your use case
• **Plan for Scale**: Consider future growth and performance requirements
• **Security First**: Implement proper authentication and authorization from the start
• **Monitor Everything**: Set up comprehensive logging and monitoring

I'm here to help you build robust, scalable, and secure applications! Let me know your specific requirements and I'll provide detailed, actionable guidance.`;
}

// Mock metadata generation for demo purposes
function generateMockMetadata(message: string) {
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes('payment') || lowerMessage.includes('e-commerce')) {
    return {
      query_analysis: {
        primary_intent: "Payment API Integration",
        key_entities: ["payment", "e-commerce", "API integration", "transaction processing"],
        search_dimensions: ["API Discovery", "Integration", "Security", "Performance", "Compliance"],
        business_context: "E-commerce application development with secure payment processing"
      },
      api_discovery: [
        {
          api_name: "Stripe API",
          service: "Payment Processing",
          system: "Payment Gateway",
          endpoints: [
            {
              method: "POST",
              path: "/v1/payment_intents",
              description: "Create payment intent",
              supports_vendor_id: false
            },
            {
              method: "GET",
              path: "/v1/payment_intents/{id}",
              description: "Retrieve payment intent",
              supports_vendor_id: false
            }
          ],
          relevance_score: 0.95,
          performance_score: 0.92,
          citations: ["Stripe API documentation", "Integration guides", "Best practices"]
        },
        {
          api_name: "PayPal API",
          service: "Digital Payments",
          system: "Payment Platform",
          endpoints: [
            {
              method: "POST",
              path: "/v1/orders",
              description: "Create payment order",
              supports_vendor_id: false
            }
          ],
          relevance_score: 0.92,
          performance_score: 0.88,
          citations: ["PayPal API documentation", "Integration guides"]
        }
      ],
      onboarding_requirements: [
        {
          service_name: "Stripe API",
          required_scopes: ["payments:read", "payments:write"],
          authentication: "OAuth 2.0 with JWT",
          rate_limits: "100 requests/second",
          approval_required: false,
          estimated_timeline: "1-2 days",
          dependencies: []
        },
        {
          service_name: "PayPal API",
          required_scopes: ["payments", "orders"],
          authentication: "OAuth 2.0 with JWT",
          rate_limits: "50 requests/second",
          approval_required: false,
          estimated_timeline: "2-3 days",
          dependencies: []
        }
      ],
      integration_recommendations: [
        {
          category: "Security",
          recommendations: [
            "Implement webhook signature verification",
            "Use HTTPS for all API communications",
            "Store API keys securely in environment variables",
            "Implement proper error handling and logging"
          ]
        },
        {
          category: "Performance",
          recommendations: [
            "Implement request caching for static data",
            "Use connection pooling for HTTP clients",
            "Implement retry logic with exponential backoff",
            "Monitor API response times and error rates"
          ]
        }
      ],
      performance_analysis: {
        tps_requirement: 100,
        performance_critical: false,
        scaling_needed: false,
        recommendations: [
          "Start with standard rate limits",
          "Monitor usage patterns and scale as needed",
          "Implement proper error handling for rate limit exceeded"
        ],
        estimated_costs: {
          additional_compute: "$0-100/month",
          load_balancers: "$0/month",
          database_scaling: "$0/month",
          monitoring_tools: "$50-100/month"
        }
      },
      downstream_impact: {
        infrastructure_team: ["No changes required"],
        platform_team: ["Update API gateway policies"],
        security_team: ["Review and approve API access"],
        data_team: ["No changes required"],
        estimated_timeline: {
          infrastructure_scaling: "Not required",
          security_review: "1-2 days",
          performance_testing: "Not required",
          total_implementation: "3-5 days"
        }
      },
      next_steps: [
        {
          priority: "High" as const,
          action: "Set up Stripe and PayPal developer accounts",
          owner: "Development Team",
          timeline: "Day 1"
        },
        {
          priority: "High" as const,
          action: "Implement payment intent creation and processing",
          owner: "Development Team",
          timeline: "Days 2-3"
        },
        {
          priority: "Medium" as const,
          action: "Set up webhook handling for payment status updates",
          owner: "Development Team",
          timeline: "Days 4-5"
        }
      ],
      summary: {
        apis_identified: 2,
        scaling_required: false,
        performance_critical: false,
        estimated_timeline: "3-5 days",
        estimated_cost: "$50-200/month"
      }
    };
  }
  
  if (lowerMessage.includes('authentication') || lowerMessage.includes('oauth')) {
    return {
      query_analysis: {
        primary_intent: "OAuth 2.0 Authentication Implementation",
        key_entities: ["OAuth 2.0", "authentication", "security", "authorization"],
        search_dimensions: ["Security", "Authentication", "Integration", "Best Practices", "Compliance"],
        business_context: "Secure user authentication implementation for web applications"
      },
      api_discovery: [
        {
          api_name: "OAuth 2.0 Provider",
          service: "Authentication Service",
          system: "Identity Management",
          endpoints: [
            {
              method: "GET",
              path: "/oauth/authorize",
              description: "Authorization endpoint",
              supports_vendor_id: false
            },
            {
              method: "POST",
              path: "/oauth/token",
              description: "Token endpoint",
              supports_vendor_id: false
            }
          ],
          relevance_score: 0.95,
          performance_score: 0.90,
          citations: ["OAuth 2.0 RFC 6749", "Security best practices"]
        }
      ],
      onboarding_requirements: [
        {
          service_name: "OAuth 2.0 Implementation",
          required_scopes: ["read", "write"],
          authentication: "Client credentials + Authorization code",
          rate_limits: "1000 requests/hour",
          approval_required: false,
          estimated_timeline: "1-2 weeks",
          dependencies: ["SSL certificate", "Secure storage"]
        }
      ],
      integration_recommendations: [
        {
          category: "Security",
          recommendations: [
            "Use HTTPS for all OAuth communications",
            "Implement proper token storage (httpOnly cookies)",
            "Validate redirect URIs to prevent open redirects",
            "Use PKCE for public clients"
          ]
        },
        {
          category: "Implementation",
          recommendations: [
            "Start with Authorization Code flow for web apps",
            "Implement proper token refresh logic",
            "Set appropriate token expiration times",
            "Log authentication events for security monitoring"
          ]
        }
      ],
      performance_analysis: {
        tps_requirement: 50,
        performance_critical: false,
        scaling_needed: false,
        recommendations: [
          "Implement token caching for performance",
          "Use connection pooling for token validation",
          "Monitor authentication response times"
        ],
        estimated_costs: {
          additional_compute: "$0-100/month",
          load_balancers: "$0/month",
          database_scaling: "$0/month",
          monitoring_tools: "$50-100/month"
        }
      },
      downstream_impact: {
        infrastructure_team: ["No changes required"],
        platform_team: ["Update security policies"],
        security_team: ["Review OAuth implementation"],
        data_team: ["No changes required"],
        estimated_timeline: {
          infrastructure_scaling: "Not required",
          security_review: "3-5 days",
          performance_testing: "1-2 days",
          total_implementation: "1-2 weeks"
        }
      },
      next_steps: [
        {
          priority: "High" as const,
          action: "Choose OAuth 2.0 provider (Auth0, Okta, or custom)",
          owner: "Security Team",
          timeline: "Week 1"
        },
        {
          priority: "High" as const,
          action: "Implement OAuth 2.0 flow in application",
          owner: "Development Team",
          timeline: "Week 1-2"
        },
        {
          priority: "Medium" as const,
          action: "Set up monitoring and logging for authentication",
          owner: "DevOps Team",
          timeline: "Week 2"
        }
      ],
      summary: {
        apis_identified: 1,
        scaling_required: false,
        performance_critical: false,
        estimated_timeline: "1-2 weeks",
        estimated_cost: "$50-200/month"
      }
    };
  }
  
  // Enhanced default metadata for comprehensive responses
  return {
    query_analysis: {
      primary_intent: "Comprehensive API Discovery and Integration Guidance",
      key_entities: ["API integration", "system architecture", "performance", "security"],
      search_dimensions: ["API Discovery", "Integration", "Performance", "Security", "Best Practices"],
      business_context: "Enterprise application development with comprehensive integration requirements"
    },
    api_discovery: [
      {
        api_name: "CatalystAI Discovery Engine",
        service: "API Discovery Service",
        system: "Intelligent Integration Platform",
        endpoints: [
          {
            method: "POST",
            path: "/api/v1/discover",
            description: "Discover relevant APIs for your use case",
            supports_vendor_id: true
          },
          {
            method: "GET",
            path: "/api/v1/recommendations",
            description: "Get integration recommendations",
            supports_vendor_id: true
          }
        ],
        relevance_score: 0.95,
        performance_score: 0.90,
        citations: ["CatalystAI documentation", "Integration guides", "Best practices"]
      }
    ],
    onboarding_requirements: [
      {
        service_name: "CatalystAI Platform",
        required_scopes: ["discovery:read", "integration:read"],
        authentication: "OAuth 2.0 with JWT",
        rate_limits: "1000 requests/hour",
        approval_required: false,
        estimated_timeline: "1 day",
        dependencies: []
      }
    ],
    integration_recommendations: [
      {
        category: "Architecture",
        recommendations: [
          "Start with API discovery to identify relevant services",
          "Plan for scalability from the beginning",
          "Implement proper error handling and monitoring",
          "Use API-first design principles"
        ]
      },
      {
        category: "Security",
        recommendations: [
          "Implement proper authentication and authorization",
          "Use HTTPS for all API communications",
          "Validate and sanitize all inputs",
          "Implement proper logging and monitoring"
        ]
      }
    ],
    performance_analysis: {
      tps_requirement: 100,
      performance_critical: false,
      scaling_needed: false,
      recommendations: [
        "Start with standard performance requirements",
        "Monitor and optimize based on usage patterns",
        "Implement caching strategies for better performance"
      ],
      estimated_costs: {
        additional_compute: "$0-200/month",
        load_balancers: "$0/month",
        database_scaling: "$0/month",
        monitoring_tools: "$50-150/month"
      }
    },
    downstream_impact: {
      infrastructure_team: ["No immediate changes required"],
      platform_team: ["Update API policies as needed"],
      security_team: ["Review and approve API access"],
      data_team: ["No immediate changes required"],
      estimated_timeline: {
        infrastructure_scaling: "Not required",
        security_review: "1-2 days",
        performance_testing: "1 day",
        total_implementation: "2-3 days"
      }
    },
          next_steps: [
        {
          priority: "High" as const,
          action: "Define specific requirements and use case details",
          owner: "Product Team",
          timeline: "Immediate"
        },
        {
          priority: "High" as const,
          action: "Use CatalystAI to discover relevant APIs",
          owner: "Development Team",
          timeline: "Day 1"
        },
        {
          priority: "Medium" as const,
          action: "Plan integration architecture and timeline",
          owner: "Architecture Team",
          timeline: "Week 1"
        }
      ],
    summary: {
      apis_identified: 1,
      scaling_required: false,
      performance_critical: false,
      estimated_timeline: "2-3 days",
      estimated_cost: "$50-350/month"
    }
  };
}
