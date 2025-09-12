#!/usr/bin/env python3
"""
Standalone SOAP to CommonAPISpec Converter

This script converts WSDL and XSD files to CommonAPISpec JSON format.
It processes all WSDL and XSD files from an input directory and outputs
the results to an output directory.

All WSDL connector functionality is self-contained in this file.

Usage:
    python standalone_soap_converter.py --input-dir /path/to/wsdl/files --output-dir /path/to/output
    python standalone_soap_converter.py -i ./soap_files -o ./output
    python standalone_soap_converter.py  # Uses default directories: ./input and ./output

Features:
    - Processes multiple WSDL files with XSD dependencies
    - Automatically detects WSDL and XSD files
    - Handles external XSD dependencies
    - Generates CommonAPISpec JSON files
    - Provides detailed processing logs
    - Error handling and recovery
    - Self-contained (no external dependencies)
"""

import os
import sys
import json
import argparse
import logging
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('soap_converter.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CommonAPISpec:
    """Common API specification structure"""
    api_name: str
    version: str
    description: str
    base_url: str
    category: str
    documentation_url: str
    api_type: str
    format: str
    endpoints: List[Dict[str, Any]] = field(default_factory=list)
    data_types: List[Dict[str, Any]] = field(default_factory=list)
    authentication: List[Dict[str, Any]] = field(default_factory=list)
    rate_limits: List[Dict[str, Any]] = field(default_factory=list)
    error_codes: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    contact_info: Dict[str, str] = field(default_factory=dict)
    license_info: Dict[str, str] = field(default_factory=dict)
    external_docs: List[Dict[str, str]] = field(default_factory=list)
    servers: List[Dict[str, str]] = field(default_factory=list)
    security_schemes: List[Dict[str, Any]] = field(default_factory=list)
    sealId: str = "105961"
    application: str = "PROFILE"

class WSDLConnector:
    """Standalone WSDL connector with all functionality self-contained"""
    
    def __init__(self):
        self.namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'soap12': 'http://schemas.xmlsoap.org/wsdl/soap12/',
            'http': 'http://schemas.xmlsoap.org/wsdl/http/',
            'mime': 'http://schemas.xmlsoap.org/wsdl/mime/',
            'tns': None  # Will be set dynamically
        }
        self.xsd_dependencies = {}
        
    def parse_wsdl_files_with_dependencies(self, file_paths: List[str]) -> CommonAPISpec:
        """Parse multiple WSDL/XSD files and convert to common structure, handling external dependencies"""
        try:
            # Identify main WSDL file
            main_wsdl_file = None
            xsd_files = []
            
            for file_path in file_paths:
                if file_path.lower().endswith('.wsdl'):
                    if main_wsdl_file is None:
                        main_wsdl_file = file_path
                    else:
                        logger.warning(f"Multiple WSDL files found, using {main_wsdl_file} as main")
                elif file_path.lower().endswith('.xsd'):
                    xsd_files.append(file_path)
            
            if main_wsdl_file is None:
                raise ValueError("No WSDL file found in the provided files")
            
            logger.info(f"📄 Main WSDL file: {main_wsdl_file}")
            logger.info(f"📄 XSD dependencies: {xsd_files}")
            
            # Load XSD dependencies
            for xsd_file in xsd_files:
                try:
                    tree = ET.parse(xsd_file)
                    root = tree.getroot()
                    schema_info = self._extract_schema_info(root, xsd_file)
                    self.xsd_dependencies[xsd_file] = schema_info
                    logger.info(f"✅ Loaded XSD dependency: {xsd_file}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load XSD dependency {xsd_file}: {str(e)}")
            
            # Parse main WSDL
            tree = ET.parse(main_wsdl_file)
            root = tree.getroot()
            
            # Extract XSD imports from the WSDL
            for import_elem in root.findall('.//xsd:import', self.namespaces):
                schema_location = import_elem.get('schemaLocation')
                namespace = import_elem.get('namespace', '')
                if schema_location:
                    # Check if the imported XSD is in the same directory
                    base_dir = os.path.dirname(main_wsdl_file)
                    import_path = os.path.join(base_dir, schema_location)
                    
                    if os.path.exists(import_path) and import_path not in self.xsd_dependencies:
                        try:
                            import_tree = ET.parse(import_path)
                            import_root = import_tree.getroot()
                            import_schema_info = self._extract_schema_info(import_root, import_path)
                            self.xsd_dependencies[import_path] = import_schema_info
                            logger.info(f"✅ Loaded XSD import: {schema_location}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to load XSD import {schema_location}: {str(e)}")
            
            # Set target namespace
            target_namespace = root.get('targetNamespace', '')
            self.namespaces['tns'] = target_namespace
            
            return self._convert_wsdl_to_common(root, main_wsdl_file)
            
        except Exception as e:
            raise ValueError(f"Error parsing WSDL files with dependencies: {str(e)}")
    
    def _extract_schema_info(self, xsd_root: ET.Element, file_path: str) -> Dict[str, Any]:
        """Extract schema information from XSD file with import resolution"""
        schema_info = {
            'file_path': file_path,
            'elements': {},
            'complex_types': {},
            'simple_types': {},
            'imports': [],
            'resolved_imports': {}
        }
        
        # Extract elements
        for element in xsd_root.findall('.//xsd:element', self.namespaces):
            name = element.get('name')
            if name:
                schema_info['elements'][name] = {
                    'type': element.get('type'),
                    'minOccurs': element.get('minOccurs'),
                    'maxOccurs': element.get('maxOccurs')
                }
        
        # Extract complex types
        for complex_type in xsd_root.findall('.//xsd:complexType', self.namespaces):
            name = complex_type.get('name')
            if name:
                schema_info['complex_types'][name] = self._extract_complex_type_details(complex_type, xsd_root)
        
        # Extract simple types
        for simple_type in xsd_root.findall('.//xsd:simpleType', self.namespaces):
            name = simple_type.get('name')
            if name:
                schema_info['simple_types'][name] = {
                    'restriction': simple_type.find('.//xsd:restriction', self.namespaces) is not None
                }
        
        # Extract imports and resolve them
        for import_elem in xsd_root.findall('.//xsd:import', self.namespaces):
            schema_location = import_elem.get('schemaLocation')
            namespace = import_elem.get('namespace', '')
            if schema_location:
                schema_info['imports'].append({
                    'namespace': namespace,
                    'schemaLocation': schema_location
                })
                
                # Try to resolve the import
                resolved_import = self._resolve_xsd_import(file_path, schema_location, namespace)
                if resolved_import:
                    schema_info['resolved_imports'][schema_location] = resolved_import
        
        return schema_info
    
    def _resolve_xsd_import(self, base_file: str, import_location: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Resolve an XSD import by loading the referenced file"""
        try:
            # Handle relative paths
            if not os.path.isabs(import_location):
                base_dir = os.path.dirname(base_file)
                import_path = os.path.join(base_dir, import_location)
            else:
                import_path = import_location
            
            # Check if the file exists
            if os.path.exists(import_path):
                logger.info(f"📄 Resolving XSD import: {import_location} -> {import_path}")
                
                # Parse the imported XSD file
                import_tree = ET.parse(import_path)
                import_root = import_tree.getroot()
                
                # Extract schema information from the imported file
                import_schema = self._extract_schema_info(import_root, import_path)
                import_schema['namespace'] = namespace
                
                return import_schema
            else:
                logger.warning(f"⚠️ XSD import file not found: {import_path}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Error resolving XSD import {import_location}: {str(e)}")
            return None
    
    def _resolve_type_reference_with_root(self, type_name: str, root: ET.Element) -> tuple[Optional[ET.Element], Optional[ET.Element]]:
        """Resolve a type reference across all loaded XSD dependencies and return both element and root"""
        # First check in the main WSDL/XSD
        complex_type_elem = root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
        if complex_type_elem is not None:
            return complex_type_elem, root
        
        # Then check in XSD dependencies
        for xsd_file, schema_info in self.xsd_dependencies.items():
            # Check in main schema
            if type_name in schema_info.get('complex_types', {}):
                # Load the actual XSD file and find the complex type
                try:
                    xsd_tree = ET.parse(xsd_file)
                    xsd_root = xsd_tree.getroot()
                    external_type = xsd_root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
                    if external_type is not None:
                        logger.debug(f"✅ Found external type {type_name} in {xsd_file}")
                        return external_type, xsd_root
                except Exception as e:
                    logger.warning(f"⚠️ Error loading external XSD {xsd_file}: {str(e)}")
            
            # Check in resolved imports
            for import_location, import_schema in schema_info.get('resolved_imports', {}).items():
                if type_name in import_schema.get('complex_types', {}):
                    # Load the actual imported XSD file and find the complex type
                    try:
                        import_tree = ET.parse(import_location)
                        import_root = import_tree.getroot()
                        external_type = import_root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
                        if external_type is not None:
                            logger.debug(f"✅ Found external type {type_name} in imported file {import_location}")
                            return external_type, import_root
                    except Exception as e:
                        logger.warning(f"⚠️ Error loading imported XSD {import_location}: {str(e)}")
        
        return None, None
    
    def _convert_wsdl_to_common(self, root: ET.Element, file_path: str) -> CommonAPISpec:
        """Convert WSDL to CommonAPISpec format"""
        try:
            # Extract basic information
            service_name = self._extract_service_name(root)
            target_namespace = root.get('targetNamespace', '')
            
            # Extract endpoints
            endpoints = self._extract_endpoints(root)
            
            # Extract data types
            data_types = self._extract_data_types(root)
            
            # Create CommonAPISpec
            common_spec = CommonAPISpec(
                api_name=service_name,
                version="1.0.0",
                description=f"SOAP service: {service_name}",
                base_url=self._extract_base_url(root),
                category="SOAP",
                documentation_url="",
                api_type="SOAP",
                format="WSDL",
                endpoints=endpoints,
                data_types=data_types,
                authentication=self._extract_authentication(root),
                rate_limits=[],
                error_codes=self._extract_error_codes(root),
                examples=[],
                tags=["SOAP", "WSDL"],
                contact_info={},
                license_info={},
                external_docs=[],
                servers=self._extract_servers(root),
                security_schemes=[]
            )
            
            return common_spec
            
        except Exception as e:
            logger.error(f"Error converting WSDL to common format: {str(e)}")
            raise
    
    def _extract_service_name(self, root: ET.Element) -> str:
        """Extract service name from WSDL"""
        service_elem = root.find('.//wsdl:service', self.namespaces)
        if service_elem is not None:
            return service_elem.get('name', 'UnknownService')
        return 'UnknownService'
    
    def _extract_base_url(self, root: ET.Element) -> str:
        """Extract base URL from WSDL"""
        port_elem = root.find('.//wsdl:port', self.namespaces)
        if port_elem is not None:
            address_elem = port_elem.find('.//soap:address', self.namespaces)
            if address_elem is None:
                address_elem = port_elem.find('.//soap12:address', self.namespaces)
            if address_elem is not None:
                return address_elem.get('location', '')
        return ''
    
    def _extract_endpoints(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract endpoints from WSDL"""
        endpoints = []
        
        # Get all port types
        port_types = root.findall('.//wsdl:portType', self.namespaces)
        
        for port_type in port_types:
            port_type_name = port_type.get('name', '')
            operations = self._extract_operations_from_port_type(port_type, root)
            
            for operation in operations:
                endpoint = {
                    'path': f"/{operation['operation_name']}",
                    'method': 'POST',  # SOAP always uses POST
                    'summary': operation['summary'],
                    'description': operation['description'],
                    'operation_name': operation['operation_name'],
                    'soap_headers': operation.get('soap_headers', []),
                    'request': operation.get('request', {}),
                    'response': operation.get('response', {}),
                    'parameters': operation.get('parameters', []),
                    'responses': operation.get('responses', {}),
                    'tags': [port_type_name] if port_type_name else []
                }
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_operations_from_port_type(self, port_type: ET.Element, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract operations from a port type"""
        operations = []
        
        for operation in port_type.findall('.//wsdl:operation', self.namespaces):
            operation_name = operation.get('name', '')
            if not operation_name:
                continue
            
            # Get input and output messages
            input_elem = operation.find('wsdl:input', self.namespaces)
            output_elem = operation.find('wsdl:output', self.namespaces)
            
            request = {}
            response = {}
            
            if input_elem is not None:
                message_name = input_elem.get('message', '')
                request = self._extract_message_details(message_name, root)
            
            if output_elem is not None:
                message_name = output_elem.get('message', '')
                response = self._extract_message_details(message_name, root)
            
            operation_data = {
                'operation_name': operation_name,
                'summary': f"SOAP operation: {operation_name}",
                'description': f"SOAP operation {operation_name}",
                'soap_headers': [],
                'request': request,
                'response': response,
                'parameters': request.get('all_attributes', []),
                'responses': {
                    '200': {
                        'description': 'Successful response',
                        'content': response.get('all_attributes', [])
                    }
                }
            }
            
            operations.append(operation_data)
        
        return operations
    
    def _extract_message_details(self, message_name: str, root: ET.Element) -> Dict[str, Any]:
        """Extract message details from WSDL"""
        logger.debug(f"🔍 Extracting message: {message_name}")
        
        # Handle qualified message names (e.g., "tns:GetUserRequestMessage")
        if ':' in message_name:
            prefix, local_name = message_name.split(':', 1)
            # Try with namespace prefix first
            message_elem = root.find(f'.//wsdl:message[@name="{message_name}"]', self.namespaces)
            if message_elem is None:
                # Try without prefix
                message_elem = root.find(f'.//wsdl:message[@name="{local_name}"]', self.namespaces)
        else:
            message_elem = root.find(f'.//wsdl:message[@name="{message_name}"]', self.namespaces)
        
        if message_elem is None:
            logger.warning(f"⚠️ Message not found: {message_name}")
            return {}
        
        all_attributes = []
        
        for part in message_elem.findall('.//wsdl:part', self.namespaces):
            part_name = part.get('name', '')
            part_type = part.get('type', '')
            part_element = part.get('element', '')
            
            logger.debug(f"🔍 Part: {part_name}, type: {part_type}, element: {part_element}")
            
            if part_element:
                # Extract element details
                element_details = self._extract_element_details(part_element, root)
                if element_details:
                    all_attributes.append(element_details)
                    logger.debug(f"✅ Extracted element: {element_details}")
            elif part_type:
                # Extract type details
                type_details = self._extract_type_details(part_type, root)
                if type_details:
                    all_attributes.append(type_details)
                    logger.debug(f"✅ Extracted type: {type_details}")
        
        logger.debug(f"📋 Message {message_name} has {len(all_attributes)} attributes")
        
        # Flatten all nested attributes into the main all_attributes array
        flattened_attributes = []
        for attr in all_attributes:
            flattened_attributes.append(attr)
            # Add nested attributes from complex_type.nested_attributes
            if 'complex_type' in attr and 'nested_attributes' in attr['complex_type']:
                nested_attrs = attr['complex_type']['nested_attributes']
                flattened_attributes.extend(nested_attrs)
            # Add nested attributes from direct nested_attributes field (only if not already added from complex_type)
            elif 'nested_attributes' in attr:
                nested_attrs = attr['nested_attributes']
                flattened_attributes.extend(nested_attrs)
        
        return {
            'message_name': message_name,
            'all_attributes': flattened_attributes
        }
    
    def _extract_element_details(self, element_name: str, root: ET.Element) -> Dict[str, Any]:
        """Extract element details from WSDL/XSD"""
        # Handle qualified element names (e.g., "tns:GetUserRequest")
        if ':' in element_name:
            prefix, local_name = element_name.split(':', 1)
            # Try with namespace prefix first
            element_elem = root.find(f'.//xsd:element[@name="{element_name}"]', self.namespaces)
            if element_elem is None:
                # Try without prefix
                element_elem = root.find(f'.//xsd:element[@name="{local_name}"]', self.namespaces)
        else:
            element_elem = root.find(f'.//xsd:element[@name="{element_name}"]', self.namespaces)
        
        if element_elem is None:
            return {}
        
        element_type = element_elem.get('type', '')
        min_occurs = element_elem.get('minOccurs', '1')
        max_occurs = element_elem.get('maxOccurs', '1')
        nillable = element_elem.get('nillable', 'false')
        
        element_details = {
            'name': element_name,
            'type': element_type,
            'min_occurs': min_occurs,
            'max_occurs': max_occurs,
            'nillable': nillable == 'true',
            'description': f"Element: {element_name}",
            'is_nested': False
        }
        
        # Check for complex type
        if element_type and ':' in element_type:
            prefix, type_name = element_type.split(':', 1)
            complex_type_elem, _ = self._resolve_type_reference_with_root(type_name, root)
            
            if complex_type_elem is not None:
                nested_details = self._extract_complex_type_details(complex_type_elem, root)
                element_details['complex_type'] = nested_details
                
                # Extract nested attributes
                nested_attributes = self._extract_nested_attributes(
                    complex_type_elem, 
                    root, 
                    element_name, 
                    set(), 
                    0, 
                    0
                )
                element_details['nested_attributes'] = nested_attributes
        
        # Also check for inline complex type definition
        inline_complex_type = element_elem.find('xsd:complexType', self.namespaces)
        if inline_complex_type is not None:
            nested_details = self._extract_complex_type_details(inline_complex_type, root)
            element_details['complex_type'] = nested_details
            
            # Extract nested attributes
            nested_attributes = self._extract_nested_attributes(
                inline_complex_type, 
                root, 
                element_name, 
                set(), 
                0, 
                0
            )
            element_details['nested_attributes'] = nested_attributes
        
        return element_details
    
    def _extract_type_details(self, type_name: str, root: ET.Element) -> Dict[str, Any]:
        """Extract type details from WSDL/XSD"""
        if ':' not in type_name:
            return {
                'name': type_name,
                'type': type_name,
                'description': f"Type: {type_name}",
                'is_nested': False
            }
        
        prefix, local_type_name = type_name.split(':', 1)
        complex_type_elem = self._resolve_type_reference(local_type_name, root)
        
        if complex_type_elem is not None:
            type_details = {
                'name': local_type_name,
                'type': type_name,
                'description': f"Complex type: {local_type_name}",
                'is_nested': False
            }
            
            nested_details = self._extract_complex_type_details(complex_type_elem, root)
            type_details['complex_type'] = nested_details
            
            # Extract nested attributes
            nested_attributes = self._extract_nested_attributes(
                complex_type_elem, 
                root, 
                local_type_name, 
                set(), 
                0, 
                0
            )
            type_details['nested_attributes'] = nested_attributes
            
            return type_details
        
        return {
            'name': local_type_name,
            'type': type_name,
            'description': f"Type: {local_type_name}",
            'is_nested': False
        }
    
    def _extract_complex_type_details(self, complex_type: ET.Element, root: ET.Element, visited_types: set = None) -> Dict[str, Any]:
        """Extract details from a complex type definition"""
        if visited_types is None:
            visited_types = set()
        
        type_name = complex_type.get('name', '')
        if type_name in visited_types:
            logger.warning(f"⚠️ Circular reference detected for type: {type_name}")
            return {}
        
        visited_types.add(type_name)
        
        details = {
            'name': type_name,
            'attributes': [],
            'sequences': [],
            'nested_attributes': []
        }
        
        # Handle inheritance (xsd:extension)
        for complex_content in complex_type.findall('.//xsd:complexContent', self.namespaces):
            for extension in complex_content.findall('.//xsd:extension', self.namespaces):
                base_type = extension.get('base', '')
                if base_type and ':' in base_type:
                    # Extract base type name
                    prefix, base_type_name = base_type.split(':', 1)
                    
                    # Check for circular inheritance using a more specific key
                    inheritance_key = f"{type_name}->{base_type_name}"
                    if inheritance_key in visited_types:
                        logger.warning(f"⚠️ Circular inheritance detected: {type_name} -> {base_type_name}")
                        continue
                    
                    logger.debug(f"🔗 Processing inheritance: {type_name} extends {base_type}")
                    
                    # Create a new visited set for inheritance to avoid false circular references
                    inheritance_visited = visited_types.copy()
                    inheritance_visited.add(inheritance_key)  # Add inheritance key to prevent circular inheritance
                    
                    # Resolve the base type
                    base_type_elem, base_root = self._resolve_type_reference_with_root(base_type_name, root)
                    if base_type_elem is not None:
                        # Extract base type details with inheritance-aware visited set
                        base_details = self._extract_complex_type_details(base_type_elem, base_root, inheritance_visited)
                        
                        # Merge base type attributes into current type
                        details['attributes'].extend(base_details.get('attributes', []))
                        details['sequences'].extend(base_details.get('sequences', []))
                        details['nested_attributes'].extend(base_details.get('nested_attributes', []))
                        
                        logger.debug(f"✅ Merged {len(base_details.get('attributes', []))} attributes from base type {base_type_name}")
        
        # Extract sequences
        for sequence in complex_type.findall('.//xsd:sequence', self.namespaces):
            sequence_details = {
                'elements': []
            }
            
            for element in sequence.findall('.//xsd:element', self.namespaces):
                element_name = element.get('name', '')
                element_type = element.get('type', '')
                min_occurs = element.get('minOccurs', '1')
                max_occurs = element.get('maxOccurs', '1')
                nillable = element.get('nillable', 'false')
                
                element_details = {
                    'name': element_name,
                    'type': element_type,
                    'min_occurs': min_occurs,
                    'max_occurs': max_occurs,
                    'nillable': nillable == 'true',
                    'description': f"Element: {element_name}"
                }
                
                sequence_details['elements'].append(element_details)
                details['attributes'].append(element_details)
                
                # Check if this element has nested complex type (recursive extraction)
                if root is not None:
                    element_path = f"{type_name}.{element.get('name', '')}"
                    nested_attributes = self._extract_nested_attributes(element, root, element_path, visited_types.copy(), 0, 0)
                    details['nested_attributes'].extend(nested_attributes)
            
            details['sequences'].append(sequence_details)
        
        # Extract direct sequence elements (for non-inherited complex types)
        for element in complex_type.findall('.//xsd:element', self.namespaces):
            element_name = element.get('name', '')
            element_type = element.get('type', '')
            min_occurs = element.get('minOccurs', '1')
            max_occurs = element.get('maxOccurs', '1')
            nillable = element.get('nillable', 'false')
            
            element_details = {
                'name': element_name,
                'type': element_type,
                'min_occurs': min_occurs,
                'max_occurs': max_occurs,
                'nillable': nillable == 'true',
                'description': f"Element: {element_name}"
            }
            
            details['attributes'].append(element_details)
            
            # Note: Nested attributes are already extracted in the sequence processing above
            # No need to extract them again here to avoid duplicates
        
        return details
    
    def _extract_nested_attributes(self, element: ET.Element, root: ET.Element, parent_path: str = "", visited_types: set = None, depth: int = 0, circular_count: int = 0) -> List[Dict[str, Any]]:
        """Recursively extract all nested attributes until leaf nodes with depth limiting"""
        if visited_types is None:
            visited_types = set()
            
        # Add depth limit to prevent infinite recursion
        if depth > 8:  # Reduced from 15 to 8 for better performance
            logger.warning(f"⚠️ Maximum recursion depth reached for path: {parent_path}")
            return []
            
        # Limit circular references to prevent excessive processing
        if circular_count > 5:  # Maximum circular references allowed
            logger.warning(f"⚠️ Too many circular references detected ({circular_count}), stopping recursion")
            return []
            
        nested_attributes = []
        element_name = element.get('name', '')
        element_type = element.get('type', '')
        
        # Build the path for nested elements
        current_path = f"{parent_path}.{element_name}" if parent_path else element_name
        
        # Check if this element has a complex type definition
        if element_type and ':' in element_type:
            # Handle qualified type names (e.g., "tns:DailyForecast")
            prefix, type_name = element_type.split(':', 1)
            
            # Check for circular reference using improved path-based detection
            # Create a path-based identifier that includes the current context
            path_key = f"{current_path}:{type_name}"
            
            if path_key in visited_types:
                logger.warning(f"⚠️ Circular reference detected in path: {path_key}")
                # Increment circular count and check limit
                new_circular_count = circular_count + 1
                if new_circular_count > 5:
                    logger.warning(f"⚠️ Too many circular references detected ({new_circular_count}), stopping recursion")
                    return []
                return []
                
            # Use enhanced type resolution that checks XSD dependencies
            complex_type_elem, external_root = self._resolve_type_reference_with_root(type_name, root)
            
            if complex_type_elem is not None:
                # Add current path to visited types before recursive call
                visited_types.add(path_key)
                
                # Use the appropriate root element (external_root if from external XSD, otherwise root)
                search_root = external_root if external_root is not None else root
                
                # Recursively extract nested complex type details
                nested_details = self._extract_complex_type_details(complex_type_elem, search_root, visited_types.copy())
                
                # Extract nested attributes recursively with depth limiting
                nested_attributes = self._extract_nested_attributes(
                    complex_type_elem, 
                    search_root, 
                    current_path, 
                    visited_types.copy(),
                    depth + 1,
                    circular_count
                )
                
                # Process nested sequences
                for sequence in nested_details.get('sequences', []):
                    for nested_element in sequence.get('elements', []):
                        nested_attr = {
                            'name': nested_element['name'],
                            'type': nested_element['type'],
                            'min_occurs': nested_element['min_occurs'],
                            'max_occurs': nested_element['max_occurs'],
                            'nillable': nested_element['nillable'],
                            'description': nested_element['description'],
                            'parent_path': current_path,
                            'is_nested': True
                        }
                        nested_attributes.append(nested_attr)
                        
                        # Find the actual XML element for recursive processing
                        actual_element = complex_type_elem.find(f'.//xsd:element[@name="{nested_element["name"]}"]', self.namespaces)
                        if actual_element is not None:
                            nested_attributes.extend(
                                self._extract_nested_attributes(
                                    actual_element, 
                                    root, 
                                    current_path,
                                    visited_types.copy(),
                                    depth + 1,
                                    circular_count
                                )
                            )
        
        # Also check for inline complex type definition
        inline_complex_type = element.find('xsd:complexType', self.namespaces)
        if inline_complex_type is not None:
            nested_details = self._extract_complex_type_details(inline_complex_type, root, visited_types.copy())
            
            # Process nested sequences
            for sequence in nested_details.get('sequences', []):
                for nested_element in sequence.get('elements', []):
                    nested_attr = {
                        'name': nested_element['name'],
                        'type': nested_element['type'],
                        'min_occurs': nested_element['min_occurs'],
                        'max_occurs': nested_element['max_occurs'],
                        'nillable': nested_element['nillable'],
                        'description': nested_element['description'],
                        'parent_path': current_path,
                        'is_nested': True
                    }
                    nested_attributes.append(nested_attr)
                    
                    # Find the actual XML element for recursive processing
                    actual_element = inline_complex_type.find(f'.//xsd:element[@name="{nested_element["name"]}"]', self.namespaces)
                    if actual_element is not None:
                        nested_attributes.extend(
                            self._extract_nested_attributes(
                                actual_element, 
                                root, 
                                current_path,
                                visited_types.copy(),
                                depth + 1,
                                circular_count
                            )
                        )
        
        return nested_attributes
    
    def _extract_data_types(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract data types from WSDL"""
        data_types = []
        
        # Extract complex types
        for complex_type in root.findall('.//xsd:complexType', self.namespaces):
            type_name = complex_type.get('name', '')
            if type_name:
                type_details = self._extract_complex_type_details(complex_type, root)
                data_types.append({
                    'name': type_name,
                    'type': 'complex',
                    'description': f"Complex type: {type_name}",
                    'properties': type_details.get('attributes', []),
                    'nested_attributes': type_details.get('nested_attributes', [])
                })
        
        # Extract simple types
        for simple_type in root.findall('.//xsd:simpleType', self.namespaces):
            type_name = simple_type.get('name', '')
            if type_name:
                data_types.append({
                    'name': type_name,
                    'type': 'simple',
                    'description': f"Simple type: {type_name}",
                    'properties': []
                })
        
        return data_types
    
    def _extract_authentication(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract authentication information from WSDL"""
        auth_methods = []
        
        # Check for SOAP binding security
        bindings = root.findall('.//wsdl:binding', self.namespaces)
        for binding in bindings:
            # This is a simplified extraction - real WSDLs might have more complex security
            auth_methods.append({
                'type': 'SOAP',
                'description': 'SOAP-based authentication',
                'scheme': 'bearer'
            })
        
        return auth_methods
    
    def _extract_error_codes(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract error codes from WSDL"""
        # WSDL doesn't typically define error codes like REST APIs
        # This is a placeholder for potential fault definitions
        error_codes = []
        
        # Check for fault definitions
        for fault in root.findall('.//wsdl:fault', self.namespaces):
            fault_name = fault.get('name', '')
            if fault_name:
                error_codes.append({
                    'code': fault_name,
                    'message': f"SOAP fault: {fault_name}",
                    'description': f"SOAP fault definition: {fault_name}"
                })
        
        return error_codes
    
    def _extract_servers(self, root: ET.Element) -> List[Dict[str, str]]:
        """Extract server information from WSDL"""
        servers = []
        
        # Extract service endpoints
        services = root.findall('.//wsdl:service', self.namespaces)
        for service in services:
            service_name = service.get('name', '')
            ports = service.findall('.//wsdl:port', self.namespaces)
            
            for port in ports:
                port_name = port.get('name', '')
                address_elem = port.find('.//soap:address', self.namespaces)
                if address_elem is None:
                    address_elem = port.find('.//soap12:address', self.namespaces)
                
                if address_elem is not None:
                    location = address_elem.get('location', '')
                    servers.append({
                        'url': location,
                        'description': f"SOAP endpoint: {service_name}/{port_name}"
                    })
        
        return servers

class StandaloneSOAPConverter:
    """Standalone SOAP converter with all functionality self-contained"""
    
    def __init__(self, input_dir: str, output_dir: str, chunking_strategy: str = "ENDPOINT_BASED", use_timestamp: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunking_strategy = chunking_strategy
        self.use_timestamp = use_timestamp
        self.wsdl_connector = WSDLConnector()
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🚀 Starting Standalone SOAP to CommonAPISpec conversion")
        logger.info(f"📁 Input directory: {self.input_dir}")
        logger.info(f"📁 Output directory: {self.output_dir}")
    
    def _group_files_by_service(self, wsdl_files: List[Path], xsd_files: List[Path]) -> Dict[str, Dict[str, List[Path]]]:
        """Group WSDL and XSD files by service name"""
        service_groups = {}
        
        # Group WSDL files by name (without extension)
        for wsdl_file in wsdl_files:
            service_name = wsdl_file.stem
            if service_name not in service_groups:
                service_groups[service_name] = {'wsdl': [], 'xsd': []}
            service_groups[service_name]['wsdl'].append(wsdl_file)
        
        # Group XSD files by name similarity
        for xsd_file in xsd_files:
            xsd_name = xsd_file.stem
            # Try to match with existing service groups
            matched = False
            for service_name in service_groups.keys():
                if service_name.lower() in xsd_name.lower() or xsd_name.lower() in service_name.lower():
                    service_groups[service_name]['xsd'].append(xsd_file)
                    matched = True
                    break
            
            if not matched:
                # Create new service group for standalone XSD
                service_groups[xsd_name] = {'wsdl': [], 'xsd': [xsd_file]}
        
        return service_groups
    
    def convert_service_group(self, service_name: str, service_files: Dict[str, List[Path]]) -> None:
        """Convert a group of WSDL/XSD files"""
        try:
            logger.info(f"🔄 Converting service: {service_name}")
            
            # Prepare file paths
            file_paths = []
            for wsdl_file in service_files['wsdl']:
                file_paths.append(str(wsdl_file))
            for xsd_file in service_files['xsd']:
                file_paths.append(str(xsd_file))
            
            if not file_paths:
                logger.warning(f"⚠️ No files found for service: {service_name}")
                return
            
            # Convert using WSDL connector
            common_spec = self.wsdl_connector.parse_wsdl_files_with_dependencies(file_paths)
            
            # Generate output filename
            if self.use_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{service_name}_{timestamp}.json"
            else:
                output_filename = f"{service_name}.json"
            output_path = self.output_dir / output_filename
            
            # Convert to JSON and save
            spec_dict = self._common_spec_to_dict(common_spec)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(spec_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Successfully converted service: {service_name}")
            logger.info(f"💾 Saved CommonAPISpec to: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Error converting service {service_name}: {str(e)}")
            logger.error(traceback.format_exc())
    
    def _common_spec_to_dict(self, common_spec: CommonAPISpec) -> Dict[str, Any]:
        """Convert CommonAPISpec to dictionary"""
        return {
            'api_name': common_spec.api_name,
            'version': common_spec.version,
            'description': common_spec.description,
            'base_url': common_spec.base_url,
            'category': common_spec.category,
            'documentation_url': common_spec.documentation_url,
            'api_type': common_spec.api_type,
            'format': common_spec.format,
            'endpoints': common_spec.endpoints,
            'data_types': common_spec.data_types,
            'authentication': common_spec.authentication,
            'rate_limits': common_spec.rate_limits,
            'error_codes': common_spec.error_codes,
            'examples': common_spec.examples,
            'tags': common_spec.tags,
            'contact_info': common_spec.contact_info,
            'license_info': common_spec.license_info,
            'external_docs': common_spec.external_docs,
            'servers': common_spec.servers,
            'security_schemes': common_spec.security_schemes,
            'sealId': common_spec.sealId,
            'application': common_spec.application
        }
    
    def process_all_files(self) -> None:
        """Process all WSDL and XSD files in the input directory"""
        try:
            # Find all WSDL and XSD files
            wsdl_files = list(self.input_dir.glob("*.wsdl"))
            xsd_files = list(self.input_dir.glob("*.xsd"))
            
            logger.info(f"📄 Found {len(wsdl_files)} WSDL files")
            logger.info(f"📄 Found {len(xsd_files)} XSD files")
            logger.info(f"📄 Total files: {len(wsdl_files) + len(xsd_files)}")
            
            if not wsdl_files and not xsd_files:
                logger.warning("⚠️ No WSDL or XSD files found in input directory")
                return
            
            # Group files by service
            service_groups = self._group_files_by_service(wsdl_files, xsd_files)
            
            logger.info(f"🔗 Found {len(service_groups)} service groups")
            for service_name, files in service_groups.items():
                logger.info(f"🔗 Service '{service_name}': {len(files['wsdl'])} WSDL + {len(files['xsd'])} XSD files")
            
            # Process each service group
            for service_name, service_files in service_groups.items():
                self.convert_service_group(service_name, service_files)
            
            logger.info("🎉 Processing complete!")
            
        except Exception as e:
            logger.error(f"❌ Error processing files: {str(e)}")
            logger.error(traceback.format_exc())

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert SOAP (WSDL/XSD) files to CommonAPISpec JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python standalone_soap_converter.py --input-dir ./soap_files --output-dir ./output
    python standalone_soap_converter.py -i ./wsdl_files -o ./json_output
    python standalone_soap_converter.py  # Uses default directories: ./input and ./output
    
Environment Variables:
    export SOAP_INPUT_DIR=/path/to/wsdl/files
    export SOAP_OUTPUT_DIR=/path/to/output
    python standalone_soap_converter.py  # Uses environment variables
        """
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        default=os.getenv('SOAP_INPUT_DIR', './input'),
        help='Directory containing WSDL and XSD files (default: ./input or SOAP_INPUT_DIR env var)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default=os.getenv('SOAP_OUTPUT_DIR', './output'),
        help='Directory to output CommonAPISpec JSON files (default: ./output or SOAP_OUTPUT_DIR env var)'
    )
    
    parser.add_argument(
        '--chunking-strategy',
        choices=['FIXED_SIZE', 'SEMANTIC', 'HYBRID', 'ENDPOINT_BASED'],
        default='ENDPOINT_BASED',
        help='Chunking strategy for ChromaDB storage (default: ENDPOINT_BASED)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--timestamp',
        action='store_true',
        help='Include timestamp in output filenames (default: overwrite existing files)'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        converter = StandaloneSOAPConverter(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            chunking_strategy=args.chunking_strategy,
            use_timestamp=args.timestamp
        )
        
        converter.process_all_files()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
