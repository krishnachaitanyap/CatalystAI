#!/usr/bin/env python3
"""
Test script for the SOAP converter

This script tests various scenarios for the SOAP converter.
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

def create_test_files(test_dir: Path):
    """Create test WSDL and XSD files"""
    
    # Create the directory if it doesn't exist
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test WSDL file
    wsdl_content = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://example.com/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="http://example.com/">
    <types>
        <xsd:schema targetNamespace="http://example.com/">
            <xsd:element name="GetUserRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="userId" type="xsd:string"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
        </xsd:schema>
    </types>
    <message name="GetUserRequestMessage">
        <part name="parameters" element="tns:GetUserRequest"/>
    </message>
    <portType name="UserServicePortType">
        <operation name="GetUser">
            <input message="tns:GetUserRequestMessage"/>
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
    
    # Test XSD file
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="http://example.com/types"
             xmlns:tns="http://example.com/types">
    <xsd:complexType name="UserType">
        <xsd:sequence>
            <xsd:element name="id" type="xsd:int"/>
            <xsd:element name="name" type="xsd:string"/>
            <xsd:element name="email" type="xsd:string"/>
        </xsd:sequence>
    </xsd:complexType>
</xsd:schema>'''
    
    # Write test files
    (test_dir / "user-service.wsdl").write_text(wsdl_content)
    (test_dir / "user-types.xsd").write_text(xsd_content)
    
    print(f"📄 Created test files in {test_dir}")

def test_converter():
    """Test the SOAP converter with various scenarios"""
    
    print("🧪 Testing SOAP Converter")
    print("=" * 40)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files
        create_test_files(input_dir)
        
        # Test 1: Basic conversion
        print("\n🔧 Test 1: Basic WSDL + XSD conversion")
        converter = SOAPConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            chunking_strategy="ENDPOINT_BASED"
        )
        
        converter.process_all_files()
        
        # Check results
        output_files = list(output_dir.glob("*.json"))
        print(f"✅ Generated {len(output_files)} JSON files")
        
        for file_path in output_files:
            print(f"   - {file_path.name}")
        
        # Test 2: Different chunking strategies
        print("\n🔧 Test 2: Different chunking strategies")
        strategies = ["FIXED_SIZE", "SEMANTIC", "HYBRID"]
        
        for strategy in strategies:
            print(f"   Testing {strategy} strategy...")
            converter = SOAPConverter(
                input_dir=str(input_dir),
                output_dir=str(output_dir),
                chunking_strategy=strategy
            )
            
            # Just test initialization, don't process again
            print(f"   ✅ {strategy} strategy initialized")
        
        print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    test_converter()
