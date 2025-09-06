#!/usr/bin/env python3
"""
🎯 Example: Using Custom Service Configuration

This example shows how to use the new custom service environment properties
in your actual code.
"""

import requests
import time
from typing import Optional, Dict, Any
from env_config import get_custom_service_config, is_custom_service_enabled

class CustomServiceClient:
    """Example client for the custom service"""
    
    def __init__(self):
        self.config = get_custom_service_config()
        
        if not self.config['enabled']:
            raise ValueError("Custom service is not enabled in environment configuration")
            
        if not self.config['api_key']:
            raise ValueError("Custom service API key is not configured")
    
    def make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to the custom service with retry logic"""
        
        headers = {
            'Authorization': f'Bearer {self.config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.config['endpoint']}/{endpoint}"
        
        for attempt in range(self.config['retry_attempts']):
            try:
                response = requests.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.config['timeout']
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Request failed with status {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"Request timeout on attempt {attempt + 1}")
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.config['retry_attempts'] - 1:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        return None

def example_usage():
    """Example of how to use the custom service"""
    
    print("🎯 Custom Service Example")
    print("=" * 40)
    
    # Check if custom service is enabled
    if not is_custom_service_enabled():
        print("❌ Custom service is not enabled")
        print("To enable it, set CUSTOM_SERVICE_ENABLED=true in your .env file")
        return
    
    # Get configuration
    config = get_custom_service_config()
    print(f"✅ Custom service is enabled")
    print(f"   Endpoint: {config['endpoint']}")
    print(f"   Timeout: {config['timeout']}s")
    print(f"   Retry Attempts: {config['retry_attempts']}")
    
    try:
        # Create client
        client = CustomServiceClient()
        
        # Example request
        data = {
            "query": "payment processing API",
            "filters": {
                "category": "payment",
                "max_results": 5
            }
        }
        
        print(f"\n📡 Making request to custom service...")
        result = client.make_request("search", data)
        
        if result:
            print("✅ Request successful!")
            print(f"   Results: {len(result.get('results', []))} items found")
        else:
            print("❌ Request failed after all retry attempts")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def example_with_conditional_usage():
    """Example showing conditional usage based on environment configuration"""
    
    print("\n🔄 Conditional Usage Example")
    print("=" * 40)
    
    # Check if custom service is available
    if is_custom_service_enabled():
        print("✅ Using custom service for enhanced functionality")
        # Use custom service
        config = get_custom_service_config()
        print(f"   Service endpoint: {config['endpoint']}")
    else:
        print("ℹ️ Custom service not available, using fallback")
        # Use fallback/default implementation
        print("   Using default search functionality")

if __name__ == "__main__":
    example_usage()
    example_with_conditional_usage()
