#!/usr/bin/env python3
"""
🚀 CatalystAI API Discovery & Integration Command Line Tool (Simplified)

This script provides a command-line interface for API discovery using ChromaDB as a vector store 
with OpenAI for intelligent API discovery and integration guidance.

Usage:
    python api_discovery_simple.py --help
    python api_discovery_simple.py search "How do I integrate payment processing?"
    python api_discovery_simple.py init-db
    python api_discovery_simple.py list-apis
    python api_discovery_simple.py test

Requirements:
    - OpenAI API key
    - Python 3.8+
    - Internet connection for API calls
"""

import os
import json
import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Vector database
import chromadb
from chromadb.config import Settings

# OpenAI
import openai

# Utilities
from dotenv import load_dotenv

class APIDiscoveryTool:
    """Main class for API discovery functionality"""
    
    def __init__(self):
        """Initialize the API discovery tool"""
        self.load_environment()
        self.initialize_services()
        self.collection_name = "api_documentation"
        
    def load_environment(self):
        """Load environment variables and OpenAI configuration"""
        load_dotenv()
        
        # Set OpenAI API key
        self.openai_api_key = "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"
        if not self.openai_api_key:
            print("❌ Error: OPENAI_API_KEY not found in environment variables")
            print("   Please set your OpenAI API key in .env file or environment variables")
            print("   You can get one from: https://platform.openai.com/api-keys")
            sys.exit(1)
            
        openai.api_key = self.openai_api_key
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        print("✅ Environment loaded successfully")
        
    def initialize_services(self):
        """Initialize ChromaDB and other services"""
        try:
            # Initialize ChromaDB client with new configuration
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db"
            )
            
            print("✅ Services initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing services: {str(e)}")
            sys.exit(1)
            
    def get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"✅ Using existing collection: {self.collection_name}")
            return collection
        except:
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Comprehensive API documentation and integration guides"}
            )
            print(f"✅ Created new collection: {self.collection_name}")
            return collection
            
    def get_comprehensive_api_dataset(self):
        """Get comprehensive dataset of popular tools and their API specifications"""
        
        api_docs = [
            {
                "api_name": "Stripe Payment API",
                "category": "Payment Processing",
                "description": "Stripe provides APIs for accepting payments, managing subscriptions, and handling financial transactions",
                "endpoints": [
                    "POST /v1/payment_intents - Create payment intent",
                    "GET /v1/payment_intents/{id} - Retrieve payment intent",
                    "POST /v1/charges - Create charge",
                    "POST /v1/customers - Create customer",
                    "POST /v1/subscriptions - Create subscription"
                ],
                "authentication": "Bearer token authentication with secret key",
                "rate_limits": "100 requests per second, 1000 requests per minute",
                "pricing": "2.9% + 30¢ per successful charge",
                "integration_steps": [
                    "1. Create Stripe account and get API keys",
                    "2. Install Stripe library for your language",
                    "3. Initialize Stripe with your secret key",
                    "4. Create payment intents for transactions",
                    "5. Handle webhooks for payment status updates"
                ],
                "best_practices": [
                    "Always use HTTPS in production",
                    "Implement idempotency keys",
                    "Handle webhook signature verification",
                    "Store sensitive data securely",
                    "Use test mode for development"
                ],
                "common_use_cases": [
                    "E-commerce payments",
                    "Subscription billing",
                    "Marketplace transactions",
                    "Digital goods sales",
                    "Recurring payments"
                ],
                "sdk_languages": ["Python", "JavaScript", "Java", "Ruby", "PHP", "Go", "C#"],
                "documentation_url": "https://stripe.com/docs/api"
            },
            {
                "api_name": "Google Maps API",
                "category": "Maps & Location",
                "description": "Google Maps provides location services, geocoding, directions, and mapping capabilities",
                "endpoints": [
                    "GET /maps/api/geocode/json - Geocoding",
                    "GET /maps/api/directions/json - Directions",
                    "GET /maps/api/place/details/json - Place details",
                    "GET /maps/api/places/nearby/json - Nearby places",
                    "GET /maps/api/distancematrix/json - Distance matrix"
                ],
                "authentication": "API key authentication with billing account",
                "rate_limits": "1000 requests per day (free tier), 100,000 requests per day (paid)",
                "pricing": "Free tier available, then $5 per 1000 requests",
                "integration_steps": [
                    "1. Get Google Cloud project and enable Maps API",
                    "2. Create API key with appropriate restrictions",
                    "3. Install Google Maps client library",
                    "4. Initialize client with API key",
                    "5. Make API calls for location services"
                ],
                "best_practices": [
                    "Restrict API key to specific domains/IPs",
                    "Implement request caching",
                    "Handle rate limiting gracefully",
                    "Use appropriate coordinate systems",
                    "Monitor usage and costs"
                ],
                "common_use_cases": [
                    "Address validation",
                    "Route planning",
                    "Location-based services",
                    "Business listings",
                    "Geospatial analysis"
                ],
                "sdk_languages": ["JavaScript", "Python", "Java", "iOS", "Android"],
                "documentation_url": "https://developers.google.com/maps/documentation"
            },
            {
                "api_name": "Auth0 API",
                "category": "Authentication & Security",
                "description": "Auth0 provides identity and access management with OAuth 2.0, OIDC, and social login support",
                "endpoints": [
                    "POST /oauth/token - Get access token",
                    "GET /userinfo - Get user information",
                    "POST /dbconnections/signup - User registration",
                    "POST /dbconnections/login - User login",
                    "GET /api/v2/users - Manage users"
                ],
                "authentication": "OAuth 2.0 with JWT tokens",
                "rate_limits": "1000 requests per minute",
                "pricing": "Free tier available, then $23/month for 7,000 users",
                "integration_steps": [
                    "1. Create Auth0 account and application",
                    "2. Configure OAuth 2.0 settings",
                    "3. Implement authorization code flow",
                    "4. Handle token validation and refresh",
                    "5. Implement user profile management"
                ],
                "best_practices": [
                    "Use PKCE for public clients",
                    "Implement proper token storage",
                    "Validate JWT signatures",
                    "Handle token expiration gracefully",
                    "Use secure redirect URIs"
                ],
                "common_use_cases": [
                    "User authentication",
                    "Single sign-on (SSO)",
                    "Social login integration",
                    "Multi-factor authentication",
                    "API authorization"
                ],
                "sdk_languages": ["JavaScript", "Python", "Java", "C#", "PHP", "Ruby"],
                "documentation_url": "https://auth0.com/docs/api"
            },
            {
                "api_name": "Twilio API",
                "category": "Communication & Notifications",
                "description": "Twilio provides APIs for SMS, voice, video, WhatsApp messaging, and email",
                "endpoints": [
                    "POST /2010-04-01/Accounts/{AccountSid}/Messages.json - Send SMS",
                    "POST /2010-04-01/Accounts/{AccountSid}/Calls.json - Make voice call",
                    "POST /2010-04-01/Accounts/{AccountSid}/Video/Rooms.json - Create video room",
                    "POST /2010-04-01/Accounts/{AccountSid}/Verify/Verifications.json - Send verification code"
                ],
                "authentication": "Account SID and Auth Token",
                "rate_limits": "1000 requests per second",
                "pricing": "SMS: $0.0079 per message, Voice: $0.0085 per minute",
                "integration_steps": [
                    "1. Create Twilio account and get credentials",
                    "2. Install Twilio SDK for your language",
                    "3. Initialize client with credentials",
                    "4. Implement message sending functionality",
                    "5. Handle webhooks for delivery status"
                ],
                "best_practices": [
                    "Store credentials securely",
                    "Implement retry logic for failed requests",
                    "Use webhooks for real-time updates",
                    "Monitor usage and costs",
                    "Handle rate limiting gracefully"
                ],
                "common_use_cases": [
                    "SMS notifications",
                    "Voice calls",
                    "Two-factor authentication",
                    "Customer support",
                    "Appointment reminders"
                ],
                "sdk_languages": ["Python", "JavaScript", "Java", "C#", "PHP", "Ruby", "Go"],
                "documentation_url": "https://www.twilio.com/docs"
            },
            {
                "api_name": "Slack API",
                "category": "Team Collaboration",
                "description": "Slack provides APIs for messaging, team collaboration, and workflow automation",
                "endpoints": [
                    "POST /api/chat.postMessage - Send message to channel",
                    "GET /api/conversations.list - List channels",
                    "POST /api/users.lookupByEmail - Find user by email",
                    "POST /api/views.open - Open modal view"
                ],
                "authentication": "OAuth 2.0 with Bot Token or User Token",
                "rate_limits": "50 requests per second for most endpoints",
                "pricing": "Free tier available, then $7.25/user/month",
                "integration_steps": [
                    "1. Create Slack app in workspace",
                    "2. Configure OAuth scopes and permissions",
                    "3. Install app to workspace",
                    "4. Use Bot Token for API calls",
                    "5. Handle interactive components and events"
                ],
                "best_practices": [
                    "Use appropriate OAuth scopes",
                    "Handle rate limiting gracefully",
                    "Implement proper error handling",
                    "Use webhooks for real-time events",
                    "Follow Slack's design guidelines"
                ],
                "common_use_cases": [
                    "Team notifications",
                    "Workflow automation",
                    "Customer support integration",
                    "Project management",
                    "Alert systems"
                ],
                "sdk_languages": ["Python", "JavaScript", "Java", "C#", "PHP", "Ruby"],
                "documentation_url": "https://api.slack.com/"
            }
        ]
        
        print(f"📚 Created dataset with {len(api_docs)} API documentation entries")
        return api_docs
        
    def store_apis_in_chromadb(self, collection):
        """Store API documentation in ChromaDB"""
        api_docs = self.get_comprehensive_api_dataset()
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        print("🔄 Storing APIs in ChromaDB...")
        
        for i, doc in enumerate(api_docs):
            # Create comprehensive text representation
            doc_text = f"""
API: {doc['api_name']}
Category: {doc['category']}
Description: {doc['description']}
Endpoints: {', '.join(doc['endpoints'])}
Authentication: {doc['authentication']}
Rate Limits: {doc['rate_limits']}
Pricing: {doc['pricing']}
Integration Steps: {' '.join(doc['integration_steps'])}
Best Practices: {' '.join(doc['best_practices'])}
Use Cases: {' '.join(doc['common_use_cases'])}
SDK Languages: {', '.join(doc['sdk_languages'])}
Documentation: {doc['documentation_url']}
""".strip()
            
            # Convert complex data structures to strings for ChromaDB metadata
            metadata = {
                'api_name': doc['api_name'],
                'category': doc['category'],
                'description': doc['description'],
                'endpoints': ', '.join(doc['endpoints']),
                'authentication': doc['authentication'],
                'rate_limits': doc['rate_limits'],
                'pricing': doc['pricing'],
                'integration_steps': ', '.join(doc['integration_steps']),
                'best_practices': ', '.join(doc['best_practices']),
                'common_use_cases': ', '.join(doc['common_use_cases']),
                'sdk_languages': ', '.join(doc['sdk_languages']),
                'documentation_url': doc['documentation_url']
            }
            
            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(f"api_{i+1}")
        
        # Add documents to ChromaDB
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Successfully stored {len(documents)} API documentation entries in ChromaDB")
        print(f"📊 Total documents in collection: {collection.count()}")
        
    def discover_api_integration(self, query: str, top_k: int = 5):
        """Discover relevant APIs and provide integration guidance using ChromaDB and OpenAI"""
        
        collection = self.get_or_create_collection()
        
        print(f"🔍 Searching for APIs related to: {query}")
        
        # Search ChromaDB for relevant APIs
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Extract relevant API information
        relevant_apis = []
        for i, (doc, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
            # Parse SDK languages back to list if needed
            sdk_languages = metadata.get('sdk_languages', '').split(', ') if metadata.get('sdk_languages') else []
            
            relevant_apis.append({
                'api_name': metadata['api_name'],
                'category': metadata['category'],
                'relevance_score': 1 - distance,
                'description': metadata['description'],
                'pricing': metadata.get('pricing', 'N/A'),
                'sdk_languages': sdk_languages
            })
        
        print(f"✅ Found {len(relevant_apis)} relevant APIs")
        
        # Create comprehensive prompt for OpenAI
        system_prompt = """
        You are an expert API integration consultant with deep knowledge of web development, security, and best practices.
        Based on the user's query and the relevant APIs found, provide:

        1. **API Recommendations**: Which APIs are most suitable and why
        2. **Integration Strategy**: Step-by-step integration approach
        3. **Best Practices**: Security, performance, and reliability considerations
        4. **Common Pitfalls**: What to avoid during integration
        5. **Next Steps**: Actionable next steps for the developer
        6. **Cost Considerations**: Pricing and scaling implications

        Be specific, practical, and developer-friendly. Include code examples where relevant.
        Focus on real-world implementation challenges and solutions.
        """
        
        user_prompt = f"""
        User Query: {query}

        Relevant APIs Found:
        {json.dumps(relevant_apis, indent=2)}

        Please provide comprehensive integration guidance including:
        - Which API(s) to use and why
        - Step-by-step integration process
        - Security considerations
        - Performance optimization tips
        - Common mistakes to avoid
        - Code examples where helpful
        - Cost and scaling considerations
        """
        
        # Get OpenAI response
        try:
            print("🤖 Getting integration guidance from OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            guidance = response.choices[0].message.content
            print("✅ Received guidance from OpenAI")
            
        except Exception as e:
            guidance = f"Error getting OpenAI response: {str(e)}"
            print(f"❌ Error: {str(e)}")
        
        return {
            'query': query,
            'relevant_apis': relevant_apis,
            'integration_guidance': guidance,
            'timestamp': datetime.now().isoformat()
        }
        
    def list_stored_apis(self):
        """List all APIs stored in ChromaDB"""
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            count = collection.count()
            
            if count == 0:
                print("📭 No APIs found in database. Run 'init-db' first.")
                return
                
            print(f"📚 Found {count} APIs in database:")
            print("=" * 80)
            
            # Get all documents to display
            results = collection.get()
            
            for i, (id, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
                print(f"{i+1:2d}. {metadata['api_name']}")
                print(f"     Category: {metadata['category']}")
                print(f"     Description: {metadata['description'][:100]}...")
                print(f"     Pricing: {metadata.get('pricing', 'N/A')}")
                print(f"     SDK Languages: {metadata.get('sdk_languages', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing APIs: {str(e)}")
            
    def test_sample_queries(self):
        """Test the system with sample queries"""
        test_queries = [
            "How do I integrate payment processing in my e-commerce app?",
            "I need to implement user authentication with OAuth 2.0",
            "How can I send SMS notifications to users?",
            "What's the best way to implement file storage?",
            "How do I set up email marketing campaigns?"
        ]
        
        print("🧪 Testing API Discovery System with Sample Queries")
        print("=" * 80)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 60)
            
            result = self.discover_api_integration(query, top_k=3)
            
            print(f"📋 Relevant APIs Found:")
            for api in result['relevant_apis']:
                print(f"  • {api['api_name']} ({api['category']}) - Relevance: {api['relevance_score']:.2f}")
            
            print(f"\n🤖 Integration Guidance:")
            print(result['integration_guidance'][:500] + "..." if len(result['integration_guidance']) > 500 else result['integration_guidance'])
            
            if i < len(test_queries):
                print("\n" + "="*80)

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="🚀 CatalystAI API Discovery & Integration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_discovery_simple.py init-db                    # Initialize database with API data
  python api_discovery_simple.py search "payment processing" # Search for payment APIs
  python api_discovery_simple.py list-apis                  # List all stored APIs
  python api_discovery_simple.py test                       # Run sample queries
        """
    )
    
    parser.add_argument('command', choices=['init-db', 'search', 'list-apis', 'test'],
                       help='Command to execute')
    
    parser.add_argument('query', nargs='?', help='Search query (required for search command)')
    
    parser.add_argument('--top-k', type=int, default=5,
                       help='Number of top results to return (default: 5)')
    
    args = parser.parse_args()
    
    # Initialize the tool
    tool = APIDiscoveryTool()
    
    try:
        if args.command == 'init-db':
            print("🚀 Initializing API Discovery Database...")
            collection = tool.get_or_create_collection()
            tool.store_apis_in_chromadb(collection)
            print("✅ Database initialization complete!")
            
        elif args.command == 'search':
            if not args.query:
                print("❌ Error: Query is required for search command")
                sys.exit(1)
                
            print(f"🔍 Searching for: {args.query}")
            result = tool.discover_api_integration(args.query, args.top_k)
            
            print("\n" + "="*80)
            print("📋 **SEARCH RESULTS**")
            print("="*80)
            
            print(f"\n🔍 **Relevant APIs Found:**")
            for api in result['relevant_apis']:
                print(f"• {api['api_name']} ({api['category']})")
                print(f"  Relevance: {api['relevance_score']:.2f}")
                print(f"  Description: {api['description'][:100]}...")
                print(f"  Pricing: {api['pricing']}")
                print(f"  SDK Languages: {', '.join(api['sdk_languages'])}")
                print()
            
            print(f"\n🤖 **Integration Guidance:**")
            print(result['integration_guidance'])
            
        elif args.command == 'list-apis':
            tool.list_stored_apis()
            
        elif args.command == 'test':
            tool.test_sample_queries()
            
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()