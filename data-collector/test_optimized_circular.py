#!/usr/bin/env python3
"""
Quick test script for optimized circular dependency handling
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from soap_converter import SOAPConverter

def create_simple_circular_test_files(test_dir: Path):
    """Create simple test files with circular dependencies"""
    
    # Create the directory if it doesn't exist
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple WSDL with circular dependencies
    wsdl_content = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://example.com/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="http://example.com/">
    <types>
        <xsd:schema targetNamespace="http://example.com/">
            <xsd:element name="UserRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="user" type="tns:User"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <xsd:complexType name="User">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:int"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="profile" type="tns:Profile"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="Profile">
                <xsd:sequence>
                    <xsd:element name="userId" type="xsd:int"/>
                    <xsd:element name="user" type="tns:User"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
    </types>
    <message name="UserRequestMessage">
        <part name="parameters" element="tns:UserRequest"/>
    </message>
    <portType name="UserServicePortType">
        <operation name="GetUser">
            <input message="tns:UserRequestMessage"/>
        </operation>
    </portType>
    <binding name="UserServiceBinding" type="tns:UserServicePortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="GetUser">
            <soap:operation soapAction="http://example.com/GetUser"/>
            <input>
                <soap:body use="literal"/>
            </input>
        </operation>
    </binding>
    <service name="UserService">
        <port name="UserServicePort" binding="tns:UserServiceBinding">
            <soap:address location="http://example.com/UserService"/>
        </port>
    </service>
</definitions>'''
    
    # Write test file
    (test_dir / "user-service.wsdl").write_text(wsdl_content)
    
    print(f"📄 Created simple circular dependency test file in {test_dir}")

def test_optimized_circular_handling():
    """Test optimized circular dependency handling"""
    
    print("🧪 Testing Optimized Circular Dependency Handling")
    print("=" * 60)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files
        create_simple_circular_test_files(input_dir)
        
        # Test with timeout
        print("\n🔧 Testing optimized circular dependency resolution...")
        converter = SOAPConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            chunking_strategy="ENDPOINT_BASED"
        )
        
        try:
            import time
            start_time = time.time()
            
            converter.process_all_files()
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"⏱️ Processing completed in {processing_time:.2f} seconds")
            
            # Check results
            output_files = list(output_dir.glob("*.json"))
            print(f"✅ Generated {len(output_files)} JSON files")
            
            for file_path in output_files:
                print(f"   - {file_path.name}")
                
                # Check if the JSON contains type information
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Look for type information
                has_types = False
                for endpoint in data.get('endpoints', []):
                    if endpoint.get('parameters'):
                        has_types = True
                        break
                
                if has_types:
                    print(f"   ✅ Types detected and processed in {file_path.name}")
                else:
                    print(f"   ℹ️ No types detected in {file_path.name}")
            
            print(f"\n✅ Optimized circular dependency test completed in {processing_time:.2f} seconds!")
            
        except Exception as e:
            print(f"❌ Error during optimized circular dependency test: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Run the optimized test"""
    print("🔧 Testing Standalone Converter: Optimized Circular Dependencies")
    print("=" * 80)
    
    test_optimized_circular_handling()
    
    print("\n🎉 Optimized test completed!")

if __name__ == "__main__":
    main()
