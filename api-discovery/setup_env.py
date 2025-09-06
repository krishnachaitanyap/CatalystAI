#!/usr/bin/env python3
"""
🔧 CatalystAI Environment Setup Script

This script helps users set up their environment configuration for the API discovery system.
It creates the .env file from the template and guides users through the setup process.

Usage:
    python setup_env.py
    python setup_env.py --interactive
    python setup_env.py --check
"""

import os
import sys
import shutil
from pathlib import Path

def check_environment():
    """Check if .env file exists and validate configuration"""
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
        
    print("✅ .env file exists")
    
    # Check for required variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    with open(env_file, 'r') as f:
        content = f.read()
        
    for var in required_vars:
        if f'{var}=your_' in content or f'{var}=' not in content:
            missing_vars.append(var)
            
    if missing_vars:
        print(f"⚠️ Missing or not configured: {', '.join(missing_vars)}")
        return False
        
    print("✅ All required variables are configured")
    return True

def create_env_file():
    """Create .env file from template"""
    
    template_file = Path('env.template')
    env_file = Path('.env')
    
    if not template_file.exists():
        print("❌ env.template not found")
        return False
        
    if env_file.exists():
        print("⚠️ .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled")
            return False
            
    try:
        shutil.copy(template_file, env_file)
        print("✅ .env file created from template")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def interactive_setup():
    """Interactive setup for environment variables"""
    
    print("🚀 Interactive Environment Setup")
    print("=" * 50)
    
    # Create .env file if it doesn't exist
    if not Path('.env').exists():
        if not create_env_file():
            return False
    
    # Read current .env content
    with open('.env', 'r') as f:
        content = f.read()
    
    # OpenAI API Key
    print("\n🤖 OpenAI Configuration")
    print("-" * 30)
    
    openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    if openai_key:
        content = content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={openai_key}')
    
    # Model settings
    model = input("OpenAI model (gpt-4/gpt-3.5-turbo) [gpt-4]: ").strip() or 'gpt-4'
    content = content.replace('OPENAI_MODEL=gpt-4', f'OPENAI_MODEL={model}')
    
    temperature = input("Temperature (0.0-1.0) [0.3]: ").strip() or '0.3'
    content = content.replace('OPENAI_TEMPERATURE=0.3', f'OPENAI_TEMPERATURE={temperature}')
    
    # ChromaDB settings
    print("\n💾 ChromaDB Configuration")
    print("-" * 30)
    
    persist_dir = input("ChromaDB persistence directory [./chroma_db]: ").strip() or './chroma_db'
    content = content.replace('CHROMA_PERSIST_DIRECTORY=./chroma_db', f'CHROMA_PERSIST_DIRECTORY={persist_dir}')
    
    collection_name = input("Collection name [api_documentation]: ").strip() or 'api_documentation'
    content = content.replace('CHROMA_COLLECTION_NAME=api_documentation', f'CHROMA_COLLECTION_NAME={collection_name}')
    
    # Search settings
    print("\n🔍 Search Configuration")
    print("-" * 30)
    
    top_k = input("Number of search results [5]: ").strip() or '5'
    content = content.replace('TOP_K_RESULTS=5', f'TOP_K_RESULTS={top_k}')
    
    # Optional API keys
    print("\n🔗 Optional API Keys (Press Enter to skip)")
    print("-" * 40)
    
    google_key = input("Google Search API key: ").strip()
    if google_key:
        content = content.replace('GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here', f'GOOGLE_SEARCH_API_KEY={google_key}')
    
    github_token = input("GitHub API token: ").strip()
    if github_token:
        content = content.replace('GITHUB_API_TOKEN=your_github_token_here', f'GITHUB_API_TOKEN={github_token}')
    
    # Environment
    print("\n🌍 Environment Settings")
    print("-" * 30)
    
    env = input("Environment (development/staging/production) [development]: ").strip() or 'development'
    content = content.replace('ENVIRONMENT=development', f'ENVIRONMENT={env}')
    
    debug = input("Enable debug mode (true/false) [true]: ").strip() or 'true'
    content = content.replace('DEBUG_MODE=true', f'DEBUG_MODE={debug}')
    
    # Custom Service Configuration (Example)
    print("\n🎯 Custom Service Configuration (Press Enter to skip)")
    print("-" * 45)
    
    custom_enabled = input("Enable custom service (true/false) [false]: ").strip() or 'false'
    content = content.replace('CUSTOM_SERVICE_ENABLED=false', f'CUSTOM_SERVICE_ENABLED={custom_enabled}')
    
    if custom_enabled.lower() == 'true':
        custom_key = input("Custom service API key: ").strip()
        if custom_key:
            content = content.replace('CUSTOM_SERVICE_API_KEY=your_custom_service_api_key_here', f'CUSTOM_SERVICE_API_KEY={custom_key}')
        
        custom_endpoint = input("Custom service endpoint [https://api.customservice.com]: ").strip() or 'https://api.customservice.com'
        content = content.replace('CUSTOM_SERVICE_ENDPOINT=https://api.customservice.com', f'CUSTOM_SERVICE_ENDPOINT={custom_endpoint}')
        
        custom_timeout = input("Custom service timeout [30]: ").strip() or '30'
        content = content.replace('CUSTOM_SERVICE_TIMEOUT=30', f'CUSTOM_SERVICE_TIMEOUT={custom_timeout}')
    
    # Save updated content
    with open('.env', 'w') as f:
        f.write(content)
    
    print("\n✅ Environment configuration updated!")
    print("\n📝 Next steps:")
    print("1. Review your .env file")
    print("2. Test the configuration: python setup_env.py --check")
    print("3. Start using the API discovery system")
    
    return True

def main():
    """Main function"""
    
    parser = argparse.ArgumentParser(
        description="🔧 CatalystAI Environment Setup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_env.py                    # Interactive setup
  python setup_env.py --check            # Check current configuration
  python setup_env.py --create           # Create .env from template only
        """
    )
    
    parser.add_argument('--interactive', action='store_true', 
                       help='Run interactive setup (default)')
    parser.add_argument('--check', action='store_true',
                       help='Check current environment configuration')
    parser.add_argument('--create', action='store_true',
                       help='Create .env file from template only')
    
    args = parser.parse_args()
    
    # Default to interactive if no flags provided
    if not any([args.interactive, args.check, args.create]):
        args.interactive = True
    
    try:
        if args.check:
            print("🔍 Checking environment configuration...")
            if check_environment():
                print("\n✅ Environment is properly configured!")
                sys.exit(0)
            else:
                print("\n❌ Environment needs configuration")
                print("Run: python setup_env.py --interactive")
                sys.exit(1)
                
        elif args.create:
            print("📄 Creating .env file from template...")
            if create_env_file():
                print("\n✅ .env file created!")
                print("Edit the file to add your API keys")
                sys.exit(0)
            else:
                print("\n❌ Failed to create .env file")
                sys.exit(1)
                
        elif args.interactive:
            interactive_setup()
            
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    main()
