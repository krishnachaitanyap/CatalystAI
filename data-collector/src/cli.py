#!/usr/bin/env python3
"""
Data Collector CLI

Command-line interface for the Data Collector tool.
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connectors.api_connector import APIConnectorManager

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🔗 Data Collector - Convert API specifications to common structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  data-collector convert samples/sample_swagger.json                    # Convert Swagger file
  data-collector convert samples/sample_wsdl.xml --type wsdl          # Convert WSDL file
  data-collector convert-url https://api.example.com/swagger.json      # Convert from URL
  data-collector list                                                  # List stored APIs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert API specification file')
    convert_parser.add_argument('file_path', help='Path to API specification file')
    convert_parser.add_argument('--type', choices=['swagger', 'wsdl', 'auto'], default='auto',
                               help='API specification type (default: auto-detect)')
    convert_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Print detailed converted data to console')
    
    # Convert URL command
    convert_url_parser = subparsers.add_parser('convert-url', help='Convert API specification from URL')
    convert_url_parser.add_argument('url', help='URL to API specification')
    convert_url_parser.add_argument('--type', choices=['swagger', 'wsdl', 'auto'], default='auto',
                                   help='API specification type (default: auto-detect)')
    convert_url_parser.add_argument('--verbose', '-v', action='store_true',
                                   help='Print detailed converted data to console')
    
    # List command
    subparsers.add_parser('list', help='List all stored API specifications')
    
    # Info command
    subparsers.add_parser('info', help='Show project information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'info':
        show_info()
        return
    
    # Initialize the connector manager
    manager = APIConnectorManager()
    manager.load_environment()
    manager.initialize_chromadb()
    
    try:
        if args.command == 'convert':
            print(f"🔄 Converting API specification: {args.file_path}")
            success = manager.convert_and_store(args.file_path, args.type, args.verbose)
            if success:
                if not args.verbose:
                    print("✅ API specification successfully converted and stored")
            else:
                print("❌ Failed to convert API specification")
                
        elif args.command == 'convert-url':
            print(f"🔄 Converting API specification from URL: {args.url}")
            success = manager.convert_from_url(args.url, args.type, args.verbose)
            if success:
                if not args.verbose:
                    print("✅ API specification successfully converted and stored")
            else:
                print("❌ Failed to convert API specification")
                
        elif args.command == 'list':
            manager.list_stored_apis()
            
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

def show_info():
    """Show project information"""
    print("🔗 Data Collector")
    print("=" * 50)
    print("Version: 1.0.0")
    print("Author: CatalystAI Team")
    print("Description: API Specification Processing and Conversion Tool")
    print()
    print("Supported Formats:")
    print("• Swagger/OpenAPI 2.0 & 3.0 (JSON, YAML)")
    print("• WSDL 1.1 & 2.0 (XML)")
    print("• GraphQL Schema (Coming soon)")
    print("• AsyncAPI (Coming soon)")
    print("• RAML (Coming soon)")
    print()
    print("Features:")
    print("• Automatic format detection")
    print("• Common structure conversion")
    print("• ChromaDB integration")
    print("• Intelligent categorization")
    print("• Integration guidelines")
    print("• Best practices generation")

if __name__ == "__main__":
    main()
