#!/usr/bin/env python3
"""
🚀 CatalystAI API Onboard Agent

This agent searches the web for API specifications and prepares them in our 
application-specific format for ChromaDB storage.

Usage:
    python api_onboard_agent.py --help
    python api_onboard_agent.py onboard "Stripe API"
    python api_onboard_agent.py onboard "Google Maps API" --output-file stripe_api_spec.json
    python api_onboard_agent.py search "payment processing" --limit 5

Features:
    - Web search for API documentation
    - Automatic API specification extraction
    - Format conversion to our ChromaDB format
    - Integration with existing API discovery system
"""

import os
import json
import argparse
import sys
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Web scraping and content extraction
import requests
from bs4 import BeautifulSoup
import urllib.parse

# OpenAI for intelligent processing
import openai
from dotenv import load_dotenv

# Data processing
import pandas as pd

class APIOnboardAgent:
    """Agent for onboarding new APIs by searching the web and extracting specifications"""
    
    def __init__(self):
        """Initialize the API Onboard Agent"""
        self.load_environment()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
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
        
    def search_web_for_api_docs(self, product_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for API documentation URLs using OpenAI"""
        
        print(f"🔍 Finding API documentation URLs for: {product_name}")
        
        # Use OpenAI to find the correct documentation URLs
        search_results = self.find_api_docs_with_ai(product_name, limit)
        
        if not search_results:
            print("🔄 Trying fallback: Direct Google API documentation URLs")
            fallback_urls = self.get_google_api_fallback_urls(product_name)
            
            for url in fallback_urls:
                try:
                    print(f"🔄 Trying fallback URL: {url}")
                    response = requests.get(url, headers=self.headers, timeout=10)
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        search_results.append({
                            'title': f"{product_name} API Documentation",
                            'url': url,
                            'snippet': f"Official {product_name} API documentation",
                            'source': 'fallback'
                        })
                        print(f"✅ Found fallback URL: {url}")
                        break
                    else:
                        print(f"   Failed with status: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ Fallback URL failed: {url} - {str(e)}")
            
        print(f"✅ Found {len(search_results)} relevant API documentation sources")
        return search_results
        
    def find_api_docs_with_ai(self, product_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Use OpenAI to find the correct API documentation URLs"""
        
        system_prompt = """
        You are an expert API documentation finder. Given an API name, find the official documentation URLs.
        
        Return a JSON array of documentation URLs with the following structure:
        [
            {
                "title": "Official API Name Documentation",
                "url": "https://official-docs-url.com",
                "snippet": "Brief description of what this URL contains",
                "priority": 1
            }
        ]
        
        Rules:
        1. Only return official documentation URLs (not third-party sites)
        2. Prioritize the main documentation page
        3. Include reference documentation if available
        4. For Google APIs, use developers.google.com URLs
        5. For AWS APIs, use docs.aws.amazon.com URLs
        6. For Microsoft APIs, use docs.microsoft.com URLs
        7. For other APIs, find their official developer documentation
        
        Return only valid JSON, no additional text.
        """
        
        user_prompt = f"""
        Find the official API documentation URLs for: {product_name}
        
        Please provide the most relevant and official documentation URLs for this API.
        Focus on the main documentation page and reference documentation.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                urls_data = json.loads(json_match.group())
                
                # Validate URLs and convert to search results format
                search_results = []
                for url_data in urls_data[:limit]:
                    if 'url' in url_data and url_data['url'].startswith('http'):
                        search_results.append({
                            'title': url_data.get('title', f"{product_name} API Documentation"),
                            'url': url_data['url'],
                            'snippet': url_data.get('snippet', 'Official API documentation'),
                            'source': 'openai'
                        })
                
                print(f"✅ OpenAI found {len(search_results)} documentation URLs")
                return search_results
            else:
                print("❌ Could not parse JSON from OpenAI response")
                return []
                
        except Exception as e:
            print(f"❌ Error with OpenAI URL discovery: {str(e)}")
            return []
        
    def get_google_api_fallback_urls(self, product_name: str) -> List[str]:
        """Get fallback URLs for Google APIs"""
        
        # Common Google API documentation patterns
        api_patterns = {
            'adsense': [
                'https://developers.google.com/adsense/management',
                'https://developers.google.com/adsense/management/api',
                'https://developers.google.com/adsense/management/api/v1',
                'https://developers.google.com/adsense/management/api/reference'
            ],
            'ads': [
                'https://developers.google.com/google-ads/api',
                'https://developers.google.com/google-ads/api/docs',
                'https://developers.google.com/google-ads/api/reference'
            ],
            'analytics': [
                'https://developers.google.com/analytics/devguides/reporting/core/v4',
                'https://developers.google.com/analytics/devguides/reporting/data/v1',
                'https://developers.google.com/analytics/devguides/reporting'
            ],
            'maps': [
                'https://developers.google.com/maps/documentation',
                'https://developers.google.com/maps/documentation/javascript',
                'https://developers.google.com/maps/documentation/geocoding'
            ],
            'cloud': [
                'https://cloud.google.com/apis/docs',
                'https://cloud.google.com/apis/library',
                'https://cloud.google.com/apis'
            ]
        }
        
        # Find matching patterns
        product_lower = product_name.lower()
        for key, urls in api_patterns.items():
            if key in product_lower:
                return urls
                
        # Generic Google API documentation
        return [
            'https://developers.google.com/apis-explorer',
            'https://developers.google.com/apis',
            'https://cloud.google.com/apis'
        ]
        
    def extract_api_spec_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract API specifications from a given URL"""
        
        try:
            print(f"📄 Extracting API specs from: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content with better structure
            text_content = ""
            
            # Try to find main content areas
            main_content_selectors = [
                'main',
                'article',
                '.devsite-content',
                '.devsite-main-content',
                '.content',
                '.main-content',
                '#content',
                '#main'
            ]
            
            main_content = None
            for selector in main_content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                text_content = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body content
                text_content = soup.get_text(separator=' ', strip=True)
            
            # Clean up the text
            text_content = re.sub(r'\s+', ' ', text_content)  # Remove extra whitespace
            text_content = text_content.strip()
            
            # Use OpenAI to extract API specifications
            api_spec = self.extract_api_spec_with_ai(text_content, url)
            
            if api_spec:
                print(f"✅ Successfully extracted API specifications")
                return api_spec
            else:
                print(f"❌ Failed to extract API specifications")
                return None
                
        except Exception as e:
            print(f"❌ Error extracting from {url}: {str(e)}")
            return None
            
    def extract_api_spec_with_ai(self, content: str, url: str) -> Optional[Dict[str, Any]]:
        """Use OpenAI to intelligently extract API specifications from content"""
        
        # Truncate content to avoid token limits
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            
        system_prompt = """
        You are an expert API analyst. Extract comprehensive API specifications from the provided content.
        
        For Google APIs specifically, look for:
        - REST endpoints and their HTTP methods
        - Authentication methods (OAuth 2.0, API keys, etc.)
        - Rate limiting information
        - SDK libraries and supported languages
        - Pricing information
        - Integration guides and tutorials
        
        Return a JSON object with the following structure:
        {
            "api_name": "Name of the API",
            "category": "Category (e.g., Advertising, Payment Processing, Maps & Location, etc.)",
            "description": "Comprehensive description of what the API does",
            "endpoints": ["List of key endpoints with HTTP methods and descriptions"],
            "authentication": "Authentication method and requirements (OAuth 2.0, API keys, etc.)",
            "rate_limits": "Rate limiting information (requests per second/minute)",
            "pricing": "Pricing information if available",
            "integration_steps": ["Step-by-step integration instructions"],
            "best_practices": ["Security and performance best practices"],
            "common_use_cases": ["Common use cases and applications"],
            "sdk_languages": ["Supported programming languages and SDKs"],
            "documentation_url": "URL to official documentation"
        }
        
        If information is not available, use "N/A" or empty arrays as appropriate.
        Be specific and detailed in your extraction. For Google APIs, try to find actual endpoint URLs and authentication details.
        """
        
        user_prompt = f"""
        Extract API specifications from this content:
        
        URL: {url}
        Content: {content}
        
        Provide a comprehensive JSON response with all available API information.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                api_spec = json.loads(json_match.group())
                return api_spec
            else:
                print(f"❌ Could not parse JSON from AI response")
                return None
                
        except Exception as e:
            print(f"❌ Error with OpenAI extraction: {str(e)}")
            return None
            
    def onboard_api(self, product_name: str, output_file: Optional[str] = None, save_to_chromadb: bool = False) -> Dict[str, Any]:
        """Main function to onboard a new API"""
        
        print(f"🚀 Starting API onboarding process for: {product_name}")
        print("=" * 60)
        
        # Step 1: Search for API documentation
        search_results = self.search_web_for_api_docs(product_name, limit=5)
        
        if not search_results:
            print("❌ No API documentation found")
            return {}
            
        # Step 2: Extract API specifications from top results
        api_specs = []
        
        for i, result in enumerate(search_results[:3], 1):
            print(f"\n📋 Processing result {i}/{len(search_results[:3])}: {result['title']}")
            
            api_spec = self.extract_api_spec_from_url(result['url'])
            if api_spec:
                api_specs.append(api_spec)
                
            # Add delay to be respectful
            time.sleep(2)
            
        if not api_specs:
            print("❌ Failed to extract API specifications from any source")
            return {}
            
        # Step 3: Merge and consolidate API specifications
        consolidated_spec = self.consolidate_api_specs(api_specs, product_name)
        
        # Step 4: Save to file if requested
        if output_file:
            self.save_api_spec(consolidated_spec, output_file)
            
        # Step 5: Save to ChromaDB if requested
        if save_to_chromadb:
            self.save_to_chromadb(consolidated_spec)
            
        # Step 6: Return the consolidated specification
        return consolidated_spec
        
    def consolidate_api_specs(self, api_specs: List[Dict[str, Any]], product_name: str) -> Dict[str, Any]:
        """Consolidate multiple API specifications into one comprehensive spec"""
        
        print(f"🔧 Consolidating {len(api_specs)} API specifications...")
        
        # Use OpenAI to consolidate the specifications
        system_prompt = """
        You are an expert API analyst. Consolidate multiple API specifications into one comprehensive specification.
        
        Merge the information intelligently, resolving conflicts and providing the most accurate and complete information.
        
        IMPORTANT: Return only valid JSON. Do not include any text before or after the JSON object.
        Ensure all JSON syntax is correct and properly formatted.
        """
        
        user_prompt = f"""
        Consolidate these API specifications for {product_name}:
        
        {json.dumps(api_specs, indent=2)}
        
        Return a single consolidated JSON object with the same structure as the input specifications.
        Ensure all information is accurate, complete, and well-organized.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from the response with better error handling
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    consolidated_spec = json.loads(json_match.group())
                    print("✅ Successfully consolidated API specifications")
                    return consolidated_spec
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {str(e)}")
                    print(f"   Raw content: {content[:200]}...")
                    return api_specs[0] if api_specs else {}
            else:
                print("❌ Could not parse consolidated JSON")
                print(f"   Raw content: {content[:200]}...")
                return api_specs[0] if api_specs else {}
                
        except Exception as e:
            print(f"❌ Error consolidating specifications: {str(e)}")
            return api_specs[0] if api_specs else {}
            
    def save_api_spec(self, api_spec: Dict[str, Any], filename: str):
        """Save API specification to a JSON file"""
        
        try:
            with open(filename, 'w') as f:
                json.dump(api_spec, f, indent=2)
            print(f"💾 API specification saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")
            
    def save_to_chromadb(self, api_spec: Dict[str, Any]):
        """Save API specification to ChromaDB"""
        
        try:
            print("💾 Saving to ChromaDB...")
            
            # Import the integration manager
            from api_integration_manager import APIIntegrationManager
            
            # Create manager instance and add to ChromaDB
            manager = APIIntegrationManager()
            success = manager.add_api_to_chromadb(api_spec)
            
            if success:
                print("✅ Successfully saved to ChromaDB")
            else:
                print("❌ Failed to save to ChromaDB")
                
        except Exception as e:
            print(f"❌ Error saving to ChromaDB: {str(e)}")
            
    def search_existing_apis(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search through existing APIs in our dataset"""
        
        print(f"🔍 Searching existing APIs for: {query}")
        
        # Import the existing API dataset
        try:
            from api_dataset import get_comprehensive_api_dataset
            api_docs = get_comprehensive_api_dataset()
            
            # Simple keyword search
            results = []
            query_lower = query.lower()
            
            for api in api_docs:
                score = 0
                
                # Check various fields for matches
                if query_lower in api['api_name'].lower():
                    score += 10
                if query_lower in api['category'].lower():
                    score += 5
                if query_lower in api['description'].lower():
                    score += 3
                if any(query_lower in use_case.lower() for use_case in api['common_use_cases']):
                    score += 2
                    
                if score > 0:
                    results.append({
                        'api_name': api['api_name'],
                        'category': api['category'],
                        'description': api['description'],
                        'relevance_score': score,
                        'pricing': api.get('pricing', 'N/A'),
                        'sdk_languages': api.get('sdk_languages', [])
                    })
                    
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            print(f"✅ Found {len(results[:limit])} relevant existing APIs")
            return results[:limit]
            
        except Exception as e:
            print(f"❌ Error searching existing APIs: {str(e)}")
            return []

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="🚀 CatalystAI API Onboard Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_onboard_agent.py onboard "Stripe API"                    # Onboard Stripe API
  python api_onboard_agent.py onboard "Google Maps API" --output-file maps_api.json  # Save to file
  python api_onboard_agent.py onboard "Google AdSense API" --save-to-chromadb  # Save to ChromaDB
  python api_onboard_agent.py search "payment processing" --limit 3   # Search existing APIs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Onboard command
    onboard_parser = subparsers.add_parser('onboard', help='Onboard a new API')
    onboard_parser.add_argument('product_name', help='Name of the product/API to onboard')
    onboard_parser.add_argument('--output-file', help='Save API spec to file (optional)')
    onboard_parser.add_argument('--save-to-chromadb', action='store_true', help='Save API spec to ChromaDB (optional)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search existing APIs')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=5, help='Number of results (default: 5)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    # Initialize the agent
    agent = APIOnboardAgent()
    
    try:
        if args.command == 'onboard':
            print(f"🚀 Starting API onboarding for: {args.product_name}")
            api_spec = agent.onboard_api(args.product_name, args.output_file, args.save_to_chromadb)
            
            if api_spec:
                print("\n" + "="*60)
                print("📋 **ONBOARDED API SPECIFICATION**")
                print("="*60)
                print(json.dumps(api_spec, indent=2))
            else:
                print("❌ Failed to onboard API")
                
        elif args.command == 'search':
            print(f"🔍 Searching existing APIs for: {args.query}")
            results = agent.search_existing_apis(args.query, args.limit)
            
            if results:
                print("\n" + "="*60)
                print("📋 **SEARCH RESULTS**")
                print("="*60)
                
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['api_name']} ({result['category']})")
                    print(f"   Relevance: {result['relevance_score']}")
                    print(f"   Description: {result['description'][:100]}...")
                    print(f"   Pricing: {result['pricing']}")
                    print(f"   SDK Languages: {', '.join(result['sdk_languages'])}")
                    print()
            else:
                print("❌ No relevant APIs found")
                
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
