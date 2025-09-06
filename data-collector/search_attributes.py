#!/usr/bin/env python3
"""
Search script to find specific attributes in API request/response bodies
"""

import json
import sys
from typing import List, Dict, Any
import chromadb
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class AttributeSearcher:
    """Search for specific attributes in API specifications"""
    
    def __init__(self):
        """Initialize ChromaDB client"""
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("api_specifications")
    
    def search_attribute_in_request_body(self, attribute_name: str) -> List[Dict[str, Any]]:
        """Search for a specific attribute in request bodies"""
        
        # Search for the attribute name in the searchable content
        results = self.collection.query(
            query_texts=[f"request body contains {attribute_name}"],
            n_results=10
        )
        
        matches = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            # Parse the stored API specification
            try:
                api_spec = json.loads(doc)
                
                # Check each endpoint for the attribute in request body
                for endpoint in api_spec.get('endpoints', []):
                    request_body = endpoint.get('request_body', {})
                    
                    # Check if attribute exists in all_attributes
                    all_attributes = request_body.get('all_attributes', [])
                    for attr in all_attributes:
                        if attribute_name.lower() in attr.get('name', '').lower():
                            matches.append({
                                'api_name': api_spec.get('api_name', ''),
                                'endpoint': endpoint.get('path', ''),
                                'method': endpoint.get('method', ''),
                                'attribute': attr,
                                'relevance_score': 1 - distance,
                                'searchable_content': request_body.get('searchable_content', '')
                            })
                    
                    # Also check individual parts
                    for part in request_body.get('parts', []):
                        for attr in part.get('attributes', []):
                            if attribute_name.lower() in attr.get('name', '').lower():
                                matches.append({
                                    'api_name': api_spec.get('api_name', ''),
                                    'endpoint': endpoint.get('path', ''),
                                    'method': endpoint.get('method', ''),
                                    'attribute': attr,
                                    'relevance_score': 1 - distance,
                                    'searchable_content': part.get('searchable_content', '')
                                })
            
            except json.JSONDecodeError:
                continue
        
        return matches
    
    def search_attribute_in_response_body(self, attribute_name: str) -> List[Dict[str, Any]]:
        """Search for a specific attribute in response bodies"""
        
        # Search for the attribute name in the searchable content
        results = self.collection.query(
            query_texts=[f"response body contains {attribute_name}"],
            n_results=10
        )
        
        matches = []
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            distance = results['distances'][0][i]
            
            # Parse the stored API specification
            try:
                api_spec = json.loads(doc)
                
                # Check each endpoint for the attribute in responses
                for endpoint in api_spec.get('endpoints', []):
                    responses = endpoint.get('responses', {})
                    
                    for status_code, response in responses.items():
                        # Check if attribute exists in all_attributes
                        all_attributes = response.get('all_attributes', [])
                        for attr in all_attributes:
                            if attribute_name.lower() in attr.get('name', '').lower():
                                matches.append({
                                    'api_name': api_spec.get('api_name', ''),
                                    'endpoint': endpoint.get('path', ''),
                                    'method': endpoint.get('method', ''),
                                    'status_code': status_code,
                                    'attribute': attr,
                                    'relevance_score': 1 - distance,
                                    'searchable_content': response.get('searchable_content', '')
                                })
                        
                        # Also check individual parts
                        for part in response.get('parts', []):
                            for attr in part.get('attributes', []):
                                if attribute_name.lower() in attr.get('name', '').lower():
                                    matches.append({
                                        'api_name': api_spec.get('api_name', ''),
                                        'endpoint': endpoint.get('path', ''),
                                        'method': endpoint.get('method', ''),
                                        'status_code': status_code,
                                        'attribute': attr,
                                        'relevance_score': 1 - distance,
                                        'searchable_content': part.get('searchable_content', '')
                                    })
            
            except json.JSONDecodeError:
                continue
        
        return matches
    
    def search_attribute_anywhere(self, attribute_name: str) -> List[Dict[str, Any]]:
        """Search for a specific attribute anywhere in the API specification"""
        
        # Get all documents and search through them directly
        all_docs = self.collection.get()
        
        matches = []
        for i, doc in enumerate(all_docs['documents']):
            metadata = all_docs['metadatas'][i]
            
            # Parse the stored API specification
            try:
                api_spec = json.loads(doc)
                
                # Check each endpoint
                for endpoint in api_spec.get('endpoints', []):
                    # Check parameters
                    for param in endpoint.get('parameters', []):
                        for attr in param.get('attributes', []):
                            if attribute_name.lower() in attr.get('name', '').lower():
                                matches.append({
                                    'api_name': api_spec.get('api_name', ''),
                                    'endpoint': endpoint.get('path', ''),
                                    'method': endpoint.get('method', ''),
                                    'location': 'parameter',
                                    'attribute': attr,
                                    'relevance_score': 1.0  # Exact match
                                })
                    
                    # Check request body
                    request_body = endpoint.get('request_body', {})
                    for attr in request_body.get('all_attributes', []):
                        if attribute_name.lower() in attr.get('name', '').lower():
                            matches.append({
                                'api_name': api_spec.get('api_name', ''),
                                'endpoint': endpoint.get('path', ''),
                                'method': endpoint.get('method', ''),
                                'location': 'request_body',
                                'attribute': attr,
                                'relevance_score': 1.0  # Exact match
                            })
                    
                    # Check responses
                    responses = endpoint.get('responses', {})
                    for status_code, response in responses.items():
                        for attr in response.get('all_attributes', []):
                            if attribute_name.lower() in attr.get('name', '').lower():
                                matches.append({
                                    'api_name': api_spec.get('api_name', ''),
                                    'endpoint': endpoint.get('path', ''),
                                    'method': endpoint.get('method', ''),
                                    'status_code': status_code,
                                    'location': 'response_body',
                                    'attribute': attr,
                                    'relevance_score': 1.0  # Exact match
                                })
            
            except json.JSONDecodeError:
                continue
        
        return matches

def main():
    """Main function to demonstrate attribute searching"""
    
    if len(sys.argv) < 2:
        print("Usage: python search_attributes.py <attribute_name> [location]")
        print("Locations: request, response, anywhere (default: anywhere)")
        sys.exit(1)
    
    attribute_name = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else "anywhere"
    
    searcher = AttributeSearcher()
    
    print(f"🔍 Searching for attribute '{attribute_name}' in {location}...")
    print("=" * 80)
    
    if location == "request":
        matches = searcher.search_attribute_in_request_body(attribute_name)
    elif location == "response":
        matches = searcher.search_attribute_in_response_body(attribute_name)
    else:
        matches = searcher.search_attribute_anywhere(attribute_name)
    
    if not matches:
        print(f"❌ No matches found for attribute '{attribute_name}' in {location}")
        return
    
    print(f"✅ Found {len(matches)} matches:")
    print()
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. **{match['api_name']}**")
        print(f"   Endpoint: {match['method']} {match['endpoint']}")
        
        if 'status_code' in match:
            print(f"   Status Code: {match['status_code']}")
        
        if 'location' in match:
            print(f"   Location: {match['location']}")
        
        attr = match['attribute']
        print(f"   Attribute: {attr['name']}")
        print(f"   Type: {attr['type']}")
        print(f"   Required: {attr['min_occurs'] != '0'}")
        print(f"   Relevance Score: {match['relevance_score']:.3f}")
        
        if 'searchable_content' in match:
            print(f"   Searchable Content: {match['searchable_content'][:100]}...")
        
        print()

if __name__ == "__main__":
    main()
