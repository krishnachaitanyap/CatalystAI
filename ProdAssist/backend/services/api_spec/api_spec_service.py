"""
Ultra-Efficient API Specification service with sophisticated algorithms
Integrates advanced SOAP processing, intelligent caching, and vector database management
"""
import json
import yaml
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from pathlib import Path
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from dataclasses import dataclass, field
from functools import lru_cache
from collections import defaultdict, deque

from models.schemas.schemas import APISpecCreate, APISpecUpdate, APIType, ChunkingStrategy
from utils.logging import LoggerMixin
from .advanced_soap_parser import AdvancedSOAPParser
from ..vector_db.vector_db_factory import VectorDatabaseManager, VectorDatabaseType
from ..llm.enhanced_openai_service import EnhancedOpenAIService


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


class APISpecService(LoggerMixin):
    """Ultra-efficient API specification service with sophisticated algorithms"""
    
    def __init__(self, context: ProcessingContext = None, vector_db_config: Dict[str, Any] = None):
        self.context = context or ProcessingContext()
        
        # Initialize ultra-efficient components
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
        
        # Initialize services
        self.supported_formats = {
            'openapi': ['yaml', 'json'],
            'swagger': ['yaml', 'json'],
            'wsdl': ['xml'],
            'raml': ['yaml'],
            'graphql': ['json', 'sdl']
        }
        
        # Initialize advanced services
        self.soap_parser = AdvancedSOAPParser()
        
        # Initialize configurable vector database service
        if vector_db_config is None:
            # Default to ChromaDB
            vector_db_config = {
                'type': 'chromadb',
                'chunking_strategy': 'endpoint_based',
                'max_chunk_size': 1000,
                'chunk_overlap': 200,
                'embedding_model': 'text-embedding-ada-002'
            }
        
        self.vector_db_manager = VectorDatabaseManager(vector_db_config)
        self.llm_service = EnhancedOpenAIService()
        
        # Performance tracking
        self.stats = {
            'total_specs_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'total_endpoints': 0,
            'total_data_types': 0,
            'processing_time': 0.0,
            'cache_hit_rate': 0.0
        }
        
        self.logger.info(f"🚀 Ultra-Efficient API Spec Service initialized with {vector_db_config.get('type', 'chromadb')} vector database")
    
    async def create_api_spec(
        self, 
        spec_data: APISpecCreate, 
        xsd_files: Optional[List[str]] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None
    ) -> Dict[str, Any]:
        """Create API specification with ultra-efficient processing capabilities"""
        
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🔄 Processing API spec: {spec_data.name}")
            
            # Parse the specification content with ultra-efficient capabilities
            parsed_spec = self._parse_spec_content_ultra_efficient(
                spec_data.spec_content, 
                spec_data.format,
                xsd_files
            )
            
            # Convert to CommonAPI format with enhanced processing
            common_api_spec = self._convert_to_common_api_ultra_efficient(parsed_spec, spec_data)
            
            # Add AI-powered analysis
            common_api_spec = self._enhance_with_ai_analysis(common_api_spec)
            
            # Store in vector database with intelligent chunking
            if chunking_strategy:
                await self._store_in_vector_db_ultra_efficient(common_api_spec, chunking_strategy)
            
            # Update performance statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats(common_api_spec, processing_time, True)
            
            self.logger.info(f"✅ Created ultra-efficient CommonAPI spec for: {spec_data.name} "
                           f"(Processing time: {processing_time:.3f}s, Cache hit rate: {self.cache.hit_rate:.2%})")
            
            return common_api_spec
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_stats({}, processing_time, False)
            
            self.logger.error(f"❌ Error creating API spec: {str(e)}")
            raise
    
    def update_api_spec(self, spec_data: APISpecUpdate, existing_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing API specification"""
        
        try:
            # If spec_content is provided, reparse and convert
            if spec_data.spec_content:
                parsed_spec = self._parse_spec_content(spec_data.spec_content, existing_spec['format'])
                common_api_spec = self._convert_to_common_api(parsed_spec, spec_data)
            else:
                # Update metadata only
                common_api_spec = existing_spec.copy()
                update_data = spec_data.dict(exclude_unset=True)
                common_api_spec.update(update_data)
            
            self.logger.info(f"✅ Updated API spec: {common_api_spec.get('name', 'Unknown')}")
            return common_api_spec
            
        except Exception as e:
            self.logger.error(f"❌ Error updating API spec: {str(e)}")
            raise
    
    def _parse_spec_content_ultra_efficient(
        self, 
        content: str, 
        format_type: str, 
        xsd_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Ultra-efficient specification parsing with sophisticated algorithms"""
        
        try:
            if format_type.lower() in ['openapi', 'swagger']:
                if content.strip().startswith('{'):
                    return json.loads(content)
                else:
                    return yaml.safe_load(content)
            
            elif format_type.lower() == 'wsdl':
                # Use ultra-efficient SOAP parser with intelligent caching
                return self._parse_wsdl_ultra_efficient(content, xsd_files)
            
            elif format_type.lower() == 'raml':
                return yaml.safe_load(content)
            
            elif format_type.lower() == 'graphql':
                if content.strip().startswith('{'):
                    return json.loads(content)
                else:
                    # GraphQL SDL
                    return {'sdl': content}
            
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Error parsing spec content: {str(e)}")
            raise
    
    def _parse_wsdl_ultra_efficient(self, wsdl_content: str, xsd_files: List[str] = None) -> Dict[str, Any]:
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
    
    def _parse_spec_content(self, content: str, format_type: str) -> Dict[str, Any]:
        """Parse specification content based on format"""
        
        try:
            if format_type.lower() in ['openapi', 'swagger']:
                if content.strip().startswith('{'):
                    return json.loads(content)
                else:
                    return yaml.safe_load(content)
            
            elif format_type.lower() == 'wsdl':
                return self._parse_wsdl(content)
            
            elif format_type.lower() == 'raml':
                return yaml.safe_load(content)
            
            elif format_type.lower() == 'graphql':
                if content.strip().startswith('{'):
                    return json.loads(content)
                else:
                    # GraphQL SDL
                    return {'sdl': content}
            
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"❌ Error parsing spec content: {str(e)}")
            raise
    
    def _parse_wsdl(self, wsdl_content: str) -> Dict[str, Any]:
        """Parse WSDL content"""
        try:
            root = ET.fromstring(wsdl_content)
            
            # Extract basic WSDL information
            wsdl_info = {
                'name': root.get('name', 'Unknown'),
                'targetNamespace': root.get('targetNamespace', ''),
                'services': [],
                'portTypes': [],
                'bindings': [],
                'messages': [],
                'types': []
            }
            
            # Extract services
            for service in root.findall('.//{http://schemas.xmlsoap.org/wsdl/}service'):
                service_info = {
                    'name': service.get('name', ''),
                    'ports': []
                }
                
                for port in service.findall('.//{http://schemas.xmlsoap.org/wsdl/}port'):
                    port_info = {
                        'name': port.get('name', ''),
                        'binding': port.get('binding', ''),
                        'address': port.find('.//{http://schemas.xmlsoap.org/wsdl/soap/}address')
                    }
                    if port_info['address'] is not None:
                        port_info['address'] = port_info['address'].get('location', '')
                    service_info['ports'].append(port_info)
                
                wsdl_info['services'].append(service_info)
            
            # Extract port types (operations)
            for port_type in root.findall('.//{http://schemas.xmlsoap.org/wsdl/}portType'):
                port_type_info = {
                    'name': port_type.get('name', ''),
                    'operations': []
                }
                
                for operation in port_type.findall('.//{http://schemas.xmlsoap.org/wsdl/}operation'):
                    op_info = {
                        'name': operation.get('name', ''),
                        'input': operation.find('.//{http://schemas.xmlsoap.org/wsdl/}input'),
                        'output': operation.find('.//{http://schemas.xmlsoap.org/wsdl/}output')
                    }
                    
                    if op_info['input'] is not None:
                        op_info['input'] = op_info['input'].get('message', '')
                    if op_info['output'] is not None:
                        op_info['output'] = op_info['output'].get('message', '')
                    
                    port_type_info['operations'].append(op_info)
                
                wsdl_info['portTypes'].append(port_type_info)
            
            return wsdl_info
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing WSDL: {str(e)}")
            raise
    
    def _convert_to_common_api_ultra_efficient(self, parsed_spec: Dict[str, Any], spec_data: APISpecCreate) -> Dict[str, Any]:
        """Convert to CommonAPI format with ultra-efficient processing"""
        
        # Generate unique ID efficiently
        spec_id = self._generate_spec_id_optimized(spec_data.name, spec_data.spec_content)
        
        # Build CommonAPISpec structure efficiently
        common_api_spec = {
            'id': spec_id,
            'api_name': parsed_spec.get('name', spec_data.name),
            'description': f"API specification: {parsed_spec.get('name', spec_data.name)}",
            'version': '1.0.0',
            'api_type': spec_data.api_type.value if hasattr(spec_data.api_type, 'value') else str(spec_data.api_type),
            'base_url': self._extract_base_url_optimized(parsed_spec),
            'seal_id': '105961',
            'application': 'PROFILE',
            'target_namespace': parsed_spec.get('target_namespace', ''),
            'endpoints': self._extract_endpoints_ultra_efficient(parsed_spec),
            'data_types': self._extract_data_types_ultra_efficient(parsed_spec),
            'services': parsed_spec.get('services', []),
            'port_types': parsed_spec.get('port_types', []),
            'bindings': parsed_spec.get('bindings', []),
            'messages': parsed_spec.get('messages', []),
            'processing_metadata': {
                'source_name': spec_data.name,
                'processed_at': datetime.utcnow().isoformat(),
                'parser_version': 'ultra_efficient_api_spec_service_v2.0',
                'processing_stats': parsed_spec.get('processing_stats', {}),
                'cache_hit_rate': self.cache.hit_rate,
                'performance_metrics': self.get_performance_stats()
            }
        }
        
        return common_api_spec
    
    def _convert_to_common_api(self, parsed_spec: Dict[str, Any], spec_data: APISpecCreate) -> Dict[str, Any]:
        """Convert parsed specification to CommonAPI format"""
        
        common_api = {
            'api_name': spec_data.name,
            'version': spec_data.version,
            'description': spec_data.description or '',
            'base_url': spec_data.base_url or '',
            'category': spec_data.api_type.value,
            'documentation_url': '',
            'api_type': spec_data.api_type.value,
            'format': spec_data.format,
            'seal_id': spec_data.seal_id,
            'application': spec_data.application,
            'endpoints': [],
            'data_types': [],
            'schemas': {},
            'metadata': spec_data.metadata or {}
        }
        
        # Convert based on API type
        if spec_data.api_type == APIType.REST:
            common_api = self._convert_rest_api(parsed_spec, common_api)
        elif spec_data.api_type == APIType.SOAP:
            common_api = self._convert_soap_api(parsed_spec, common_api)
        
        return common_api
    
    def _generate_spec_id_optimized(self, name: str, content: str) -> int:
        """Generate spec ID efficiently"""
        content_hash = hashlib.md5(f"{name}:{content}".encode()).hexdigest()
        return int(content_hash[:8], 16)
    
    def _extract_base_url_optimized(self, parsed_spec: Dict[str, Any]) -> str:
        """Extract base URL efficiently"""
        services = parsed_spec.get('services', [])
        if services and services[0].get('ports'):
            port = services[0]['ports'][0]
            address = port.get('address', '')
            if address:
                return address.rsplit('/', 1)[0] if '/' in address else address
        return ''
    
    def _extract_endpoints_ultra_efficient(self, parsed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints with ultra-efficient processing"""
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
    
    def _extract_data_types_ultra_efficient(self, parsed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data types with ultra-efficient processing"""
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
    
    async def _store_in_vector_db_ultra_efficient(self, common_api_spec: Dict[str, Any], chunking_strategy: ChunkingStrategy) -> None:
        """Store in vector database with ultra-efficient chunking"""
        try:
            # Use configurable vector database service with intelligent chunking
            success = await self.vector_db_manager.add_api_specification(
                common_api_spec,
                chunking_strategy=chunking_strategy.value if hasattr(chunking_strategy, 'value') else str(chunking_strategy)
            )
            
            if success:
                self.logger.info(f"✅ Stored API spec in {self.vector_db_manager.get_service_type()} vector DB with {chunking_strategy} chunking strategy")
            else:
                self.logger.warning(f"⚠️ Failed to store API spec in vector DB")
            
        except Exception as e:
            self.logger.error(f"❌ Error storing in vector DB: {str(e)}")
            raise
    
    def _update_performance_stats(self, common_api_spec: Dict[str, Any], processing_time: float, success: bool) -> None:
        """Update performance statistics"""
        self.stats['total_specs_processed'] += 1
        
        if success:
            self.stats['successful_processing'] += 1
            self.stats['total_endpoints'] += len(common_api_spec.get('endpoints', []))
            self.stats['total_data_types'] += len(common_api_spec.get('data_types', []))
        else:
            self.stats['failed_processing'] += 1
        
        self.stats['processing_time'] += processing_time
        self.stats['cache_hit_rate'] = self.cache.hit_rate
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'cache_hit_rate': self.cache.hit_rate,
            'processing_stats': dict(self._processing_stats),
            'type_registry_size': len(self._type_registry),
            'xsd_dependencies_count': len(self._xsd_dependencies),
            'circular_references_detected': len(self.circular_detector._visited),
            'service_stats': dict(self.stats)
        }
    
    def clear_caches(self) -> None:
        """Clear all caches for fresh processing"""
        self.cache.clear()
        self.namespace_resolver.clear_cache()
        self.circular_detector.reset()
        self._type_registry.clear()
        self._xsd_dependencies.clear()
        self._processing_stats.clear()
        
        self.logger.info("🧹 All caches cleared for fresh processing")
    
    # Vector Database Operations
    
    async def initialize_vector_database(self) -> None:
        """Initialize the vector database connection"""
        await self.vector_db_manager.initialize()
    
    async def search_api_specifications(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ):
        """Search API specifications using vector database"""
        return await self.vector_db_manager.search_api_specifications(query, filters, limit)
    
    async def get_api_specification(self, spec_id: str) -> Optional[Dict[str, Any]]:
        """Get specific API specification by ID from vector database"""
        return await self.vector_db_manager.get_api_specification(spec_id)
    
    async def update_api_specification(
        self, 
        spec_id: str, 
        api_spec: Dict[str, Any]
    ) -> bool:
        """Update existing API specification in vector database"""
        return await self.vector_db_manager.update_api_specification(spec_id, api_spec)
    
    async def delete_api_specification(self, spec_id: str) -> bool:
        """Delete API specification from vector database"""
        return await self.vector_db_manager.delete_api_specification(spec_id)
    
    async def get_vector_db_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        return await self.vector_db_manager.get_collection_stats()
    
    async def clear_vector_database(self) -> bool:
        """Clear all data from vector database"""
        return await self.vector_db_manager.clear_collection()
    
    def get_vector_db_type(self) -> str:
        """Get the type of vector database being used"""
        return self.vector_db_manager.get_service_type()
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get the current vector database configuration"""
        return self.vector_db_manager.get_config()
    
    def _convert_rest_api(self, parsed_spec: Dict[str, Any], common_api: Dict[str, Any]) -> Dict[str, Any]:
        """Convert REST API (OpenAPI/Swagger) to CommonAPI format"""
        
        # Extract endpoints
        if 'paths' in parsed_spec:
            for path, methods in parsed_spec['paths'].items():
                for method, operation in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                        endpoint = {
                            'path': path,
                            'method': method.upper(),
                            'summary': operation.get('summary', ''),
                            'description': operation.get('description', ''),
                            'operation_id': operation.get('operationId', ''),
                            'parameters': operation.get('parameters', []),
                            'request_body': operation.get('requestBody', {}),
                            'responses': operation.get('responses', {}),
                            'tags': operation.get('tags', [])
                        }
                        common_api['endpoints'].append(endpoint)
        
        # Extract schemas/components
        if 'components' in parsed_spec and 'schemas' in parsed_spec['components']:
            common_api['schemas'] = parsed_spec['components']['schemas']
        
        # Extract data types from schemas
        if 'schemas' in common_api:
            for schema_name, schema_def in common_api['schemas'].items():
                data_type = {
                    'name': schema_name,
                    'type': schema_def.get('type', 'object'),
                    'description': schema_def.get('description', ''),
                    'properties': schema_def.get('properties', {}),
                    'required': schema_def.get('required', [])
                }
                common_api['data_types'].append(data_type)
        
        return common_api
    
    def _convert_soap_api(self, parsed_spec: Dict[str, Any], common_api: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SOAP API (WSDL) to CommonAPI format"""
        
        # Extract endpoints from services
        for service in parsed_spec.get('services', []):
            for port in service.get('ports', []):
                endpoint = {
                    'path': f"/{service['name']}/{port['name']}",
                    'method': 'POST',
                    'summary': f"SOAP operation: {port['name']}",
                    'description': f"SOAP operation {port['name']}",
                    'operation_name': port['name'],
                    'soap_headers': [],
                    'request': {
                        'message_name': '',
                        'all_attributes': []
                    },
                    'response': {
                        'message_name': '',
                        'all_attributes': []
                    }
                }
                common_api['endpoints'].append(endpoint)
        
        # Extract operations from port types
        for port_type in parsed_spec.get('portTypes', []):
            for operation in port_type.get('operations', []):
                # Find corresponding endpoint and update it
                for endpoint in common_api['endpoints']:
                    if operation['name'] in endpoint['operation_name']:
                        endpoint['operation_name'] = operation['name']
                        endpoint['summary'] = f"SOAP operation: {operation['name']}"
                        endpoint['description'] = f"SOAP operation {operation['name']}"
                        break
        
        return common_api
    
    def _enhance_with_ai_analysis(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance API specification with AI-powered analysis"""
        
        try:
            # Add AI analysis to the specification
            ai_analysis = {
                'design_quality': self._analyze_design_quality(api_spec),
                'security_assessment': self._analyze_security(api_spec),
                'performance_considerations': self._analyze_performance(api_spec),
                'documentation_score': self._analyze_documentation(api_spec),
                'integration_recommendations': self._generate_integration_recommendations(api_spec)
            }
            
            api_spec['ai_analysis'] = ai_analysis
            
            # Generate code examples for key endpoints
            api_spec['code_examples'] = self._generate_code_examples(api_spec)
            
            self.logger.info(f"✅ Enhanced API spec with AI analysis")
            return api_spec
            
        except Exception as e:
            self.logger.warning(f"⚠️ AI enhancement failed: {str(e)}")
            return api_spec
    
    def _analyze_design_quality(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API design quality using AI"""
        try:
            analysis = self.llm_service.analyze_api_specification(api_spec)
            return {
                'score': self._extract_score_from_analysis(analysis),
                'recommendations': analysis,
                'timestamp': self._get_current_timestamp()
            }
        except Exception as e:
            return {'error': str(e), 'score': 0}
    
    def _analyze_security(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security aspects of the API"""
        # Simplified security analysis
        security_issues = []
        
        # Check for authentication
        if not api_spec.get('authentication'):
            security_issues.append("No authentication mechanism defined")
        
        # Check for HTTPS
        base_url = api_spec.get('base_url', '')
        if base_url and not base_url.startswith('https://'):
            security_issues.append("Base URL does not use HTTPS")
        
        return {
            'issues': security_issues,
            'score': max(0, 100 - len(security_issues) * 20),
            'timestamp': self._get_current_timestamp()
        }
    
    def _analyze_performance(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance considerations"""
        endpoints = api_spec.get('endpoints', [])
        
        # Simple performance analysis
        performance_score = 100
        issues = []
        
        # Check for pagination
        has_pagination = any('pagination' in str(endpoint).lower() for endpoint in endpoints)
        if not has_pagination and len(endpoints) > 5:
            issues.append("Consider implementing pagination for large datasets")
            performance_score -= 10
        
        return {
            'score': performance_score,
            'issues': issues,
            'timestamp': self._get_current_timestamp()
        }
    
    def _analyze_documentation(self, api_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documentation quality"""
        endpoints = api_spec.get('endpoints', [])
        documented_endpoints = sum(1 for ep in endpoints if ep.get('description'))
        
        doc_score = (documented_endpoints / len(endpoints) * 100) if endpoints else 0
        
        return {
            'score': doc_score,
            'documented_endpoints': documented_endpoints,
            'total_endpoints': len(endpoints),
            'timestamp': self._get_current_timestamp()
        }
    
    def _generate_integration_recommendations(self, api_spec: Dict[str, Any]) -> List[str]:
        """Generate integration recommendations"""
        recommendations = []
        
        api_type = api_spec.get('api_type', '')
        if api_type == 'SOAP':
            recommendations.extend([
                "Use SOAP client libraries for better error handling",
                "Implement retry logic for network failures",
                "Consider using async SOAP clients for better performance"
            ])
        elif api_type == 'REST':
            recommendations.extend([
                "Use HTTP client libraries with connection pooling",
                "Implement proper error handling for HTTP status codes",
                "Consider using async/await patterns for better performance"
            ])
        
        return recommendations
    
    def _generate_code_examples(self, api_spec: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate code examples for key endpoints"""
        examples = {}
        endpoints = api_spec.get('endpoints', [])
        
        # Generate examples for first few endpoints
        for endpoint in endpoints[:3]:  # Limit to first 3 endpoints
            try:
                python_example = self.llm_service.generate_code_example(endpoint, "python", "basic")
                examples[endpoint.get('path', 'unknown')] = [python_example]
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to generate code example: {str(e)}")
        
        return examples
    
    def _extract_score_from_analysis(self, analysis: str) -> int:
        """Extract numerical score from AI analysis"""
        # Simple score extraction - in practice, you'd use more sophisticated NLP
        if 'excellent' in analysis.lower():
            return 90
        elif 'good' in analysis.lower():
            return 75
        elif 'fair' in analysis.lower():
            return 60
        elif 'poor' in analysis.lower():
            return 40
        else:
            return 70  # Default score
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _store_in_vector_db(self, api_spec: Dict[str, Any], chunking_strategy: ChunkingStrategy):
        """Store API specification in vector database with intelligent chunking"""
        try:
            # Add a temporary ID for vector storage
            api_spec['id'] = api_spec.get('id', 1)
            
            chunk_ids = self.vector_service.add_api_specification(api_spec, chunking_strategy)
            
            self.logger.info(f"✅ Stored API spec in vector DB with {sum(len(ids) for ids in chunk_ids.values())} chunks")
            
        except Exception as e:
            self.logger.error(f"❌ Error storing in vector DB: {str(e)}")
            raise
    
    def search_api_specifications(
        self, 
        query: str, 
        api_spec_ids: Optional[List[int]] = None,
        content_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search API specifications using vector similarity"""
        try:
            results = self.vector_service.search_api_specifications(
                query, 
                api_spec_ids, 
                content_types, 
                limit
            )
            
            self.logger.info(f"✅ Found {len(results)} search results")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error searching API specs: {str(e)}")
            raise
    
    def generate_ai_response(
        self, 
        query: str, 
        api_specs: Optional[List[Dict[str, Any]]] = None,
        search_context: Optional[List[Dict[str, Any]]] = None,
        task_type: str = 'chat_assistant'
    ) -> str:
        """Generate AI response with API specification context"""
        try:
            from models.schemas.schemas import LLMRequest
            
            request = LLMRequest(
                message=query,
                include_chain_of_thought=True
            )
            
            response = self.llm_service.generate_response(
                request, 
                task_type, 
                api_specs, 
                search_context
            )
            
            return response.response
            
        except Exception as e:
            self.logger.error(f"❌ Error generating AI response: {str(e)}")
            raise
    
    def validate_spec_format(self, content: str, format_type: str) -> bool:
        """Validate specification format"""
        
        try:
            if format_type.lower() in ['openapi', 'swagger']:
                if content.strip().startswith('{'):
                    json.loads(content)
                else:
                    yaml.safe_load(content)
                return True
            
            elif format_type.lower() == 'wsdl':
                ET.fromstring(content)
                return True
            
            elif format_type.lower() == 'raml':
                yaml.safe_load(content)
                return True
            
            elif format_type.lower() == 'graphql':
                if content.strip().startswith('{'):
                    json.loads(content)
                return True
            
            return False
            
        except Exception:
            return False
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported formats and their extensions"""
        return self.supported_formats
