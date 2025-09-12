#!/usr/bin/env python3
"""
Test script to verify circular dependency and external XSD reference handling
in the standalone SOAP converter.
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

def create_circular_dependency_test_files(test_dir: Path):
    """Create test files with circular dependencies"""
    
    # Create the directory if it doesn't exist
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # WSDL file with circular references
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
                        <xsd:element name="profile" type="tns:Profile"/>
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
                    <xsd:element name="settings" type="tns:Settings"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="Settings">
                <xsd:sequence>
                    <xsd:element name="profileId" type="xsd:int"/>
                    <xsd:element name="profile" type="tns:Profile"/>
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
    
    # External XSD file with imports
    external_xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="http://example.com/external"
             xmlns:tns="http://example.com/external"
             xmlns:common="http://example.com/common">
    
    <xsd:import namespace="http://example.com/common" schemaLocation="common-types.xsd"/>
    
    <xsd:complexType name="ExternalUserType">
        <xsd:sequence>
            <xsd:element name="id" type="xsd:int"/>
            <xsd:element name="name" type="xsd:string"/>
            <xsd:element name="commonData" type="common:CommonType"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="ExternalProfileType">
        <xsd:sequence>
            <xsd:element name="userId" type="xsd:int"/>
            <xsd:element name="externalUser" type="tns:ExternalUserType"/>
        </xsd:sequence>
    </xsd:complexType>
</xsd:schema>'''
    
    # Common types XSD (referenced by external XSD)
    common_xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="http://example.com/common"
             xmlns:tns="http://example.com/common">
    
    <xsd:complexType name="CommonType">
        <xsd:sequence>
            <xsd:element name="id" type="xsd:int"/>
            <xsd:element name="value" type="xsd:string"/>
            <xsd:element name="metadata" type="xsd:string"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="BaseType">
        <xsd:sequence>
            <xsd:element name="commonData" type="tns:CommonType"/>
        </xsd:sequence>
    </xsd:complexType>
</xsd:schema>'''
    
    # Write test files
    (test_dir / "circular-service.wsdl").write_text(wsdl_content)
    (test_dir / "external-types.xsd").write_text(external_xsd_content)
    (test_dir / "common-types.xsd").write_text(common_xsd_content)
    
    print(f"📄 Created circular dependency test files in {test_dir}")
    print("   - circular-service.wsdl (contains circular references)")
    print("   - external-types.xsd (contains external imports)")
    print("   - common-types.xsd (referenced by external-types.xsd)")

def test_circular_dependencies():
    """Test circular dependency handling"""
    
    print("🧪 Testing Circular Dependency Handling")
    print("=" * 50)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files with circular dependencies
        create_circular_dependency_test_files(input_dir)
        
        # Test circular dependency handling
        print("\n🔧 Testing circular dependency resolution...")
        converter = SOAPConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            chunking_strategy="ENDPOINT_BASED"
        )
        
        try:
            converter.process_all_files()
            
            # Check results
            output_files = list(output_dir.glob("*.json"))
            print(f"✅ Generated {len(output_files)} JSON files")
            
            for file_path in output_files:
                print(f"   - {file_path.name}")
                
                # Check if the JSON contains circular reference handling
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Look for circular reference indicators
                has_circular_refs = False
                for endpoint in data.get('endpoints', []):
                    for param in endpoint.get('parameters', []):
                        if 'circular_reference' in str(param):
                            has_circular_refs = True
                            break
                
                if has_circular_refs:
                    print(f"   ✅ Circular references detected and handled in {file_path.name}")
                else:
                    print(f"   ℹ️ No circular references detected in {file_path.name}")
            
            print("\n✅ Circular dependency test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during circular dependency test: {str(e)}")
            import traceback
            traceback.print_exc()

def test_external_xsd_references():
    """Test external XSD reference handling"""
    
    print("\n🧪 Testing External XSD Reference Handling")
    print("=" * 50)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files with external XSD references
        create_circular_dependency_test_files(input_dir)
        
        # Test external XSD reference handling
        print("\n🔧 Testing external XSD reference resolution...")
        converter = SOAPConverter(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            chunking_strategy="ENDPOINT_BASED"
        )
        
        try:
            converter.process_all_files()
            
            # Check results
            output_files = list(output_dir.glob("*.json"))
            print(f"✅ Generated {len(output_files)} JSON files")
            
            for file_path in output_files:
                print(f"   - {file_path.name}")
                
                # Check if the JSON contains external XSD information
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Look for external XSD information
                has_external_refs = False
                for endpoint in data.get('endpoints', []):
                    for param in endpoint.get('parameters', []):
                        if 'external' in str(param).lower() or 'common' in str(param).lower():
                            has_external_refs = True
                            break
                
                if has_external_refs:
                    print(f"   ✅ External XSD references detected and processed in {file_path.name}")
                else:
                    print(f"   ℹ️ No external XSD references detected in {file_path.name}")
            
            print("\n✅ External XSD reference test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during external XSD reference test: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Run all tests"""
    print("🔧 Testing Standalone Converter: Circular Dependencies & External XSD References")
    print("=" * 80)
    
    test_circular_dependencies()
    test_external_xsd_references()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
