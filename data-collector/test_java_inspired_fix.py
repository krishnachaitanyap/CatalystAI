#!/usr/bin/env python3
"""
Test script to verify Java-inspired circular reference detection and cross-namespace inheritance
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from connectors.api_connector import WSDLConnector

def test_java_inspired_fix():
    """Test the Java-inspired fix for cross-namespace inheritance"""
    
    # Initialize the connector
    connector = WSDLConnector()
    
    # Test with the sample WSDL files
    wsdl_file = "wsdl/ListAccountDetailSvc_20090801.wsdl"
    xsd_files = [
        "wsdl/jisi-2007.xsd",
        "wsdl/account-detail.xsd"
    ]
    
    all_files = [wsdl_file] + xsd_files
    
    try:
        print("🧪 Testing Java-inspired cross-namespace inheritance fix...")
        print(f"📄 Files: {all_files}")
        
        # Parse WSDL files with dependencies
        common_spec = connector.parse_wsdl_files_with_dependencies(all_files)
        
        print(f"✅ Successfully parsed WSDL!")
        print(f"📋 API Name: {common_spec.api_name}")
        print(f"📋 Endpoints: {len(common_spec.endpoints)}")
        
        # Check the first endpoint's response
        if common_spec.endpoints:
            endpoint = common_spec.endpoints[0]
            print(f"\n🔍 Endpoint: {endpoint.get('path', 'N/A')}")
            
            # Check response structure
            responses = endpoint.get('responses', {})
            if '200' in responses:
                response_200 = responses['200']
                print(f"\n📋 Response 200 structure:")
                print(f"   - Description: {response_200.get('description', 'N/A')}")
                print(f"   - Content type: {response_200.get('content_type', 'N/A')}")
                print(f"   - Parts: {len(response_200.get('parts', []))}")
                
                # Check parts for external XSD types
                parts = response_200.get('parts', [])
                for i, part in enumerate(parts):
                    print(f"\n   Part {i+1}: {part.get('name', 'N/A')}")
                    print(f"   - Element: {part.get('element', 'N/A')}")
                    print(f"   - Type: {part.get('type', 'N/A')}")
                    
                    # Check schema details
                    schema_details = part.get('schema_details', {})
                    
                    # Check attributes
                    attributes = schema_details.get('attributes', [])
                    print(f"   - Attributes: {len(attributes)}")
                    for attr in attributes[:5]:  # Show first 5 attributes
                        print(f"     * {attr.get('name', 'N/A')}: {attr.get('type', 'N/A')}")
                    
                    # Check nested attributes
                    nested_attributes = schema_details.get('nested_attributes', [])
                    print(f"   - Nested attributes: {len(nested_attributes)}")
                    for nested_attr in nested_attributes[:10]:  # Show first 10 nested attributes
                        print(f"     * {nested_attr.get('name', 'N/A')}: {nested_attr.get('type', 'N/A')}")
                
                # Check all attributes
                all_attributes = response_200.get('all_attributes', [])
                print(f"\n📋 Total all_attributes: {len(all_attributes)}")
                
                # Look for external XSD specific attributes
                external_attrs_found = []
                for attr in all_attributes:
                    attr_name = attr.get('name', '')
                    if any(keyword in attr_name.lower() for keyword in ['abe', 'dda', 'accountid', 'accountname', 'accountnumber']):
                        external_attrs_found.append(attr_name)
                
                if external_attrs_found:
                    print(f"✅ Found external XSD attributes in response: {external_attrs_found}")
                    print("🎉 SUCCESS: Java-inspired fix is working!")
                else:
                    print(f"❌ No external XSD attributes found in response")
                    print(f"   Available attribute names: {[attr.get('name', '') for attr in all_attributes[:10]]}")
            
        else:
            print("❌ No endpoints found")
            
    except Exception as e:
        print(f"❌ Error testing Java-inspired fix: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_java_inspired_fix()
