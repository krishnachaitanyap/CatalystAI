#!/usr/bin/env python3
"""
🔗 CatalystAI API Integration Manager

This script integrates onboarded APIs into the ChromaDB database for use with 
the API discovery system.

Usage:
    python api_integration_manager.py --help
    python api_integration_manager.py add api_spec.json
    python api_integration_manager.py add-multiple api_specs_folder/
    python api_integration_manager.py list
    python api_integration_manager.py remove "API Name"
"""

import os
import json
import argparse
import sys
from typing import List, Dict, Any
from datetime import datetime

# ChromaDB integration
import chromadb
from chromadb.config import Settings

# Utilities
from dotenv import load_dotenv

class APIIntegrationManager:
    """Manager for integrating APIs into the ChromaDB database"""
    
    def __init__(self):
        """Initialize the API Integration Manager"""
        self.load_environment()
        self.initialize_chromadb()
        self.collection_name = "api_documentation"
        
    def load_environment(self):
        """Load environment variables"""
        load_dotenv()
        print("✅ Environment loaded successfully")
        
    def initialize_chromadb(self):
        """Initialize ChromaDB client"""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db"
            )
            print("✅ ChromaDB initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {str(e)}")
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
            
    def add_api_to_chromadb(self, api_spec: Dict[str, Any]) -> bool:
        """Add a single API specification to ChromaDB"""
        
        try:
            collection = self.get_or_create_collection()
            
            # Create comprehensive text representation
            doc_text = f"""
API: {api_spec['api_name']}
Category: {api_spec['category']}
Description: {api_spec['description']}
Endpoints: {', '.join(api_spec.get('endpoints', []))}
Authentication: {api_spec.get('authentication', 'N/A')}
Rate Limits: {api_spec.get('rate_limits', 'N/A')}
Pricing: {api_spec.get('pricing', 'N/A')}
Integration Steps: {' '.join(api_spec.get('integration_steps', []))}
Best Practices: {' '.join(api_spec.get('best_practices', []))}
Use Cases: {' '.join(api_spec.get('common_use_cases', []))}
SDK Languages: {', '.join(api_spec.get('sdk_languages', []))}
Documentation: {api_spec.get('documentation_url', 'N/A')}
""".strip()
            
            # Convert complex data structures to strings for ChromaDB metadata
            metadata = {
                'api_name': api_spec['api_name'],
                'category': api_spec['category'],
                'description': api_spec['description'],
                'endpoints': ', '.join(api_spec.get('endpoints', [])),
                'authentication': api_spec.get('authentication', 'N/A'),
                'rate_limits': api_spec.get('rate_limits', 'N/A'),
                'pricing': api_spec.get('pricing', 'N/A'),
                'integration_steps': ', '.join(api_spec.get('integration_steps', [])),
                'best_practices': ', '.join(api_spec.get('best_practices', [])),
                'common_use_cases': ', '.join(api_spec.get('common_use_cases', [])),
                'sdk_languages': ', '.join(api_spec.get('sdk_languages', [])),
                'documentation_url': api_spec.get('documentation_url', 'N/A'),
                'added_date': datetime.now().isoformat(),
                'source': 'onboarded'
            }
            
            # Generate unique ID
            api_id = f"api_{api_spec['api_name'].lower().replace(' ', '_').replace('-', '_')}_{int(datetime.now().timestamp())}"
            
            # Add to ChromaDB
            collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[api_id]
            )
            
            print(f"✅ Successfully added {api_spec['api_name']} to ChromaDB")
            return True
            
        except Exception as e:
            print(f"❌ Error adding API to ChromaDB: {str(e)}")
            return False
            
    def load_api_spec_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load API specification from JSON file"""
        
        try:
            with open(filepath, 'r') as f:
                api_spec = json.load(f)
                
            # Validate required fields
            required_fields = ['api_name', 'category', 'description']
            for field in required_fields:
                if field not in api_spec:
                    raise ValueError(f"Missing required field: {field}")
                    
            print(f"✅ Loaded API specification from: {filepath}")
            return api_spec
            
        except Exception as e:
            print(f"❌ Error loading API spec from {filepath}: {str(e)}")
            return {}
            
    def add_api_from_file(self, filepath: str) -> bool:
        """Add API specification from file to ChromaDB"""
        
        api_spec = self.load_api_spec_from_file(filepath)
        if not api_spec:
            return False
            
        return self.add_api_to_chromadb(api_spec)
        
    def add_multiple_apis_from_folder(self, folder_path: str) -> int:
        """Add multiple API specifications from a folder"""
        
        if not os.path.exists(folder_path):
            print(f"❌ Folder does not exist: {folder_path}")
            return 0
            
        success_count = 0
        total_count = 0
        
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                filepath = os.path.join(folder_path, filename)
                print(f"\n📄 Processing: {filename}")
                
                if self.add_api_from_file(filepath):
                    success_count += 1
                total_count += 1
                
        print(f"\n📊 Summary: {success_count}/{total_count} APIs successfully added")
        return success_count
        
    def list_apis_in_chromadb(self):
        """List all APIs currently in ChromaDB"""
        
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            count = collection.count()
            
            if count == 0:
                print("📭 No APIs found in ChromaDB database")
                return
                
            print(f"📚 Found {count} APIs in ChromaDB database:")
            print("=" * 80)
            
            # Get all documents to display
            results = collection.get()
            
            for i, (id, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
                source = metadata.get('source', 'unknown')
                added_date = metadata.get('added_date', 'unknown')
                
                print(f"{i+1:2d}. {metadata['api_name']}")
                print(f"     Category: {metadata['category']}")
                print(f"     Description: {metadata['description'][:100]}...")
                print(f"     Pricing: {metadata.get('pricing', 'N/A')}")
                print(f"     Source: {source}")
                print(f"     Added: {added_date}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing APIs: {str(e)}")
            
    def remove_api_from_chromadb(self, api_name: str) -> bool:
        """Remove an API from ChromaDB by name"""
        
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            
            # Get all documents
            results = collection.get()
            
            # Find the API to remove
            api_id_to_remove = None
            for id, metadata in zip(results['ids'], results['metadatas']):
                if metadata['api_name'].lower() == api_name.lower():
                    api_id_to_remove = id
                    break
                    
            if api_id_to_remove:
                collection.delete(ids=[api_id_to_remove])
                print(f"✅ Successfully removed {api_name} from ChromaDB")
                return True
            else:
                print(f"❌ API '{api_name}' not found in ChromaDB")
                return False
                
        except Exception as e:
            print(f"❌ Error removing API: {str(e)}")
            return False
            
    def get_database_stats(self):
        """Get statistics about the ChromaDB database"""
        
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            count = collection.count()
            
            if count == 0:
                print("📭 Database is empty")
                return
                
            # Get all documents for analysis
            results = collection.get()
            
            # Analyze categories
            categories = {}
            sources = {}
            
            for metadata in results['metadatas']:
                category = metadata.get('category', 'Unknown')
                source = metadata.get('source', 'unknown')
                
                categories[category] = categories.get(category, 0) + 1
                sources[source] = sources.get(source, 0) + 1
                
            print(f"📊 ChromaDB Database Statistics")
            print("=" * 50)
            print(f"Total APIs: {count}")
            print(f"Categories: {len(categories)}")
            print(f"Sources: {len(sources)}")
            print()
            
            print("📋 Categories:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {category}: {count} APIs")
                
            print("\n📋 Sources:")
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {source}: {count} APIs")
                
        except Exception as e:
            print(f"❌ Error getting database stats: {str(e)}")

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="🔗 CatalystAI API Integration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_integration_manager.py add api_spec.json              # Add single API
  python api_integration_manager.py add-multiple api_specs/       # Add multiple APIs
  python api_integration_manager.py list                          # List all APIs
  python api_integration_manager.py stats                         # Database statistics
  python api_integration_manager.py remove "Stripe API"           # Remove API
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add API from JSON file')
    add_parser.add_argument('filepath', help='Path to API specification JSON file')
    
    # Add multiple command
    add_multiple_parser = subparsers.add_parser('add-multiple', help='Add multiple APIs from folder')
    add_multiple_parser.add_argument('folder_path', help='Path to folder containing JSON files')
    
    # List command
    subparsers.add_parser('list', help='List all APIs in ChromaDB')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove API from ChromaDB')
    remove_parser.add_argument('api_name', help='Name of the API to remove')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    # Initialize the manager
    manager = APIIntegrationManager()
    
    try:
        if args.command == 'add':
            print(f"📄 Adding API from file: {args.filepath}")
            success = manager.add_api_from_file(args.filepath)
            if success:
                print("✅ API successfully added to ChromaDB")
            else:
                print("❌ Failed to add API")
                
        elif args.command == 'add-multiple':
            print(f"📁 Adding multiple APIs from folder: {args.folder_path}")
            count = manager.add_multiple_apis_from_folder(args.folder_path)
            print(f"✅ Added {count} APIs to ChromaDB")
            
        elif args.command == 'list':
            manager.list_apis_in_chromadb()
            
        elif args.command == 'stats':
            manager.get_database_stats()
            
        elif args.command == 'remove':
            print(f"🗑️ Removing API: {args.api_name}")
            success = manager.remove_api_from_chromadb(args.api_name)
            if not success:
                print("❌ Failed to remove API")
                
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
