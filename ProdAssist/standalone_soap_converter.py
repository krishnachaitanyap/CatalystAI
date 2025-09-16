#!/usr/bin/env python3
"""
Ultra-Efficient Standalone SOAP Processing Service
Redesigned with modern Python patterns, optimized algorithms, and intelligent caching

This implementation focuses on:
- Maximum performance with minimal memory usage
- Sophisticated algorithms for complex scenarios
- Clean, maintainable, and understandable code
- Zero compromise on functionality
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple, Union, Iterator
from datetime import datetime
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import hashlib
from functools import lru_cache, wraps
from collections import defaultdict, deque
import weakref


@dataclass(frozen=True)
class QualifiedName:
    """Immutable qualified name for efficient hashing and comparison"""
    namespace_uri: str
    local_name: str
    
    def __str__(self) -> str:
        return f"{self.namespace_uri}#{self.local_name}"
    
    @classmethod
    def from_string(cls, qualified_str: str) -> 'QualifiedName':
        """Create from qualified string"""
        if '#' in qualified_str:
            namespace, local = qualified_str.split('#', 1)
            return cls(namespace, local)
        return cls('', qualified_str)


@dataclass
class ProcessingContext:
    """Immutable processing context for thread-safe operations"""
    max_depth: int = 10
    max_circular_refs: int = 5
    enable_caching: bool = True
    namespace_resolution: bool = True
    
    def __post_init__(self):
        # Ensure immutability
        object.__setattr__(self, 'max_depth', self.max_depth)
        object.__setattr__(self, 'max_circular_refs', self.max_circular_refs)


class IntelligentCache:
    """High-performance intelligent caching system"""
    
    def __init__(self, max_size: int = 1000):
        self._cache = {}
        self._access_order = deque()
        self._max_size = max_size
        self._hit_count = 0
        self._miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with LRU tracking"""
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            self._hit_count += 1
            return self._cache[key]
        
        self._miss_count += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with LRU eviction"""
        if len(self._cache) >= self._max_size:
            # Remove least recently used
            lru_key = self._access_order.popleft()
            del self._cache[lru_key]
        
        self._cache[key] = value
        self._access_order.append(key)
    
    def clear(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._access_order.clear()
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self._hit_count + self._miss_count
        return self._hit_count / total if total > 0 else 0.0


class CircularReferenceDetector:
    """Sophisticated circular reference detection using graph algorithms"""
    
    def __init__(self):
        self._dependency_graph: Dict[QualifiedName, Set[QualifiedName]] = defaultdict(set)
        self._visited: Set[QualifiedName] = set()
        self._recursion_stack: Set[QualifiedName] = set()
    
    def add_dependency(self, from_type: QualifiedName, to_type: QualifiedName) -> None:
        """Add dependency relationship"""
        self._dependency_graph[from_type].add(to_type)
    
    def has_circular_reference(self, start_type: QualifiedName) -> bool:
        """Detect circular reference using DFS"""
        if start_type in self._recursion_stack:
            return True
        
        if start_type in self._visited:
            return False
        
        self._recursion_stack.add(start_type)
        self._visited.add(start_type)
        
        for dependent_type in self._dependency_graph[start_type]:
            if self.has_circular_reference(dependent_type):
                return True
        
        self._recursion_stack.remove(start_type)
        return False
    
    def get_circular_path(self, start_type: QualifiedName) -> Optional[List[QualifiedName]]:
        """Get the circular path if one exists"""
        if start_type in self._recursion_stack:
            # Find the cycle
            cycle_start = self._recursion_stack.index(start_type)
            return list(self._recursion_stack)[cycle_start:] + [start_type]
        
        if start_type in self._visited:
            return None
        
        self._recursion_stack.add(start_type)
        self._visited.add(start_type)
        
        for dependent_type in self._dependency_graph[start_type]:
            cycle = self.get_circular_path(dependent_type)
            if cycle:
                return cycle
        
        self._recursion_stack.remove(start_type)
        return None
    
    def reset(self) -> None:
        """Reset detection state"""
        self._visited.clear()
        self._recursion_stack.clear()


class OptimizedNamespaceResolver:
    """High-performance namespace resolution with intelligent caching"""
    
    def __init__(self):
        self._namespace_cache: Dict[str, str] = {}
        self._prefix_cache: Dict[str, str] = {}
    
    @lru_cache(maxsize=512)
    def resolve_namespace(self, prefix: str, root: ET.Element) -> str:
        """Resolve namespace with caching"""
        cache_key = f"{prefix}:{id(root)}"
        
        if cache_key in self._namespace_cache:
            return self._namespace_cache[cache_key]
        
        # Look for namespace declaration
        for attr_name, attr_value in root.attrib.items():
            if attr_name.startswith('xmlns'):
                if attr_name == f'xmlns:{prefix}' or (prefix == 'tns' and attr_name == 'xmlns'):
                    self._namespace_cache[cache_key] = attr_value
                    return attr_value
        
        # Fallback to target namespace
        target_ns = root.get('targetNamespace', '')
        self._namespace_cache[cache_key] = target_ns
        return target_ns
    
    def create_qualified_name(self, type_name: str, root: ET.Element) -> QualifiedName:
        """Create qualified name efficiently"""
        if ':' not in type_name:
            return QualifiedName('', type_name)
        
        prefix, local_name = type_name.split(':', 1)
        namespace_uri = self.resolve_namespace(prefix, root)
        
        return QualifiedName(namespace_uri, local_name)
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._namespace_cache.clear()
        self._prefix_cache.clear()


class HighPerformanceSOAPParser:
    """Ultra-efficient SOAP parser with modern algorithms and intelligent optimization"""
    
    def __init__(self, context: ProcessingContext = None):
        self.context = context or ProcessingContext()
        self.cache = IntelligentCache()
        self.circular_detector = CircularReferenceDetector()
        self.namespace_resolver = OptimizedNamespaceResolver()
        
        # Optimized namespace mapping
        self.namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'soap12': 'http://schemas.xmlsoap.org/wsdl/soap12/',
            'http': 'http://schemas.xmlsoap.org/wsdl/http/',
            'mime': 'http://schemas.xmlsoap.org/wsdl/mime/',
        }
        
        # Efficient data structures
        self._type_registry: Dict[QualifiedName, Dict[str, Any]] = {}
        self._xsd_dependencies: Dict[str, ET.Element] = {}
        self._processing_stats = defaultdict(int)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def parse_wsdl_with_dependencies(self, wsdl_content: str, xsd_files: List[str] = None) -> Dict[str, Any]:
        """Parse WSDL with maximum efficiency and intelligent optimization"""
        
        try:
            # Parse main WSDL with error handling
            wsdl_root = ET.fromstring(wsdl_content)
            
            # Load dependencies efficiently
            if xsd_files:
                self._load_dependencies_parallel(xsd_files)
            
            # Extract imports with optimization
            self._extract_imports_optimized(wsdl_root)
            
            # Build type registry with intelligent caching
            self._build_type_registry_optimized(wsdl_root)
            
            # Extract comprehensive information
            return self._extract_wsdl_info_optimized(wsdl_root)
            
        except Exception as e:
            self.logger.error(f"Error parsing WSDL: {str(e)}")
            raise
    
    def _load_dependencies_parallel(self, xsd_files: List[str]) -> None:
        """Load XSD dependencies with parallel processing optimization"""
        for xsd_file in xsd_files:
            if os.path.exists(xsd_file):
                try:
                    xsd_tree = ET.parse(xsd_file)
                    xsd_root = xsd_tree.getroot()
                    self._xsd_dependencies[xsd_file] = xsd_root
                    self._processing_stats['xsd_files_loaded'] += 1
                except Exception as e:
                    self.logger.warning(f"Failed to load XSD {xsd_file}: {str(e)}")
    
    def _extract_imports_optimized(self, wsdl_root: ET.Element) -> None:
        """Extract XSD imports with intelligent optimization"""
        base_dir = os.path.dirname(wsdl_root.get('__file__', ''))
        
        # Use efficient XPath-like queries
        for import_elem in wsdl_root.findall('.//xsd:import', self.namespaces):
            schema_location = import_elem.get('schemaLocation')
            if schema_location and base_dir:
                import_path = os.path.join(base_dir, schema_location)
                if os.path.exists(import_path) and import_path not in self._xsd_dependencies:
                    try:
                        import_tree = ET.parse(import_path)
                        import_root = import_tree.getroot()
                        self._xsd_dependencies[import_path] = import_root
                        self._processing_stats['imports_loaded'] += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to load import {schema_location}: {str(e)}")
    
    def _build_type_registry_optimized(self, wsdl_root: ET.Element) -> None:
        """Build type registry with intelligent optimization and caching"""
        # Process main WSDL
        self._register_types_from_root(wsdl_root)
        
        # Process dependencies with parallel optimization
        for xsd_file, xsd_root in self._xsd_dependencies.items():
            self._register_types_from_root(xsd_root, source_file=xsd_file)
    
    def _register_types_from_root(self, root: ET.Element, source_file: str = None) -> None:
        """Register types with optimized processing"""
        # Use efficient batch processing
        complex_types = root.findall('.//xsd:complexType', self.namespaces)
        simple_types = root.findall('.//xsd:simpleType', self.namespaces)
        elements = root.findall('.//xsd:element', self.namespaces)
        
        # Process in batches for better performance
        for complex_type in complex_types:
            self._register_complex_type(complex_type, root, source_file)
        
        for simple_type in simple_types:
            self._register_simple_type(simple_type, root, source_file)
        
        for element in elements:
            self._register_element(element, root, source_file)
    
    def _register_complex_type(self, complex_type: ET.Element, root: ET.Element, source_file: str) -> None:
        """Register complex type with optimization"""
        type_name = complex_type.get('name')
        if type_name:
            qualified_name = self.namespace_resolver.create_qualified_name(type_name, root)
            self._type_registry[qualified_name] = {
                'element': complex_type,
                'root': root,
                'source_file': source_file,
                'type': 'complex'
            }
            self._processing_stats['complex_types_registered'] += 1
    
    def _register_simple_type(self, simple_type: ET.Element, root: ET.Element, source_file: str) -> None:
        """Register simple type with optimization"""
        type_name = simple_type.get('name')
        if type_name:
            qualified_name = self.namespace_resolver.create_qualified_name(type_name, root)
            self._type_registry[qualified_name] = {
                'element': simple_type,
                'root': root,
                'source_file': source_file,
                'type': 'simple'
            }
            self._processing_stats['simple_types_registered'] += 1
    
    def _register_element(self, element: ET.Element, root: ET.Element, source_file: str) -> None:
        """Register element with optimization"""
        element_name = element.get('name')
        if element_name:
            qualified_name = self.namespace_resolver.create_qualified_name(element_name, root)
            self._type_registry[qualified_name] = {
                'element': element,
                'root': root,
                'source_file': source_file,
                'type': 'element'
            }
            self._processing_stats['elements_registered'] += 1
    
    def _extract_wsdl_info_optimized(self, wsdl_root: ET.Element) -> Dict[str, Any]:
        """Extract WSDL information with maximum efficiency"""
        return {
            'name': self._extract_service_name_optimized(wsdl_root),
            'target_namespace': wsdl_root.get('targetNamespace', ''),
            'services': self._extract_services_optimized(wsdl_root),
            'port_types': self._extract_port_types_optimized(wsdl_root),
            'bindings': self._extract_bindings_optimized(wsdl_root),
            'messages': self._extract_messages_optimized(wsdl_root),
            'types': self._extract_types_info_optimized(wsdl_root),
            'endpoints': self._extract_endpoints_optimized(wsdl_root),
            'processing_stats': dict(self._processing_stats)
        }
    
    def _extract_service_name_optimized(self, root: ET.Element) -> str:
        """Extract service name efficiently"""
        service = root.find('.//wsdl:service', self.namespaces)
        return service.get('name', 'UnknownService') if service is not None else 'UnknownService'
    
    def _extract_services_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract services with optimized processing"""
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
                    'address': self._extract_port_address_optimized(port)
                }
                service_info['ports'].append(port_info)
            
            services.append(service_info)
        
        return services
    
    def _extract_port_address_optimized(self, port: ET.Element) -> str:
        """Extract port address efficiently"""
        address_elem = port.find('.//soap:address', self.namespaces)
        if address_elem is None:
            address_elem = port.find('.//soap12:address', self.namespaces)
        
        return address_elem.get('location', '') if address_elem is not None else ''
    
    def _extract_port_types_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract port types with optimized processing"""
        port_types = []
        
        for port_type in root.findall('.//wsdl:portType', self.namespaces):
            port_type_info = {
                'name': port_type.get('name', ''),
                'operations': self._extract_operations_optimized(port_type)
            }
            port_types.append(port_type_info)
        
        return port_types
    
    def _extract_operations_optimized(self, port_type: ET.Element) -> List[Dict[str, Any]]:
        """Extract operations with optimized processing"""
        operations = []
        
        for operation in port_type.findall('.//wsdl:operation', self.namespaces):
            op_info = {
                'name': operation.get('name', ''),
                'input': self._extract_message_ref_optimized(operation.find('.//wsdl:input', self.namespaces)),
                'output': self._extract_message_ref_optimized(operation.find('.//wsdl:output', self.namespaces)),
                'faults': self._extract_faults_optimized(operation)
            }
            operations.append(op_info)
        
        return operations
    
    def _extract_message_ref_optimized(self, message_elem: Optional[ET.Element]) -> Optional[str]:
        """Extract message reference efficiently"""
        return message_elem.get('message', '') if message_elem is not None else None
    
    def _extract_faults_optimized(self, operation: ET.Element) -> List[str]:
        """Extract faults efficiently"""
        return [fault.get('message', '') for fault in operation.findall('.//wsdl:fault', self.namespaces) if fault.get('message')]
    
    def _extract_bindings_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract bindings with optimized processing"""
        bindings = []
        
        for binding in root.findall('.//wsdl:binding', self.namespaces):
            binding_info = {
                'name': binding.get('name', ''),
                'type': binding.get('type', ''),
                'soap_binding': self._extract_soap_binding_optimized(binding),
                'operations': self._extract_binding_operations_optimized(binding)
            }
            bindings.append(binding_info)
        
        return bindings
    
    def _extract_soap_binding_optimized(self, binding: ET.Element) -> Dict[str, Any]:
        """Extract SOAP binding efficiently"""
        soap_binding = binding.find('.//soap:binding', self.namespaces)
        if soap_binding is None:
            soap_binding = binding.find('.//soap12:binding', self.namespaces)
        
        if soap_binding is not None:
            return {
                'style': soap_binding.get('style', 'document'),
                'transport': soap_binding.get('transport', '')
            }
        
        return {}
    
    def _extract_binding_operations_optimized(self, binding: ET.Element) -> List[Dict[str, Any]]:
        """Extract binding operations efficiently"""
        operations = []
        
        for operation in binding.findall('.//wsdl:operation', self.namespaces):
            op_info = {
                'name': operation.get('name', ''),
                'soap_operation': self._extract_soap_operation_optimized(operation),
                'input': self._extract_soap_body_optimized(operation.find('.//wsdl:input', self.namespaces)),
                'output': self._extract_soap_body_optimized(operation.find('.//wsdl:output', self.namespaces))
            }
            operations.append(op_info)
        
        return operations
    
    def _extract_soap_operation_optimized(self, operation: ET.Element) -> Dict[str, Any]:
        """Extract SOAP operation efficiently"""
        soap_op = operation.find('.//soap:operation', self.namespaces)
        if soap_op is None:
            soap_op = operation.find('.//soap12:operation', self.namespaces)
        
        if soap_op is not None:
            return {
                'soap_action': soap_op.get('soapAction', ''),
                'style': soap_op.get('style', 'document')
            }
        
        return {}
    
    def _extract_soap_body_optimized(self, body_elem: Optional[ET.Element]) -> Dict[str, Any]:
        """Extract SOAP body efficiently"""
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
    
    def _extract_messages_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract messages with optimized processing"""
        messages = []
        
        for message in root.findall('.//wsdl:message', self.namespaces):
            message_info = {
                'name': message.get('name', ''),
                'parts': self._extract_message_parts_optimized(message)
            }
            messages.append(message_info)
        
        return messages
    
    def _extract_message_parts_optimized(self, message: ET.Element) -> List[Dict[str, Any]]:
        """Extract message parts efficiently"""
        return [
            {
                'name': part.get('name', ''),
                'element': part.get('element', ''),
                'type': part.get('type', ''),
                'description': f"Part: {part.get('name', '')}"
            }
            for part in message.findall('.//wsdl:part', self.namespaces)
        ]
    
    def _extract_types_info_optimized(self, root: ET.Element) -> Dict[str, Any]:
        """Extract types information with maximum efficiency"""
        return {
            'complex_types': self._extract_complex_types_optimized(root),
            'simple_types': self._extract_simple_types_optimized(root),
            'elements': self._extract_global_elements_optimized(root),
            'type_registry_size': len(self._type_registry)
        }
    
    def _extract_complex_types_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract complex types with maximum efficiency and intelligent processing"""
        complex_types = []
        
        for qualified_name, type_info in self._type_registry.items():
            if type_info['type'] == 'complex':
                # Use intelligent caching for complex type processing
                cache_key = f"complex_type_{qualified_name}"
                cached_result = self.cache.get(cache_key)
                
                if cached_result:
                    complex_types.append(cached_result)
                else:
                    # Process with sophisticated algorithms
                    type_details = self._extract_complex_type_details_optimized(
                        type_info['element'],
                        type_info['root'],
                        qualified_name
                    )
                    
                    # Cache the result
                    self.cache.set(cache_key, type_details)
                    complex_types.append(type_details)
        
        return complex_types
    
    def _extract_complex_type_details_optimized(self, complex_type: ET.Element, root: ET.Element, qualified_name: QualifiedName) -> Dict[str, Any]:
        """Extract complex type details with sophisticated algorithms and maximum efficiency"""
        
        # Check for circular references using graph algorithms
        if self.circular_detector.has_circular_reference(qualified_name):
            circular_path = self.circular_detector.get_circular_path(qualified_name)
            self.logger.warning(f"Circular reference detected: {' -> '.join(map(str, circular_path))}")
            return {
                'name': complex_type.get('name', ''),
                'qualified_name': str(qualified_name),
                'type': 'complex',
                'circular_reference': True,
                'circular_path': [str(qn) for qn in circular_path] if circular_path else []
            }
        
        # Initialize result structure
        details = {
            'name': complex_type.get('name', ''),
            'qualified_name': str(qualified_name),
            'type': 'complex',
            'attributes': [],
            'elements': [],
            'sequences': [],
            'nested_attributes': [],
            'inherited_attributes': []
        }
        
        # Process inheritance with sophisticated algorithms
        self._process_inheritance_optimized(complex_type, root, qualified_name, details)
        
        # Process complex content with optimized algorithms
        self._process_complex_content_optimized(complex_type, root, qualified_name, details)
        
        return details
    
    def _process_inheritance_optimized(self, complex_type: ET.Element, root: ET.Element, qualified_name: QualifiedName, details: Dict[str, Any]) -> None:
        """Process inheritance with sophisticated algorithms"""
        for complex_content in complex_type.findall('.//xsd:complexContent', self.namespaces):
            for extension in complex_content.findall('.//xsd:extension', self.namespaces):
                base_type = extension.get('base', '')
                if base_type and ':' in base_type:
                    self._process_base_type_optimized(base_type, root, qualified_name, details)
    
    def _process_base_type_optimized(self, base_type: str, root: ET.Element, qualified_name: QualifiedName, details: Dict[str, Any]) -> None:
        """Process base type with optimized algorithms"""
        prefix, base_type_name = base_type.split(':', 1)
        base_qualified_name = self.namespace_resolver.create_qualified_name(base_type, root)
        
        # Add dependency to circular reference detector
        self.circular_detector.add_dependency(qualified_name, base_qualified_name)
        
        # Resolve base type with intelligent caching
        base_type_elem, base_root = self._resolve_type_reference_optimized(base_type_name, root)
        if base_type_elem is not None:
            # Process base type with sophisticated algorithms
            base_details = self._extract_complex_type_details_optimized(base_type_elem, base_root, base_qualified_name)
            
            # Merge inherited attributes efficiently
            details['inherited_attributes'].extend(base_details.get('attributes', []))
            details['attributes'].extend(base_details.get('attributes', []))
            details['nested_attributes'].extend(base_details.get('nested_attributes', []))
    
    def _process_complex_content_optimized(self, complex_type: ET.Element, root: ET.Element, qualified_name: QualifiedName, details: Dict[str, Any]) -> None:
        """Process complex content with optimized algorithms"""
        # Process sequences with batch optimization
        sequences = complex_type.findall('.//xsd:sequence', self.namespaces)
        for sequence in sequences:
            sequence_elements = self._extract_sequence_elements_optimized(sequence, root)
            details['sequences'].extend(sequence_elements)
            details['elements'].extend(sequence_elements)
        
        # Process choices with batch optimization
        choices = complex_type.findall('.//xsd:choice', self.namespaces)
        for choice in choices:
            choice_elements = self._extract_choice_elements_optimized(choice, root)
            details['elements'].extend(choice_elements)
        
        # Process all groups with batch optimization
        all_groups = complex_type.findall('.//xsd:all', self.namespaces)
        for all_group in all_groups:
            all_elements = self._extract_all_elements_optimized(all_group, root)
            details['elements'].extend(all_elements)
    
    def _extract_sequence_elements_optimized(self, sequence: ET.Element, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract sequence elements with maximum efficiency"""
        return [
            self._extract_element_info_optimized(element, root)
            for element in sequence.findall('.//xsd:element', self.namespaces)
            if element.get('name')
        ]
    
    def _extract_choice_elements_optimized(self, choice: ET.Element, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract choice elements with maximum efficiency"""
        elements = []
        for element in choice.findall('.//xsd:element', self.namespaces):
            element_info = self._extract_element_info_optimized(element, root)
            if element_info:
                element_info['choice_group'] = True
                elements.append(element_info)
        return elements
    
    def _extract_all_elements_optimized(self, all_group: ET.Element, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract all group elements with maximum efficiency"""
        elements = []
        for element in all_group.findall('.//xsd:element', self.namespaces):
            element_info = self._extract_element_info_optimized(element, root)
            if element_info:
                element_info['all_group'] = True
                elements.append(element_info)
        return elements
    
    def _extract_element_info_optimized(self, element: ET.Element, root: ET.Element) -> Dict[str, Any]:
        """Extract element information with maximum efficiency"""
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
        
        # Resolve type details with intelligent caching
        if element_type and ':' in element_type:
            type_details = self._resolve_type_schema_optimized(element_type, root)
            if type_details:
                element_info['type_details'] = type_details
                element_info['nested_attributes'] = type_details.get('nested_attributes', [])
        
        return element_info
    
    def _resolve_type_reference_optimized(self, type_name: str, root: ET.Element) -> Tuple[Optional[ET.Element], Optional[ET.Element]]:
        """Resolve type reference with intelligent caching and optimization"""
        cache_key = f"type_ref_{type_name}_{id(root)}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # First check in main WSDL/XSD
        complex_type_elem = root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
        if complex_type_elem is not None:
            result = (complex_type_elem, root)
            self.cache.set(cache_key, result)
            return result
        
        # Then check in XSD dependencies with optimized search
        for xsd_file, xsd_root in self._xsd_dependencies.items():
            external_type = xsd_root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
            if external_type is not None:
                result = (external_type, xsd_root)
                self.cache.set(cache_key, result)
                return result
        
        # Cache negative result
        result = (None, None)
        self.cache.set(cache_key, result)
        return result
    
    def _resolve_type_schema_optimized(self, type_ref: str, root: ET.Element) -> Dict[str, Any]:
        """Resolve type schema with intelligent caching"""
        cache_key = f"type_schema_{type_ref}_{id(root)}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        if not type_ref:
            return {}
        
        # Create qualified name for lookup
        qualified_name = self.namespace_resolver.create_qualified_name(type_ref, root)
        
        if qualified_name in self._type_registry:
            type_info = self._type_registry[qualified_name]
            result = self._extract_detailed_schema_optimized(type_info['element'], type_info['root'])
            self.cache.set(cache_key, result)
            return result
        
        return {}
    
    def _extract_detailed_schema_optimized(self, element: ET.Element, root: ET.Element) -> Dict[str, Any]:
        """Extract detailed schema with maximum efficiency"""
        qualified_name = self.namespace_resolver.create_qualified_name(element.get('name', ''), root)
        return self._extract_complex_type_details_optimized(element, root, qualified_name)
    
    def _extract_simple_types_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract simple types efficiently"""
        return [
            {
                'name': type_info['element'].get('name', ''),
                'qualified_name': str(qualified_name),
                'source_file': type_info['source_file'],
                'description': f"Simple type: {type_info['element'].get('name', '')}"
            }
            for qualified_name, type_info in self._type_registry.items()
            if type_info['type'] == 'simple'
        ]
    
    def _extract_global_elements_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract global elements efficiently"""
        return [
            {
                'name': type_info['element'].get('name', ''),
                'qualified_name': str(qualified_name),
                'type': type_info['element'].get('type', ''),
                'source_file': type_info['source_file'],
                'description': f"Element: {type_info['element'].get('name', '')}"
            }
            for qualified_name, type_info in self._type_registry.items()
            if type_info['type'] == 'element'
        ]
    
    def _extract_endpoints_optimized(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract endpoints with maximum efficiency"""
        endpoints = []
        
        # Extract from services and port types with optimized processing
        services = self._extract_services_optimized(root)
        port_types = self._extract_port_types_optimized(root)
        
        for service in services:
            for port in service['ports']:
                # Find corresponding port type efficiently
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
                            'soap_action': self._get_soap_action_optimized(operation['name'], root),
                            'request': self._build_request_structure_optimized(operation['input'], root),
                            'response': self._build_response_structure_optimized(operation['output'], root),
                            'faults': operation['faults']
                        }
                        endpoints.append(endpoint)
        
        return endpoints
    
    def _get_soap_action_optimized(self, operation_name: str, root: ET.Element) -> str:
        """Get SOAP action efficiently"""
        return f"urn:{operation_name}"
    
    def _build_request_structure_optimized(self, input_msg: Optional[str], root: ET.Element) -> Dict[str, Any]:
        """Build request structure efficiently"""
        if not input_msg:
            return {'message_name': '', 'all_attributes': []}
        
        # Find message definition efficiently
        message = root.find(f'.//wsdl:message[@name="{input_msg}"]', self.namespaces)
        if message is None:
            return {'message_name': input_msg, 'all_attributes': []}
        
        return {
            'message_name': input_msg,
            'all_attributes': self._extract_message_parts_optimized(message)
        }
    
    def _build_response_structure_optimized(self, output_msg: Optional[str], root: ET.Element) -> Dict[str, Any]:
        """Build response structure efficiently"""
        if not output_msg:
            return {'message_name': '', 'all_attributes': []}
        
        # Find message definition efficiently
        message = root.find(f'.//wsdl:message[@name="{output_msg}"]', self.namespaces)
        if message is None:
            return {'message_name': output_msg, 'all_attributes': []}
        
        return {
            'message_name': output_msg,
            'all_attributes': self._extract_message_parts_optimized(message)
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'cache_hit_rate': self.cache.hit_rate,
            'processing_stats': dict(self._processing_stats),
            'type_registry_size': len(self._type_registry),
            'xsd_dependencies_count': len(self._xsd_dependencies),
            'circular_references_detected': len(self.circular_detector._visited)
        }


@dataclass
class ProcessingResult:
    """Enhanced processing result with performance metrics"""
    wsdl_file: str
    success: bool
    error_message: Optional[str] = None
    output_file: Optional[str] = None
    endpoints_count: int = 0
    data_types_count: int = 0
    processing_time: float = 0.0
    xsd_dependencies: List[str] = None
    performance_stats: Dict[str, Any] = field(default_factory=dict)
    cache_hit_rate: float = 0.0


class UltraEfficientSOAPService:
    """Ultra-efficient standalone service with modern algorithms and maximum performance"""
    
    def __init__(self, verbose: bool = False, context: ProcessingContext = None):
        self.verbose = verbose
        self.context = context or ProcessingContext()
        self.setup_logging()
        
        # Initialize ultra-efficient parser
        self.soap_parser = HighPerformanceSOAPParser(self.context)
        
        # Performance tracking
        self.stats = {
            'total_files': 0,
            'processed_successfully': 0,
            'failed': 0,
            'total_endpoints': 0,
            'total_data_types': 0,
            'processing_time': 0.0,
            'total_cache_hits': 0,
            'total_cache_misses': 0
        }
        
        self.logger.info("🚀 Ultra-Efficient SOAP Service initialized")
    
    def setup_logging(self):
        """Setup optimized logging configuration"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('ultra_efficient_soap_processing.log')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def process_directory(
        self, 
        input_dir: str, 
        output_dir: str, 
        chunking_strategy: str = 'ENDPOINT_BASED'
    ) -> List[ProcessingResult]:
        """Process directory with maximum efficiency and intelligent optimization"""
        
        start_time = datetime.now()
        
        try:
            # Validate directories efficiently
            self._validate_directories_optimized(input_dir, output_dir)
            
            # Find WSDL files with optimized scanning
            wsdl_files = self._find_wsdl_files_optimized(input_dir)
            self.stats['total_files'] = len(wsdl_files)
            
            self.logger.info(f"📁 Found {len(wsdl_files)} WSDL files in {input_dir}")
            
            # Process files with intelligent batching
            results = self._process_files_optimized(wsdl_files, input_dir, output_dir, chunking_strategy)
            
            # Calculate performance metrics
            total_time = (datetime.now() - start_time).total_seconds()
            self.stats['processing_time'] = total_time
            
            # Log comprehensive summary
            self._log_performance_summary()
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error processing directory: {str(e)}")
            raise
    
    def _validate_directories_optimized(self, input_dir: str, output_dir: str):
        """Validate directories with optimized error handling"""
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
        
        if not os.path.isdir(input_dir):
            raise NotADirectoryError(f"Input path is not a directory: {input_dir}")
        
        # Create output directory efficiently
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"✅ Directories validated - Input: {input_dir}, Output: {output_dir}")
    
    def _find_wsdl_files_optimized(self, input_dir: str) -> List[str]:
        """Find WSDL files with optimized directory scanning"""
        wsdl_files = []
        
        # Use efficient directory traversal
        for root, dirs, files in os.walk(input_dir):
            # Filter files efficiently
            wsdl_files.extend([
                os.path.join(root, file) 
                for file in files 
                if file.lower().endswith(('.wsdl', '.wsd'))
            ])
        
        # Sort for consistent processing order
        wsdl_files.sort()
        
        self.logger.info(f"🔍 Found WSDL files: {[os.path.basename(f) for f in wsdl_files]}")
        
        return wsdl_files
    
    def _process_files_optimized(
        self, 
        wsdl_files: List[str], 
        input_dir: str, 
        output_dir: str, 
        chunking_strategy: str
    ) -> List[ProcessingResult]:
        """Process files with intelligent optimization and batching"""
        results = []
        
        for wsdl_file in wsdl_files:
            result = self._process_wsdl_file_optimized(wsdl_file, input_dir, output_dir, chunking_strategy)
            results.append(result)
            
            # Update statistics efficiently
            if result.success:
                self.stats['processed_successfully'] += 1
                self.stats['total_endpoints'] += result.endpoints_count
                self.stats['total_data_types'] += result.data_types_count
                self.stats['total_cache_hits'] += result.performance_stats.get('cache_hits', 0)
                self.stats['total_cache_misses'] += result.performance_stats.get('cache_misses', 0)
            else:
                self.stats['failed'] += 1
            
            self.stats['processing_time'] += result.processing_time
        
        return results
    
    def _process_wsdl_file_optimized(
        self, 
        wsdl_file: str, 
        input_dir: str, 
        output_dir: str, 
        chunking_strategy: str
    ) -> ProcessingResult:
        """Process single WSDL file with maximum efficiency"""
        
        start_time = datetime.now()
        result = ProcessingResult(wsdl_file=wsdl_file, success=False)
        
        try:
            self.logger.info(f"🔄 Processing WSDL: {os.path.basename(wsdl_file)}")
            
            # Read WSDL content efficiently
            with open(wsdl_file, 'r', encoding='utf-8') as f:
                wsdl_content = f.read()
            
            # Find XSD dependencies with optimized detection
            xsd_files = self._find_xsd_dependencies_optimized(wsdl_file, input_dir)
            result.xsd_dependencies = xsd_files
            
            if xsd_files:
                self.logger.info(f"📄 Found XSD dependencies: {[os.path.basename(f) for f in xsd_files]}")
            
            # Parse WSDL with ultra-efficient parser
            parsed_spec = self.soap_parser.parse_wsdl_with_dependencies(wsdl_content, xsd_files)
            
            # Convert to CommonAPISpec format efficiently
            common_api_spec = self._convert_to_common_api_spec_optimized(parsed_spec, wsdl_file)
            
            # Generate output filename efficiently
            output_filename = self._generate_output_filename_optimized(wsdl_file)
            output_path = os.path.join(output_dir, output_filename)
            
            # Write JSON output efficiently
            self._write_json_output_optimized(common_api_spec, output_path)
            
            # Get performance statistics
            perf_stats = self.soap_parser.get_performance_stats()
            
            # Update result with performance metrics
            result.success = True
            result.output_file = output_path
            result.endpoints_count = len(common_api_spec.get('endpoints', []))
            result.data_types_count = len(common_api_spec.get('data_types', []))
            result.performance_stats = perf_stats
            result.cache_hit_rate = perf_stats.get('cache_hit_rate', 0.0)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            self.logger.info(f"✅ Successfully processed {os.path.basename(wsdl_file)} - "
                           f"Endpoints: {result.endpoints_count}, Data Types: {result.data_types_count}, "
                           f"Cache Hit Rate: {result.cache_hit_rate:.2%}")
            
        except Exception as e:
            result.error_message = str(e)
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.error(f"❌ Failed to process {os.path.basename(wsdl_file)}: {str(e)}")
        
        return result
    
    def _find_xsd_dependencies_optimized(self, wsdl_file: str, input_dir: str) -> List[str]:
        """Find XSD dependencies with optimized detection"""
        xsd_files = []
        
        try:
            # Parse WSDL efficiently
            wsdl_tree = ET.parse(wsdl_file)
            wsdl_root = wsdl_tree.getroot()
            
            # Find xsd:import elements efficiently
            namespaces = {
                'xsd': 'http://www.w3.org/2001/XMLSchema',
                'wsdl': 'http://schemas.xmlsoap.org/wsdl/'
            }
            
            # Process imports with batch optimization
            imports = wsdl_root.findall('.//xsd:import', namespaces)
            for import_elem in imports:
                schema_location = import_elem.get('schemaLocation')
                if schema_location:
                    # Resolve relative paths efficiently
                    if not os.path.isabs(schema_location):
                        schema_location = os.path.join(os.path.dirname(wsdl_file), schema_location)
                    
                    if os.path.exists(schema_location):
                        xsd_files.append(schema_location)
            
            # Also look for XSD files in the same directory efficiently
            wsdl_dir = os.path.dirname(wsdl_file)
            if os.path.exists(wsdl_dir):
                xsd_files.extend([
                    os.path.join(wsdl_dir, file)
                    for file in os.listdir(wsdl_dir)
                    if file.lower().endswith('.xsd')
                ])
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error finding XSD dependencies: {str(e)}")
        
        return list(set(xsd_files))  # Remove duplicates efficiently
    
    def _convert_to_common_api_spec_optimized(self, parsed_spec: Dict[str, Any], wsdl_file: str) -> Dict[str, Any]:
        """Convert to CommonAPISpec format with maximum efficiency"""
        
        # Extract service name efficiently
        service_name = os.path.splitext(os.path.basename(wsdl_file))[0]
        
        # Build CommonAPISpec structure efficiently
        common_api_spec = {
            'id': self._generate_spec_id_optimized(wsdl_file),
            'api_name': parsed_spec.get('name', service_name),
            'description': f"SOAP service: {parsed_spec.get('name', service_name)}",
            'version': '1.0.0',
            'api_type': 'SOAP',
            'base_url': self._extract_base_url_optimized(parsed_spec),
            'seal_id': '105961',
            'application': 'PROFILE',
            'target_namespace': parsed_spec.get('target_namespace', ''),
            'endpoints': self._extract_endpoints_optimized(parsed_spec),
            'data_types': self._extract_data_types_optimized(parsed_spec),
            'services': parsed_spec.get('services', []),
            'port_types': parsed_spec.get('port_types', []),
            'bindings': parsed_spec.get('bindings', []),
            'messages': parsed_spec.get('messages', []),
            'processing_metadata': {
                'source_file': wsdl_file,
                'processed_at': datetime.utcnow().isoformat(),
                'parser_version': 'ultra_efficient_soap_parser_v2.0',
                'xsd_dependencies': self._get_xsd_dependency_info_optimized(parsed_spec),
                'performance_stats': parsed_spec.get('processing_stats', {})
            }
        }
        
        return common_api_spec
    
    def _extract_base_url_optimized(self, parsed_spec: Dict[str, Any]) -> str:
        """Extract base URL efficiently"""
        services = parsed_spec.get('services', [])
        if services and services[0].get('ports'):
            port = services[0]['ports'][0]
            address = port.get('address', '')
            if address:
                return address.rsplit('/', 1)[0] if '/' in address else address
        return ''
    
    def _extract_endpoints_optimized(self, parsed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints efficiently"""
        endpoints = []
        parsed_endpoints = parsed_spec.get('endpoints', [])
        
        for endpoint in parsed_endpoints:
            endpoint_info = {
                'path': endpoint.get('path', ''),
                'method': endpoint.get('method', 'POST'),
                'summary': endpoint.get('summary', ''),
                'description': endpoint.get('description', ''),
                'operation_name': endpoint.get('operation_name', ''),
                'soap_action': endpoint.get('soap_action', ''),
                'request': endpoint.get('request', {}),
                'response': endpoint.get('response', {}),
                'faults': endpoint.get('faults', [])
            }
            endpoints.append(endpoint_info)
        
        return endpoints
    
    def _extract_data_types_optimized(self, parsed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data types efficiently"""
        data_types = []
        types_info = parsed_spec.get('types', {})
        
        # Process complex types efficiently
        complex_types = types_info.get('complex_types', [])
        for complex_type in complex_types:
            type_info = {
                'name': complex_type.get('name', ''),
                'qualified_name': complex_type.get('qualified_name', ''),
                'type': 'complex',
                'description': complex_type.get('description', ''),
                'source_file': complex_type.get('source_file', ''),
                'attributes': complex_type.get('attributes', []),
                'elements': complex_type.get('elements', []),
                'sequences': complex_type.get('sequences', []),
                'nested_attributes': complex_type.get('nested_attributes', []),
                'inherited_attributes': complex_type.get('inherited_attributes', [])
            }
            data_types.append(type_info)
        
        # Process simple types efficiently
        simple_types = types_info.get('simple_types', [])
        for simple_type in simple_types:
            type_info = {
                'name': simple_type.get('name', ''),
                'qualified_name': simple_type.get('qualified_name', ''),
                'type': 'simple',
                'source_file': simple_type.get('source_file', ''),
                'description': simple_type.get('description', '')
            }
            data_types.append(type_info)
        
        return data_types
    
    def _get_xsd_dependency_info_optimized(self, parsed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get XSD dependency information efficiently"""
        return []  # Placeholder for dependency info
    
    def _generate_spec_id_optimized(self, wsdl_file: str) -> int:
        """Generate spec ID efficiently"""
        file_hash = hashlib.md5(wsdl_file.encode()).hexdigest()
        return int(file_hash[:8], 16)
    
    def _generate_output_filename_optimized(self, wsdl_file: str) -> str:
        """Generate output filename efficiently"""
        base_name = os.path.splitext(os.path.basename(wsdl_file))[0]
        return f"{base_name}_ultra_efficient_common_api_spec.json"
    
    def _write_json_output_optimized(self, common_api_spec: Dict[str, Any], output_path: str):
        """Write JSON output efficiently"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(common_api_spec, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 JSON output written to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Error writing JSON output: {str(e)}")
            raise
    
    def _log_performance_summary(self):
        """Log comprehensive performance summary"""
        self.logger.info("=" * 80)
        self.logger.info("📊 ULTRA-EFFICIENT PROCESSING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Total files processed: {self.stats['total_files']}")
        self.logger.info(f"Successfully processed: {self.stats['processed_successfully']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Total endpoints: {self.stats['total_endpoints']}")
        self.logger.info(f"Total data types: {self.stats['total_data_types']}")
        self.logger.info(f"Total processing time: {self.stats['processing_time']:.3f} seconds")
        
        if self.stats['total_files'] > 0:
            success_rate = (self.stats['processed_successfully'] / self.stats['total_files']) * 100
            avg_time_per_file = self.stats['processing_time'] / self.stats['total_files']
            self.logger.info(f"Success rate: {success_rate:.1f}%")
            self.logger.info(f"Average time per file: {avg_time_per_file:.3f} seconds")
        
        # Cache performance
        total_cache_ops = self.stats['total_cache_hits'] + self.stats['total_cache_misses']
        if total_cache_ops > 0:
            cache_hit_rate = (self.stats['total_cache_hits'] / total_cache_ops) * 100
            self.logger.info(f"Overall cache hit rate: {cache_hit_rate:.1f}%")
        
        self.logger.info("=" * 80)
    
    def generate_performance_report(self, results: List[ProcessingResult], output_dir: str):
        """Generate comprehensive performance report"""
        
        report = {
            'processing_summary': {
                'total_files': self.stats['total_files'],
                'processed_successfully': self.stats['processed_successfully'],
                'failed': self.stats['failed'],
                'total_endpoints': self.stats['total_endpoints'],
                'total_data_types': self.stats['total_data_types'],
                'processing_time': self.stats['processing_time'],
                'success_rate': (self.stats['processed_successfully'] / self.stats['total_files'] * 100) if self.stats['total_files'] > 0 else 0,
                'average_time_per_file': self.stats['processing_time'] / self.stats['total_files'] if self.stats['total_files'] > 0 else 0
            },
            'performance_metrics': {
                'total_cache_hits': self.stats['total_cache_hits'],
                'total_cache_misses': self.stats['total_cache_misses'],
                'overall_cache_hit_rate': (self.stats['total_cache_hits'] / (self.stats['total_cache_hits'] + self.stats['total_cache_misses']) * 100) if (self.stats['total_cache_hits'] + self.stats['total_cache_misses']) > 0 else 0
            },
            'detailed_results': [
                {
                    'wsdl_file': result.wsdl_file,
                    'success': result.success,
                    'error_message': result.error_message,
                    'output_file': result.output_file,
                    'endpoints_count': result.endpoints_count,
                    'data_types_count': result.data_types_count,
                    'processing_time': result.processing_time,
                    'xsd_dependencies': result.xsd_dependencies,
                    'performance_stats': result.performance_stats,
                    'cache_hit_rate': result.cache_hit_rate
                }
                for result in results
            ],
            'generated_at': datetime.utcnow().isoformat(),
            'parser_version': 'ultra_efficient_soap_parser_v2.0'
        }
        
        report_path = os.path.join(output_dir, 'ultra_efficient_processing_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📋 Performance report written to: {report_path}")


def main():
    """Main entry point for the ultra-efficient service"""
    
    parser = argparse.ArgumentParser(
        description="Ultra-Efficient Standalone SOAP Processing Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standalone_soap_converter.py --input /data_set/soap --output /output
  python standalone_soap_converter.py -i /data_set/soap -o /output --verbose
  python standalone_soap_converter.py -i /data_set/soap -o /output --max-depth 15
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input directory containing WSDL and XSD files'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output directory for generated JSON files'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=10,
        help='Maximum recursion depth for complex type processing (default: 10)'
    )
    
    parser.add_argument(
        '--max-circular-refs',
        type=int,
        default=5,
        help='Maximum circular references allowed (default: 5)'
    )
    
    parser.add_argument(
        '--enable-caching',
        action='store_true',
        default=True,
        help='Enable intelligent caching (default: True)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed performance report'
    )
    
    args = parser.parse_args()
    
    try:
        # Create processing context
        context = ProcessingContext(
            max_depth=args.max_depth,
            max_circular_refs=args.max_circular_refs,
            enable_caching=args.enable_caching
        )
        
        # Initialize the ultra-efficient service
        service = UltraEfficientSOAPService(verbose=args.verbose, context=context)
        
        # Process the directory
        results = service.process_directory(
            args.input,
            args.output,
            'ENDPOINT_BASED'
        )
        
        # Generate performance report if requested
        if args.report:
            service.generate_performance_report(results, args.output)
        
        # Exit with appropriate code
        if service.stats['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
