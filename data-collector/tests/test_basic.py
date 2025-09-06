#!/usr/bin/env python3
"""
Test script for Data Collector

This script tests the basic functionality of the data collector.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connectors.api_connector import APIConnectorManager

def test_swagger_conversion():
    """Test Swagger file conversion"""
    print("🧪 Testing Swagger conversion...")
    
    manager = APIConnectorManager()
    manager.load_environment()
    manager.initialize_chromadb()
    
    # Test with sample Swagger file
    sample_file = Path(__file__).parent.parent / "samples" / "sample_swagger.json"
    
    if sample_file.exists():
        success = manager.convert_and_store(str(sample_file), "swagger")
        if success:
            print("✅ Swagger conversion test passed")
            return True
        else:
            print("❌ Swagger conversion test failed")
            return False
    else:
        print("⚠️ Sample Swagger file not found")
        return False

def test_wsdl_conversion():
    """Test WSDL file conversion"""
    print("🧪 Testing WSDL conversion...")
    
    manager = APIConnectorManager()
    manager.load_environment()
    manager.initialize_chromadb()
    
    # Test with sample WSDL file
    sample_file = Path(__file__).parent.parent / "samples" / "sample_wsdl.xml"
    
    if sample_file.exists():
        success = manager.convert_and_store(str(sample_file), "wsdl")
        if success:
            print("✅ WSDL conversion test passed")
            return True
        else:
            print("❌ WSDL conversion test failed")
            return False
    else:
        print("⚠️ Sample WSDL file not found")
        return False

def test_list_apis():
    """Test listing stored APIs"""
    print("🧪 Testing API listing...")
    
    manager = APIConnectorManager()
    manager.load_environment()
    manager.initialize_chromadb()
    
    try:
        manager.list_stored_apis()
        print("✅ API listing test passed")
        return True
    except Exception as e:
        print(f"❌ API listing test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Data Collector Tests")
    print("=" * 50)
    
    tests = [
        test_swagger_conversion,
        test_wsdl_conversion,
        test_list_apis,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
        print()
    
    print("📊 Test Results")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
