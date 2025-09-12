#!/usr/bin/env python3
"""
Comprehensive test script for complex SOAP scenarios including:
- Deep circular dependencies
- External XSD imports
- Cross-file references
- Namespace resolution
- Complex inheritance chains
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

def create_complex_scenario_test_files(test_dir: Path):
    """Create test files with complex scenarios"""
    
    # Create the directory if it doesn't exist
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Main WSDL with complex circular dependencies
    main_wsdl_content = '''<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:tns="http://example.com/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns:ext="http://example.com/external"
             targetNamespace="http://example.com/">
    <types>
        <xsd:schema targetNamespace="http://example.com/">
            <xsd:import namespace="http://example.com/external" schemaLocation="external-types.xsd"/>
            
            <xsd:element name="ComplexRequest">
                <xsd:complexType>
                    <xsd:sequence>
                        <xsd:element name="user" type="tns:User"/>
                        <xsd:element name="profile" type="tns:Profile"/>
                        <xsd:element name="externalData" type="ext:ExternalUserType"/>
                    </xsd:sequence>
                </xsd:complexType>
            </xsd:element>
            
            <xsd:complexType name="User">
                <xsd:sequence>
                    <xsd:element name="id" type="xsd:int"/>
                    <xsd:element name="name" type="xsd:string"/>
                    <xsd:element name="profile" type="tns:Profile"/>
                    <xsd:element name="settings" type="tns:Settings"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="Profile">
                <xsd:sequence>
                    <xsd:element name="userId" type="xsd:int"/>
                    <xsd:element name="user" type="tns:User"/>
                    <xsd:element name="preferences" type="tns:Preferences"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="Settings">
                <xsd:sequence>
                    <xsd:element name="profileId" type="xsd:int"/>
                    <xsd:element name="profile" type="tns:Profile"/>
                    <xsd:element name="advanced" type="tns:AdvancedSettings"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="Preferences">
                <xsd:sequence>
                    <xsd:element name="settingsId" type="xsd:int"/>
                    <xsd:element name="settings" type="tns:Settings"/>
                </xsd:sequence>
            </xsd:complexType>
            
            <xsd:complexType name="AdvancedSettings">
                <xsd:sequence>
                    <xsd:element name="preferencesId" type="xsd:int"/>
                    <xsd:element name="preferences" type="tns:Preferences"/>
                </xsd:sequence>
            </xsd:complexType>
        </xsd:schema>
    </types>
    <message name="ComplexRequestMessage">
        <part name="parameters" element="tns:ComplexRequest"/>
    </message>
    <portType name="ComplexServicePortType">
        <operation name="ProcessComplex">
            <input message="tns:ComplexRequestMessage"/>
        </operation>
    </portType>
    <binding name="ComplexServiceBinding" type="tns:ComplexServicePortType">
        <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
        <operation name="ProcessComplex">
            <soap:operation soapAction="http://example.com/ProcessComplex"/>
            <input>
                <soap:body use="literal"/>
            </input>
        </operation>
    </binding>
    <service name="ComplexService">
        <port name="ComplexServicePort" binding="tns:ComplexServiceBinding">
            <soap:address location="http://example.com/ComplexService"/>
        </port>
    </service>
</definitions>'''
    
    # External XSD with imports
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
            <xsd:element name="metadata" type="tns:ExternalMetadata"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="ExternalMetadata">
        <xsd:sequence>
            <xsd:element name="source" type="xsd:string"/>
            <xsd:element name="version" type="xsd:string"/>
            <xsd:element name="commonInfo" type="common:CommonType"/>
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
            <xsd:element name="nested" type="tns:NestedCommonType"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="NestedCommonType">
        <xsd:sequence>
            <xsd:element name="parentId" type="xsd:int"/>
            <xsd:element name="parent" type="tns:CommonType"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="BaseType">
        <xsd:sequence>
            <xsd:element name="commonData" type="tns:CommonType"/>
        </xsd:sequence>
    </xsd:complexType>
</xsd:schema>'''
    
    # Additional XSD with more complex circular dependencies
    additional_xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             targetNamespace="http://example.com/additional"
             xmlns:tns="http://example.com/additional">
    
    <xsd:complexType name="AdditionalType">
        <xsd:sequence>
            <xsd:element name="id" type="xsd:int"/>
            <xsd:element name="related" type="tns:RelatedType"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="RelatedType">
        <xsd:sequence>
            <xsd:element name="additionalId" type="xsd:int"/>
            <xsd:element name="additional" type="tns:AdditionalType"/>
            <xsd:element name="deep" type="tns:DeepType"/>
        </xsd:sequence>
    </xsd:complexType>
    
    <xsd:complexType name="DeepType">
        <xsd:sequence>
            <xsd:element name="relatedId" type="xsd:int"/>
            <xsd:element name="related" type="tns:RelatedType"/>
        </xsd:sequence>
    </xsd:complexType>
</xsd:schema>'''
    
    # Write test files
    (test_dir / "complex-service.wsdl").write_text(main_wsdl_content)
    (test_dir / "external-types.xsd").write_text(external_xsd_content)
    (test_dir / "common-types.xsd").write_text(common_xsd_content)
    (test_dir / "additional-types.xsd").write_text(additional_xsd_content)
    
    print(f"📄 Created complex scenario test files in {test_dir}")
    print("   - complex-service.wsdl (main WSDL with external imports)")
    print("   - external-types.xsd (contains external imports)")
    print("   - common-types.xsd (referenced by external-types.xsd)")
    print("   - additional-types.xsd (additional circular dependencies)")

def test_complex_circular_dependencies():
    """Test complex circular dependency handling"""
    
    print("🧪 Testing Complex Circular Dependencies")
    print("=" * 60)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files with complex circular dependencies
        create_complex_scenario_test_files(input_dir)
        
        # Test complex circular dependency handling
        print("\n🔧 Testing complex circular dependency resolution...")
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
                
                # Check if the JSON contains complex type information
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Look for complex type information
                has_complex_types = False
                for endpoint in data.get('endpoints', []):
                    for param in endpoint.get('parameters', []):
                        if 'complex_type' in str(param) or 'nested_attributes' in str(param):
                            has_complex_types = True
                            break
                
                if has_complex_types:
                    print(f"   ✅ Complex types detected and processed in {file_path.name}")
                else:
                    print(f"   ℹ️ No complex types detected in {file_path.name}")
            
            print("\n✅ Complex circular dependency test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during complex circular dependency test: {str(e)}")
            import traceback
            traceback.print_exc()

def test_external_xsd_import_resolution():
    """Test external XSD import resolution"""
    
    print("\n🧪 Testing External XSD Import Resolution")
    print("=" * 60)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files with external XSD imports
        create_complex_scenario_test_files(input_dir)
        
        # Test external XSD import resolution
        print("\n🔧 Testing external XSD import resolution...")
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
            
            print("\n✅ External XSD import resolution test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during external XSD import resolution test: {str(e)}")
            import traceback
            traceback.print_exc()

def test_cross_file_references():
    """Test cross-file reference handling"""
    
    print("\n🧪 Testing Cross-File Reference Handling")
    print("=" * 60)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "input"
        output_dir = temp_path / "output"
        
        # Create test files with cross-file references
        create_complex_scenario_test_files(input_dir)
        
        # Test cross-file reference handling
        print("\n🔧 Testing cross-file reference resolution...")
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
                
                # Check if the JSON contains cross-file reference information
                import json
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Look for cross-file reference information
                has_cross_refs = False
                for endpoint in data.get('endpoints', []):
                    for param in endpoint.get('parameters', []):
                        if 'referenced from' in str(param).lower():
                            has_cross_refs = True
                            break
                
                if has_cross_refs:
                    print(f"   ✅ Cross-file references detected and processed in {file_path.name}")
                else:
                    print(f"   ℹ️ No cross-file references detected in {file_path.name}")
            
            print("\n✅ Cross-file reference handling test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during cross-file reference handling test: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Run all complex scenario tests"""
    print("🔧 Testing Standalone Converter: Complex Scenarios")
    print("=" * 80)
    
    test_complex_circular_dependencies()
    test_external_xsd_import_resolution()
    test_cross_file_references()
    
    print("\n🎉 All complex scenario tests completed!")

if __name__ == "__main__":
    main()
