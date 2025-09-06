#!/usr/bin/env python3
"""
🔍 CatalystAI Intelligent API Search Tool

This tool provides intelligent search capabilities for the onboarded APIs in ChromaDB.
It uses OpenAI to understand complex queries and find the most relevant APIs.

Usage:
    python intelligent_search.py "I need to process payments and send notifications"
    python intelligent_search.py "How do I integrate authentication and user management?"
    python intelligent_search.py "What APIs do I need for an e-commerce platform?"
    python intelligent_search.py "Compare payment processing APIs"
"""

import os
import json
import argparse
import sys
from typing import List, Dict, Any, Optional
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

class IntelligentAPISearch:
    """Intelligent API search using OpenAI and ChromaDB"""
    
    def __init__(self):
        """Initialize the intelligent search tool"""
        self.load_environment()
        self.initialize_services()
        self.collection_name = "api_documentation"
        
    def load_environment(self):
        """Load environment variables and OpenAI configuration"""
        load_dotenv()
        
        # Set OpenAI API key
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            print("❌ Error: OPENAI_API_KEY not found in environment variables")
            print("   Please set your OpenAI API key in .env file")
            sys.exit(1)
            
        openai.api_key = self.openai_api_key
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        print("✅ Environment loaded successfully")
        
    def initialize_services(self):
        """Initialize ChromaDB and other services"""
        try:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            print("✅ Services initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing services: {str(e)}")
            sys.exit(1)
            
    def get_collection(self):
        """Get the API documentation collection"""
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            return collection
        except Exception as e:
            print(f"❌ Error getting collection: {str(e)}")
            return None
            
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Use OpenAI to analyze the query intent and extract search criteria"""
        
        system_prompt = """
        You are an expert API analyst. Analyze the user's query to understand their intent and extract search criteria.
        
        Return a JSON object with the following structure:
        {
            "intent": "primary intent (e.g., 'payment_processing', 'authentication', 'notifications', 'ecommerce')",
            "primary_category": "main API category needed",
            "secondary_categories": ["additional categories that might be relevant"],
            "key_features": ["specific features or capabilities needed"],
            "complexity_level": "beginner|intermediate|advanced",
            "integration_type": "simple|complex|enterprise",
            "search_keywords": ["keywords to use for vector search"],
            "constraints": ["any constraints like pricing, performance, etc."]
        }
        
        Be specific and practical. Focus on what APIs the user actually needs.
        """
        
        user_prompt = f"""
        Analyze this query to understand what APIs the user needs:
        
        Query: {query}
        
        Think about:
        1. What is the main functionality they're trying to implement?
        2. What types of APIs would be most relevant?
        3. Are there any specific requirements or constraints?
        4. What would be the best search keywords?
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print("❌ Could not parse query analysis")
                return {}
                
        except Exception as e:
            print(f"❌ Error analyzing query: {str(e)}")
            return {}
            
    def search_apis_intelligently(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """Intelligently search for APIs based on query analysis"""
        
        print(f"🔍 Analyzing query: {query}")
        
        # Step 1: Analyze query intent
        query_analysis = self.analyze_query_intent(query)
        
        if not query_analysis:
            print("❌ Failed to analyze query")
            return {}
            
        print(f"📊 Query Analysis:")
        print(f"   Intent: {query_analysis.get('intent', 'N/A')}")
        print(f"   Primary Category: {query_analysis.get('primary_category', 'N/A')}")
        print(f"   Complexity: {query_analysis.get('complexity_level', 'N/A')}")
        
        # Step 2: Get collection
        collection = self.get_collection()
        if not collection:
            return {}
            
        # Step 3: Search with multiple strategies
        search_results = []
        
        # Strategy 1: Search with original query
        results1 = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Strategy 2: Search with extracted keywords
        keywords = query_analysis.get('search_keywords', [])
        if keywords:
            keyword_query = ' '.join(keywords)
            results2 = collection.query(
                query_texts=[keyword_query],
                n_results=top_k
            )
            
            # Combine and deduplicate results
            all_results = []
            
            # Add results from original query
            for i, (doc, metadata, distance) in enumerate(zip(results1['documents'][0], results1['metadatas'][0], results1['distances'][0])):
                all_results.append({
                    'api_name': metadata['api_name'],
                    'category': metadata['category'],
                    'description': metadata['description'],
                    'relevance_score': 1 - distance,
                    'source': 'original_query',
                    'metadata': metadata
                })
                
            # Add results from keyword search
            for i, (doc, metadata, distance) in enumerate(zip(results2['documents'][0], results2['metadatas'][0], results2['distances'][0])):
                all_results.append({
                    'api_name': metadata['api_name'],
                    'category': metadata['category'],
                    'description': metadata['description'],
                    'relevance_score': 1 - distance,
                    'source': 'keyword_search',
                    'metadata': metadata
                })
                
            # Deduplicate and sort by relevance
            seen_apis = set()
            unique_results = []
            for result in all_results:
                if result['api_name'] not in seen_apis:
                    seen_apis.add(result['api_name'])
                    unique_results.append(result)
                    
            search_results = sorted(unique_results, key=lambda x: x['relevance_score'], reverse=True)[:top_k]
        else:
            # Fallback to original query results
            for i, (doc, metadata, distance) in enumerate(zip(results1['documents'][0], results1['metadatas'][0], results1['distances'][0])):
                search_results.append({
                    'api_name': metadata['api_name'],
                    'category': metadata['category'],
                    'description': metadata['description'],
                    'relevance_score': 1 - distance,
                    'source': 'original_query',
                    'metadata': metadata
                })
                
        print(f"✅ Found {len(search_results)} relevant APIs")
        
        return {
            'query_analysis': query_analysis,
            'search_results': search_results,
            'total_apis_found': len(search_results)
        }
        
    def generate_comprehensive_recommendations(self, query: str, search_data: Dict[str, Any]) -> str:
        """Generate comprehensive API recommendations using OpenAI"""
        
        query_analysis = search_data['query_analysis']
        search_results = search_data['search_results']
        
        system_prompt = """
        You are an expert API integration consultant and solution architect. 
        Provide comprehensive, actionable recommendations for API integration.
        
        Structure your response with:
        
        ## 🎯 **Query Analysis**
        - Brief summary of what the user is trying to accomplish
        - Key requirements and constraints identified
        
        ## 🔍 **API Recommendations**
        - **Primary APIs**: Most suitable APIs for the main functionality
        - **Secondary APIs**: Supporting APIs that might be useful
        - **Why These APIs**: Justification for each recommendation
        
        ## 🚀 **Integration Strategy**
        - **Architecture Overview**: How the APIs work together
        - **Implementation Steps**: Step-by-step integration process
        - **Code Examples**: Relevant code snippets where helpful
        
        ## 🔒 **Security & Best Practices**
        - **Authentication**: How to handle API authentication
        - **Security Considerations**: Important security measures
        - **Performance Tips**: Optimization strategies
        
        ## 💰 **Cost & Scaling**
        - **Pricing Overview**: Cost implications of each API
        - **Scaling Considerations**: How costs scale with usage
        - **Budget Recommendations**: Cost-effective approaches
        
        ## ⚠️ **Common Pitfalls**
        - **What to Avoid**: Common mistakes and how to avoid them
        - **Troubleshooting**: Common issues and solutions
        
        ## 📋 **Next Steps**
        - **Immediate Actions**: What to do first
        - **Development Timeline**: Suggested implementation timeline
        - **Resources**: Additional resources and documentation
        
        Be specific, practical, and developer-friendly. Include real-world examples and code snippets.
        """
        
        user_prompt = f"""
        Query: {query}
        
        Query Analysis:
        {json.dumps(query_analysis, indent=2)}
        
        Available APIs:
        {json.dumps(search_results, indent=2)}
        
        Please provide comprehensive integration guidance based on the user's needs and available APIs.
        Focus on practical implementation and real-world scenarios.
        """
        
        try:
            print("🤖 Generating comprehensive recommendations...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error generating recommendations: {str(e)}"
            
    def search_and_recommend(self, query: str) -> Dict[str, Any]:
        """Main method to search APIs and generate recommendations"""
        
        print("🚀 Starting intelligent API search...")
        print("=" * 60)
        
        # Step 1: Search for relevant APIs
        search_data = self.search_apis_intelligently(query)
        
        if not search_data or not search_data['search_results']:
            print("❌ No relevant APIs found")
            return {
                'query': query,
                'error': 'No relevant APIs found',
                'timestamp': datetime.now().isoformat()
            }
            
        # Step 2: Generate comprehensive recommendations
        recommendations = self.generate_comprehensive_recommendations(query, search_data)
        
        # Step 3: Return complete results
        return {
            'query': query,
            'query_analysis': search_data['query_analysis'],
            'search_results': search_data['search_results'],
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
    def list_available_apis(self):
        """List all available APIs in the database"""
        try:
            collection = self.get_collection()
            if not collection:
                return
                
            count = collection.count()
            print(f"📚 Available APIs in database: {count}")
            print("=" * 60)
            
            if count == 0:
                print("No APIs found. Run the API onboard agent first.")
                return
                
            # Get all APIs
            results = collection.get()
            
            # Group by category
            categories = {}
            for i, metadata in enumerate(results['metadatas']):
                category = metadata.get('category', 'Unknown')
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    'name': metadata['api_name'],
                    'description': metadata.get('description', 'N/A')[:100] + '...',
                    'pricing': metadata.get('pricing', 'N/A'),
                    'sdk_languages': metadata.get('sdk_languages', 'N/A')
                })
                
            # Display by category
            for category, apis in categories.items():
                print(f"\n📂 **{category}** ({len(apis)} APIs)")
                print("-" * 40)
                for api in apis:
                    print(f"  • {api['name']}")
                    print(f"    {api['description']}")
                    print(f"    Pricing: {api['pricing']}")
                    print(f"    SDKs: {api['sdk_languages']}")
                    print()
                    
        except Exception as e:
            print(f"❌ Error listing APIs: {str(e)}")

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="🔍 CatalystAI Intelligent API Search Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python intelligent_search.py "I need to process payments and send notifications"
  python intelligent_search.py "How do I integrate authentication and user management?"
  python intelligent_search.py "What APIs do I need for an e-commerce platform?"
  python intelligent_search.py "Compare payment processing APIs"
  python intelligent_search.py --list-apis
        """
    )
    
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--list-apis', action='store_true', help='List all available APIs')
    
    args = parser.parse_args()
    
    # Initialize the search tool
    search_tool = IntelligentAPISearch()
    
    try:
        if args.list_apis:
            search_tool.list_available_apis()
        elif args.query:
            # Perform search and generate recommendations
            results = search_tool.search_and_recommend(args.query)
            
            if 'error' in results:
                print(f"❌ {results['error']}")
                return
                
            # Display results
            print("\n" + "=" * 60)
            print("📋 **SEARCH RESULTS & RECOMMENDATIONS**")
            print("=" * 60)
            
            print(f"\n🔍 **Query**: {results['query']}")
            print(f"📊 **Analysis**: {results['query_analysis'].get('intent', 'N/A')} - {results['query_analysis'].get('complexity_level', 'N/A')}")
            print(f"📈 **APIs Found**: {len(results['search_results'])}")
            
            print(f"\n🎯 **Top APIs Found**:")
            for i, api in enumerate(results['search_results'][:5], 1):
                print(f"{i}. **{api['api_name']}** ({api['category']})")
                print(f"   Relevance: {api['relevance_score']:.2f}")
                print(f"   Description: {api['description'][:100]}...")
                print()
                
            print("\n" + "=" * 60)
            print("🚀 **COMPREHENSIVE RECOMMENDATIONS**")
            print("=" * 60)
            print(results['recommendations'])
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\n👋 Search cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
