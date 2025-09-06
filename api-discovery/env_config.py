#!/usr/bin/env python3
"""
🔧 Environment Configuration Helper

This module provides easy access to environment variables with proper typing
and validation. It centralizes all environment configuration for the API discovery system.
"""

import os
from typing import Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnvironmentConfig:
    """Centralized environment configuration with validation"""
    
    @staticmethod
    def get_openai_config() -> dict:
        """Get OpenAI configuration"""
        return {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
            'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.3')),
            'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '2000')),
            'timeout': int(os.getenv('OPENAI_REQUEST_TIMEOUT', '30'))
        }
    
    @staticmethod
    def get_chromadb_config() -> dict:
        """Get ChromaDB configuration"""
        return {
            'persist_directory': os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db'),
            'collection_name': os.getenv('CHROMA_COLLECTION_NAME', 'api_documentation'),
            'distance_function': os.getenv('CHROMA_DISTANCE_FUNCTION', 'cosine')
        }
    
    @staticmethod
    def get_search_config() -> dict:
        """Get search configuration"""
        return {
            'top_k_results': int(os.getenv('TOP_K_RESULTS', '5')),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
            'search_timeout': int(os.getenv('SEARCH_TIMEOUT', '10')),
            'cache_enabled': os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        }
    
    @staticmethod
    def get_web_search_config() -> dict:
        """Get web search configuration"""
        return {
            'timeout': int(os.getenv('WEB_SEARCH_TIMEOUT', '15')),
            'delay': int(os.getenv('WEB_SEARCH_DELAY', '2')),
            'max_retries': int(os.getenv('WEB_SEARCH_MAX_RETRIES', '3')),
            'user_agent': os.getenv('WEB_SEARCH_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        }
    
    @staticmethod
    def get_external_api_keys() -> dict:
        """Get external API keys"""
        return {
            'google_search': os.getenv('GOOGLE_SEARCH_API_KEY'),
            'google_engine_id': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
            'bing_search': os.getenv('BING_SEARCH_API_KEY'),
            'github': os.getenv('GITHUB_API_TOKEN'),
            'rapidapi': os.getenv('RAPIDAPI_KEY')
        }
    
    @staticmethod
    def get_custom_service_config() -> dict:
        """Get custom service configuration"""
        return {
            'enabled': os.getenv('CUSTOM_SERVICE_ENABLED', 'false').lower() == 'true',
            'api_key': os.getenv('CUSTOM_SERVICE_API_KEY'),
            'endpoint': os.getenv('CUSTOM_SERVICE_ENDPOINT', 'https://api.customservice.com'),
            'timeout': int(os.getenv('CUSTOM_SERVICE_TIMEOUT', '30')),
            'retry_attempts': int(os.getenv('CUSTOM_SERVICE_RETRY_ATTEMPTS', '3'))
        }
    
    @staticmethod
    def get_security_config() -> dict:
        """Get security configuration"""
        return {
            'encrypt_api_keys': os.getenv('ENCRYPT_API_KEYS', 'false').lower() == 'true',
            'encryption_password': os.getenv('KEY_ENCRYPTION_PASSWORD'),
            'enable_rate_limiting': os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true',
            'max_requests_per_minute': int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        }
    
    @staticmethod
    def get_performance_config() -> dict:
        """Get performance configuration"""
        return {
            'enable_caching': os.getenv('ENABLE_CACHING', 'true').lower() == 'true',
            'cache_ttl': int(os.getenv('CACHE_TTL', '3600')),
            'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', '5')),
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30'))
        }
    
    @staticmethod
    def get_logging_config() -> dict:
        """Get logging configuration"""
        return {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file': os.getenv('LOG_FILE', './logs/api_discovery.log'),
            'enable_metrics': os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
            'metrics_port': int(os.getenv('METRICS_PORT', '8000'))
        }
    
    @staticmethod
    def get_file_paths() -> dict:
        """Get file path configuration"""
        return {
            'api_specs_dir': os.getenv('API_SPECS_DIR', './api_specs'),
            'export_dir': os.getenv('EXPORT_DIR', './exports'),
            'backup_dir': os.getenv('BACKUP_DIR', './backups'),
            'temp_dir': os.getenv('TEMP_DIR', './temp')
        }
    
    @staticmethod
    def get_environment_config() -> dict:
        """Get environment configuration"""
        return {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug_mode': os.getenv('DEBUG_MODE', 'true').lower() == 'true',
            'enable_telemetry': os.getenv('ENABLE_TELEMETRY', 'false').lower() == 'true',
            'telemetry_endpoint': os.getenv('TELEMETRY_ENDPOINT', 'https://telemetry.example.com')
        }
    
    @staticmethod
    def validate_required_config() -> bool:
        """Validate that required configuration is present"""
        openai_config = EnvironmentConfig.get_openai_config()
        
        if not openai_config['api_key'] or openai_config['api_key'].startswith('your_'):
            print("❌ OPENAI_API_KEY is required and not configured")
            return False
            
        return True
    
    @staticmethod
    def print_config_summary():
        """Print a summary of current configuration"""
        print("🔧 Environment Configuration Summary")
        print("=" * 50)
        
        # Required config
        openai_config = EnvironmentConfig.get_openai_config()
        print(f"🤖 OpenAI: {'✅ Configured' if openai_config['api_key'] and not openai_config['api_key'].startswith('your_') else '❌ Not configured'}")
        
        # Optional configs
        external_keys = EnvironmentConfig.get_external_api_keys()
        configured_keys = [k for k, v in external_keys.items() if v and not str(v).startswith('your_')]
        print(f"🔗 External APIs: {len(configured_keys)} configured")
        
        # Custom service
        custom_config = EnvironmentConfig.get_custom_service_config()
        print(f"🎯 Custom Service: {'✅ Enabled' if custom_config['enabled'] else '❌ Disabled'}")
        
        # Environment
        env_config = EnvironmentConfig.get_environment_config()
        print(f"🌍 Environment: {env_config['environment']}")
        print(f"🐛 Debug Mode: {'✅ Enabled' if env_config['debug_mode'] else '❌ Disabled'}")

# Convenience functions for common use cases
def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key"""
    return EnvironmentConfig.get_openai_config()['api_key']

def get_custom_service_config() -> dict:
    """Get custom service configuration"""
    return EnvironmentConfig.get_custom_service_config()

def is_custom_service_enabled() -> bool:
    """Check if custom service is enabled"""
    return EnvironmentConfig.get_custom_service_config()['enabled']

def get_chromadb_path() -> str:
    """Get ChromaDB persistence directory"""
    return EnvironmentConfig.get_chromadb_config()['persist_directory']

def get_search_results_limit() -> int:
    """Get number of search results to return"""
    return EnvironmentConfig.get_search_config()['top_k_results']

def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return EnvironmentConfig.get_environment_config()['debug_mode']

# Example usage
if __name__ == "__main__":
    EnvironmentConfig.print_config_summary()
    
    # Example of using custom service config
    custom_config = get_custom_service_config()
    if custom_config['enabled']:
        print(f"\n🎯 Custom Service Configuration:")
        print(f"   Endpoint: {custom_config['endpoint']}")
        print(f"   Timeout: {custom_config['timeout']}s")
        print(f"   Retry Attempts: {custom_config['retry_attempts']}")
    else:
        print("\n🎯 Custom Service: Not enabled")
