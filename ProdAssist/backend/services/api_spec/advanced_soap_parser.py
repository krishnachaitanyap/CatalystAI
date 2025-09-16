"""
Advanced SOAP/WSDL Parser with Java-inspired patterns
Leverages proven techniques from Apache CXF, JAXB, and JAX-WS
"""
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import os
from dataclasses import dataclass
from utils.logging import LoggerMixin


@dataclass
class QualifiedName:
    """Java-inspired qualified name for namespace-aware type identification"""
    namespace_uri: str
    local_name: str
    
    def __str__(self) -> str:
        return f"{self.namespace_uri}#{self.local_name}"
    
    def __hash__(self) -> int:
        return hash((self.namespace_uri, self.local_name))
    
    def __eq__(self, other) -> bool:
        return isinstance(other, QualifiedName) and \
               self.namespace_uri == other.namespace_uri and \
               self.local_name == other.local_name


@dataclass
class TypeContext:
    """Context for type processing to prevent circular references"""
    processing_stack: List[QualifiedName]
    visited_types: Set[QualifiedName]
    depth: int = 0
    max_depth: int = 10


class AdvancedSOAPParser(LoggerMixin):
    """Advanced SOAP parser with Java-inspired patterns"""
    
    def __init__(self):
        self.namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'soap12': 'http://schemas.xmlsoap.org/wsdl/soap12/',
            'tns': None  # Will be set dynamically
        }
        self.xsd_dependencies: Dict[str, ET.Element] = {}
        self.type_registry: Dict[QualifiedName, Dict[str, Any]] = {}
    
    def parse_wsdl_with_dependencies(self, wsdl_content: str, xsd_files: List[str] = None) -> Dict[str, Any]:
        """Parse WSDL with external XSD dependencies using Java-inspired patterns"""
        
        try:
            # Parse main WSDL
            wsdl_root = ET.fromstring(wsdl_content)
            self._set_target_namespace(wsdl_root)
            
            # Load XSD dependencies
            if xsd_files:
                self._load_xsd_dependencies(xsd_files)
            
            # Extract XSD imports from WSDL
            self._extract_xsd_imports(wsdl_root)
            
            # Build type registry
            self._build_type_registry(wsdl_root)
            
            # Extract comprehensive WSDL information
            wsdl_info = self._extract_wsdl_info(wsdl_root)
            
            self.logger.info(f"✅ Successfully parsed WSDL with {len(self.xsd_dependencies)} XSD dependencies")
            return wsdl_info
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing WSDL: {str(e)}")
            raise
    
    def _set_target_namespace(self, root: ET.Element):
        """Set target namespace for proper qualified name resolution"""
        target_ns = root.get('targetNamespace', '')
        if target_ns:
            self.namespaces['tns'] = target_ns
    
    def _load_xsd_dependencies(self, xsd_files: List[str]):
        """Load external XSD files into dependency registry"""
        for xsd_file in xsd_files:
            if os.path.exists(xsd_file):
                try:
                    xsd_tree = ET.parse(xsd_file)
                    xsd_root = xsd_tree.getroot()
                    self.xsd_dependencies[xsd_file] = xsd_root
                    self.logger.info(f"✅ Loaded XSD dependency: {xsd_file}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to load XSD {xsd_file}: {str(e)}")
    
    def _extract_xsd_imports(self, wsdl_root: ET.Element):
        """Extract and load XSD imports from WSDL"""
        base_dir = os.path.dirname(wsdl_root.get('__file__', ''))
        
        for import_elem in wsdl_root.findall('.//xsd:import', self.namespaces):
            schema_location = import_elem.get('schemaLocation')
            if schema_location and base_dir:
                import_path = os.path.join(base_dir, schema_location)
                if os.path.exists(import_path) and import_path not in self.xsd_dependencies:
                    try:
                        import_tree = ET.parse(import_path)
                        import_root = import_tree.getroot()
                        self.xsd_dependencies[import_path] = import_root
                        self.logger.info(f"✅ Loaded XSD import: {schema_location}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to load XSD import {schema_location}: {str(e)}")
    
    def _build_type_registry(self, wsdl_root: ET.Element):
        """Build comprehensive type registry from all sources"""
        # Register types from main WSDL
        self._register_types_from_root(wsdl_root)
        
        # Register types from XSD dependencies
        for xsd_file, xsd_root in self.xsd_dependencies.items():
            self._register_types_from_root(xsd_root, source_file=xsd_file)
    
    def _register_types_from_root(self, root: ET.Element, source_file: str = None):
        """Register all types from a root element"""
        # Register complex types
        for complex_type in root.findall('.//xsd:complexType', self.namespaces):
            type_name = complex_type.get('name')
            if type_name:
                qualified_name = self._get_qualified_name(root, type_name)
                self.type_registry[qualified_name] = {
                    'element': complex_type,
                    'root': root,
                    'source_file': source_file,
                    'type': 'complex'
                }
        
        # Register simple types
        for simple_type in root.findall('.//xsd:simpleType', self.namespaces):
            type_name = simple_type.get('name')
            if type_name:
                qualified_name = self._get_qualified_name(root, type_name)
                self.type_registry[qualified_name] = {
                    'element': simple_type,
                    'root': root,
                    'source_file': source_file,
                    'type': 'simple'
                }
        
        # Register elements
        for element in root.findall('.//xsd:element', self.namespaces):
            element_name = element.get('name')
            if element_name:
                qualified_name = self._get_qualified_name(root, element_name)
                self.type_registry[qualified_name] = {
                    'element': element,
                    'root': root,
                    'source_file': source_file,
                    'type': 'element'
                }
    
    def _get_qualified_name(self, root: ET.Element, type_name: str) -> QualifiedName:
        """Get qualified name using Java-inspired namespace resolution"""
        namespace_uri = ''
        
        if ':' in type_name:
            prefix = type_name.split(':', 1)[0]
            # Look for namespace declaration
            for attr_name, attr_value in root.attrib.items():
                if attr_name.startswith('xmlns') and (
                    attr_name == f'xmlns:{prefix}' or 
                    (prefix == 'tns' and attr_name == 'xmlns')
                ):
                    namespace_uri = attr_value
                    break
        
        if not namespace_uri:
            namespace_uri = root.get('targetNamespace', '')
        
        local_name = type_name.split(':', 1)[-1] if ':' in type_name else type_name
        
        return QualifiedName(namespace_uri, local_name)
    
    def _extract_wsdl_info(self, wsdl_root: ET.Element) -> Dict[str, Any]:
        """Extract comprehensive WSDL information"""
        return {
            'name': self._extract_service_name(wsdl_root),
            'target_namespace': wsdl_root.get('targetNamespace', ''),
            'services': self._extract_services(wsdl_root),
            'port_types': self._extract_port_types(wsdl_root),
            'bindings': self._extract_bindings(wsdl_root),
            'messages': self._extract_messages(wsdl_root),
            'types': self._extract_types_info(wsdl_root),
            'endpoints': self._extract_endpoints(wsdl_root)
        }
    
    def _extract_service_name(self, root: ET.Element) -> str:
        """Extract service name"""
        service = root.find('.//wsdl:service', self.namespaces)
        return service.get('name', 'UnknownService') if service is not None else 'UnknownService'
    
    def _extract_services(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract service information"""
        services = []
        for service in root.findall('.//wsdl:service', self.namespaces):
            service_info = {
                'name': service.get('name', ''),
                'ports': []
            }
            
            for port in service.findall('.//wsdl:port', self.namespaces):
                port_info = {
                    'name': port.get('name', ''),
                    'binding': port.get('binding', ''),
                    'address': self._extract_port_address(port)
                }
                service_info['ports'].append(port_info)
            
            services.append(service_info)
        
        return services
    
    def _extract_port_address(self, port: ET.Element) -> str:
        """Extract SOAP address from port"""
        address_elem = port.find('.//soap:address', self.namespaces)
        if address_elem is None:
            address_elem = port.find('.//soap12:address', self.namespaces)
        
        return address_elem.get('location', '') if address_elem is not None else ''
    
    def _extract_port_types(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract port type information with operations"""
        port_types = []
        
        for port_type in root.findall('.//wsdl:portType', self.namespaces):
            port_type_info = {
                'name': port_type.get('name', ''),
                'operations': self._extract_operations(port_type)
            }
            port_types.append(port_type_info)
        
        return port_types
    
    def _extract_operations(self, port_type: ET.Element) -> List[Dict[str, Any]]:
        """Extract operations from port type"""
        operations = []
        
        for operation in port_type.findall('.//wsdl:operation', self.namespaces):
            op_info = {
                'name': operation.get('name', ''),
                'input': self._extract_message_ref(operation.find('.//wsdl:input', self.namespaces)),
                'output': self._extract_message_ref(operation.find('.//wsdl:output', self.namespaces)),
                'faults': self._extract_faults(operation)
            }
            operations.append(op_info)
        
        return operations
    
    def _extract_message_ref(self, message_elem: Optional[ET.Element]) -> Optional[str]:
        """Extract message reference"""
        return message_elem.get('message', '') if message_elem is not None else None
    
    def _extract_faults(self, operation: ET.Element) -> List[str]:
        """Extract fault messages from operation"""
        faults = []
        for fault in operation.findall('.//wsdl:fault', self.namespaces):
            fault_msg = fault.get('message', '')
            if fault_msg:
                faults.append(fault_msg)
        return faults
    
    def _extract_bindings(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract binding information"""
        bindings = []
        
        for binding in root.findall('.//wsdl:binding', self.namespaces):
            binding_info = {
                'name': binding.get('name', ''),
                'type': binding.get('type', ''),
                'soap_binding': self._extract_soap_binding(binding),
                'operations': self._extract_binding_operations(binding)
            }
            bindings.append(binding_info)
        
        return bindings
    
    def _extract_soap_binding(self, binding: ET.Element) -> Dict[str, Any]:
        """Extract SOAP binding details"""
        soap_binding = binding.find('.//soap:binding', self.namespaces)
        if soap_binding is None:
            soap_binding = binding.find('.//soap12:binding', self.namespaces)
        
        if soap_binding is not None:
            return {
                'style': soap_binding.get('style', 'document'),
                'transport': soap_binding.get('transport', '')
            }
        
        return {}
    
    def _extract_binding_operations(self, binding: ET.Element) -> List[Dict[str, Any]]:
        """Extract binding operations"""
        operations = []
        
        for operation in binding.findall('.//wsdl:operation', self.namespaces):
            op_info = {
                'name': operation.get('name', ''),
                'soap_operation': self._extract_soap_operation(operation),
                'input': self._extract_soap_body(operation.find('.//wsdl:input', self.namespaces)),
                'output': self._extract_soap_body(operation.find('.//wsdl:output', self.namespaces))
            }
            operations.append(op_info)
        
        return operations
    
    def _extract_soap_operation(self, operation: ET.Element) -> Dict[str, Any]:
        """Extract SOAP operation details"""
        soap_op = operation.find('.//soap:operation', self.namespaces)
        if soap_op is None:
            soap_op = operation.find('.//soap12:operation', self.namespaces)
        
        if soap_op is not None:
            return {
                'soap_action': soap_op.get('soapAction', ''),
                'style': soap_op.get('style', 'document')
            }
        
        return {}
    
    def _extract_soap_body(self, body_elem: Optional[ET.Element]) -> Dict[str, Any]:
        """Extract SOAP body details"""
        if body_elem is None:
            return {}
        
        soap_body = body_elem.find('.//soap:body', self.namespaces)
        if soap_body is None:
            soap_body = body_elem.find('.//soap12:body', self.namespaces)
        
        if soap_body is not None:
            return {
                'use': soap_body.get('use', 'literal'),
                'namespace': soap_body.get('namespace', ''),
                'parts': soap_body.get('parts', '')
            }
        
        return {}
    
    def _extract_messages(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract message definitions with detailed parts"""
        messages = []
        
        for message in root.findall('.//wsdl:message', self.namespaces):
            message_info = {
                'name': message.get('name', ''),
                'parts': self._extract_message_parts(message)
            }
            messages.append(message_info)
        
        return messages
    
    def _extract_message_parts(self, message: ET.Element) -> List[Dict[str, Any]]:
        """Extract message parts with type information"""
        parts = []
        
        for part in message.findall('.//wsdl:part', self.namespaces):
            part_info = {
                'name': part.get('name', ''),
                'element': part.get('element', ''),
                'type': part.get('type', ''),
                'schema_details': self._resolve_type_schema(part.get('element', '') or part.get('type', ''))
            }
            parts.append(part_info)
        
        return parts
    
    def _resolve_type_schema(self, type_ref: str) -> Dict[str, Any]:
        """Resolve type reference to detailed schema information"""
        if not type_ref:
            return {}
        
        # Create qualified name for lookup
        qualified_name = self._get_qualified_name_from_ref(type_ref)
        
        if qualified_name in self.type_registry:
            type_info = self.type_registry[qualified_name]
            return self._extract_detailed_schema(type_info['element'], type_info['root'])
        
        return {}
    
    def _get_qualified_name_from_ref(self, type_ref: str) -> QualifiedName:
        """Get qualified name from type reference"""
        # This is a simplified version - in practice, you'd need to resolve the namespace
        # based on the context where the reference appears
        if ':' in type_ref:
            prefix, local_name = type_ref.split(':', 1)
            # For now, use empty namespace - this should be improved with proper context
            return QualifiedName('', local_name)
        else:
            return QualifiedName('', type_ref)
    
    def _extract_detailed_schema(self, element: ET.Element, root: ET.Element) -> Dict[str, Any]:
        """Extract detailed schema information with Java-inspired patterns"""
        context = TypeContext(
            processing_stack=[],
            visited_types=set(),
            depth=0,
            max_depth=10
        )
        
        return self._extract_complex_type_details(element, root, context)
    
    def _extract_complex_type_details(self, element: ET.Element, root: ET.Element, context: TypeContext) -> Dict[str, Any]:
        """Extract complex type details with circular reference protection"""
        type_name = element.get('name', '')
        if not type_name:
            return {}
        
        qualified_name = self._get_qualified_name(root, type_name)
        
        # Check for circular reference using Java-inspired qualified name approach
        if qualified_name in context.visited_types:
            self.logger.warning(f"⚠️ Circular reference detected: {qualified_name}")
            return {'circular_reference': True, 'type_name': str(qualified_name)}
        
        # Check depth limit
        if context.depth >= context.max_depth:
            self.logger.warning(f"⚠️ Maximum depth reached for type: {qualified_name}")
            return {'max_depth_reached': True, 'type_name': str(qualified_name)}
        
        # Add to visited types
        context.visited_types.add(qualified_name)
        context.processing_stack.append(qualified_name)
        context.depth += 1
        
        try:
            details = {
                'name': type_name,
                'qualified_name': str(qualified_name),
                'attributes': [],
                'elements': [],
                'sequences': [],
                'nested_attributes': [],
                'inherited_attributes': []
            }
            
            # Process inheritance (xsd:extension)
            self._process_inheritance(element, root, context, details)
            
            # Process complex content
            self._process_complex_content(element, root, context, details)
            
            return details
            
        finally:
            # Clean up context
            context.visited_types.discard(qualified_name)
            if context.processing_stack and context.processing_stack[-1] == qualified_name:
                context.processing_stack.pop()
            context.depth -= 1
    
    def _process_inheritance(self, element: ET.Element, root: ET.Element, context: TypeContext, details: Dict[str, Any]):
        """Process inheritance with cross-namespace support"""
        for complex_content in element.findall('.//xsd:complexContent', self.namespaces):
            for extension in complex_content.findall('.//xsd:extension', self.namespaces):
                base_type = extension.get('base', '')
                if base_type and ':' in base_type:
                    self._process_base_type(base_type, root, context, details)
    
    def _process_base_type(self, base_type: str, root: ET.Element, context: TypeContext, details: Dict[str, Any]):
        """Process base type with cross-namespace inheritance support"""
        prefix, base_type_name = base_type.split(':', 1)
        base_qualified_name = self._get_qualified_name(root, base_type)
        
        # Check for cross-namespace inheritance
        if self._is_cross_namespace_inheritance(base_type_name, base_type):
            self.logger.info(f"🔗 Cross-namespace inheritance: {base_type_name} -> {base_type}")
            # Use fresh context for cross-namespace inheritance
            fresh_context = TypeContext(
                processing_stack=[],
                visited_types=set(),
                depth=0,
                max_depth=context.max_depth
            )
            self._process_inherited_type(base_qualified_name, fresh_context, details)
        else:
            self._process_inherited_type(base_qualified_name, context, details)
    
    def _is_cross_namespace_inheritance(self, type_name: str, base_type: str) -> bool:
        """Check for cross-namespace inheritance (Java-inspired pattern)"""
        if ':' not in type_name or ':' not in base_type:
            return False
        
        type_prefix, type_local = type_name.split(':', 1)
        base_prefix, base_local = base_type.split(':', 1)
        
        return type_local == base_local and type_prefix != base_prefix
    
    def _process_inherited_type(self, qualified_name: QualifiedName, context: TypeContext, details: Dict[str, Any]):
        """Process inherited type details"""
        if qualified_name in self.type_registry:
            type_info = self.type_registry[qualified_name]
            base_details = self._extract_complex_type_details(
                type_info['element'], 
                type_info['root'], 
                context
            )
            
            # Merge inherited attributes
            details['inherited_attributes'].extend(base_details.get('attributes', []))
            details['attributes'].extend(base_details.get('attributes', []))
            details['nested_attributes'].extend(base_details.get('nested_attributes', []))
    
    def _process_complex_content(self, element: ET.Element, root: ET.Element, context: TypeContext, details: Dict[str, Any]):
        """Process complex content (sequences, choices, etc.)"""
        # Process sequences
        for sequence in element.findall('.//xsd:sequence', self.namespaces):
            sequence_elements = self._extract_sequence_elements(sequence, root, context)
            details['sequences'].extend(sequence_elements)
            details['elements'].extend(sequence_elements)
        
        # Process choices
        for choice in element.findall('.//xsd:choice', self.namespaces):
            choice_elements = self._extract_choice_elements(choice, root, context)
            details['elements'].extend(choice_elements)
        
        # Process all groups
        for all_group in element.findall('.//xsd:all', self.namespaces):
            all_elements = self._extract_all_elements(all_group, root, context)
            details['elements'].extend(all_elements)
    
    def _extract_sequence_elements(self, sequence: ET.Element, root: ET.Element, context: TypeContext) -> List[Dict[str, Any]]:
        """Extract elements from sequence"""
        elements = []
        for element in sequence.findall('.//xsd:element', self.namespaces):
            element_info = self._extract_element_info(element, root, context)
            if element_info:
                elements.append(element_info)
        return elements
    
    def _extract_choice_elements(self, choice: ET.Element, root: ET.Element, context: TypeContext) -> List[Dict[str, Any]]:
        """Extract elements from choice"""
        elements = []
        for element in choice.findall('.//xsd:element', self.namespaces):
            element_info = self._extract_element_info(element, root, context)
            if element_info:
                element_info['choice_group'] = True
                elements.append(element_info)
        return elements
    
    def _extract_all_elements(self, all_group: ET.Element, root: ET.Element, context: TypeContext) -> List[Dict[str, Any]]:
        """Extract elements from all group"""
        elements = []
        for element in all_group.findall('.//xsd:element', self.namespaces):
            element_info = self._extract_element_info(element, root, context)
            if element_info:
                element_info['all_group'] = True
                elements.append(element_info)
        return elements
    
    def _extract_element_info(self, element: ET.Element, root: ET.Element, context: TypeContext) -> Dict[str, Any]:
        """Extract detailed element information"""
        element_name = element.get('name', '')
        element_type = element.get('type', '')
        
        if not element_name:
            return {}
        
        element_info = {
            'name': element_name,
            'type': element_type,
            'min_occurs': element.get('minOccurs', '1'),
            'max_occurs': element.get('maxOccurs', '1'),
            'nillable': element.get('nillable', 'false'),
            'description': f"Element: {element_name}"
        }
        
        # Resolve type details if it's a complex type
        if element_type and ':' in element_type:
            type_details = self._resolve_type_schema(element_type)
            if type_details:
                element_info['type_details'] = type_details
                element_info['nested_attributes'] = type_details.get('nested_attributes', [])
        
        return element_info
    
    def _extract_types_info(self, root: ET.Element) -> Dict[str, Any]:
        """Extract comprehensive types information"""
        return {
            'complex_types': self._extract_complex_types(root),
            'simple_types': self._extract_simple_types(root),
            'elements': self._extract_global_elements(root),
            'type_registry_size': len(self.type_registry)
        }
    
    def _extract_complex_types(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract complex types with full details"""
        complex_types = []
        
        for qualified_name, type_info in self.type_registry.items():
            if type_info['type'] == 'complex':
                context = TypeContext(
                    processing_stack=[],
                    visited_types=set(),
                    depth=0,
                    max_depth=10
                )
                
                type_details = self._extract_complex_type_details(
                    type_info['element'],
                    type_info['root'],
                    context
                )
                
                type_details['source_file'] = type_info['source_file']
                complex_types.append(type_details)
        
        return complex_types
    
    def _extract_simple_types(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract simple types"""
        simple_types = []
        
        for qualified_name, type_info in self.type_registry.items():
            if type_info['type'] == 'simple':
                simple_type = {
                    'name': type_info['element'].get('name', ''),
                    'qualified_name': str(qualified_name),
                    'source_file': type_info['source_file']
                }
                simple_types.append(simple_type)
        
        return simple_types
    
    def _extract_global_elements(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract global elements"""
        global_elements = []
        
        for qualified_name, type_info in self.type_registry.items():
            if type_info['type'] == 'element':
                element = {
                    'name': type_info['element'].get('name', ''),
                    'qualified_name': str(qualified_name),
                    'type': type_info['element'].get('type', ''),
                    'source_file': type_info['source_file']
                }
                global_elements.append(element)
        
        return global_elements
    
    def _extract_endpoints(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract endpoints with detailed request/response information"""
        endpoints = []
        
        # Extract from services and port types
        services = self._extract_services(root)
        port_types = self._extract_port_types(root)
        
        for service in services:
            for port in service['ports']:
                # Find corresponding port type
                port_type = next(
                    (pt for pt in port_types if pt['name'] in port['binding']), 
                    None
                )
                
                if port_type:
                    for operation in port_type['operations']:
                        endpoint = {
                            'path': f"/{service['name']}/{operation['name']}",
                            'method': 'POST',
                            'summary': f"SOAP operation: {operation['name']}",
                            'description': f"SOAP operation {operation['name']}",
                            'operation_name': operation['name'],
                            'soap_action': self._get_soap_action(operation['name'], root),
                            'request': self._build_request_structure(operation['input'], root),
                            'response': self._build_response_structure(operation['output'], root),
                            'faults': operation['faults']
                        }
                        endpoints.append(endpoint)
        
        return endpoints
    
    def _get_soap_action(self, operation_name: str, root: ET.Element) -> str:
        """Get SOAP action for operation"""
        # This would need to be extracted from bindings
        return f"urn:{operation_name}"
    
    def _build_request_structure(self, input_msg: Optional[str], root: ET.Element) -> Dict[str, Any]:
        """Build detailed request structure"""
        if not input_msg:
            return {'message_name': '', 'all_attributes': []}
        
        # Find message definition
        message = root.find(f'.//wsdl:message[@name="{input_msg}"]', self.namespaces)
        if message is None:
            return {'message_name': input_msg, 'all_attributes': []}
        
        return {
            'message_name': input_msg,
            'all_attributes': self._extract_message_parts(message)
        }
    
    def _build_response_structure(self, output_msg: Optional[str], root: ET.Element) -> Dict[str, Any]:
        """Build detailed response structure"""
        if not output_msg:
            return {'message_name': '', 'all_attributes': []}
        
        # Find message definition
        message = root.find(f'.//wsdl:message[@name="{output_msg}"]', self.namespaces)
        if message is None:
            return {'message_name': output_msg, 'all_attributes': []}
        
        return {
            'message_name': output_msg,
            'all_attributes': self._extract_message_parts(message)
        }
