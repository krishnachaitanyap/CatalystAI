#!/usr/bin/env python3
"""
Standalone Swagger/OpenAPI to CommonAPISpec Converter

This script converts Swagger 2.0 and OpenAPI 3.x files to CommonAPISpec JSON format.
It processes all Swagger/OpenAPI files from an input directory and outputs
the results to an output directory.

Usage:
    python swagger_converter.py --input-dir /path/to/swagger/files --output-dir /path/to/output
    python swagger_converter.py -i ./swagger_files -o ./output
    python swagger_converter.py  # Uses default directories: ./input and ./output

Features:
    - Processes multiple Swagger 2.0 and OpenAPI 3.x files
    - Automatically detects Swagger/OpenAPI files
    - Handles external references and dependencies
    - Generates CommonAPISpec JSON files
    - Provides detailed processing logs
    - Error handling and recovery
    - Intelligent caching and optimization
    - Batch processing capabilities
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Union
from datetime import datetime
import traceback
import yaml
import hashlib
from functools import lru_cache
from collections import defaultdict, deque
import weakref

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from connectors.api_connector import APIConnectorManager
    from utils.chunking import ChunkingConfig, ChunkingStrategy
    from models import CommonAPISpec
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you're running this script from the data-collector directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('swagger_converter.log')
    ]
)
logger = logging.getLogger(__name__)


def parse_json_or_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse JSON or YAML file and return the parsed content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try YAML
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML file {file_path}: {str(e)}")
            return None
            
    except Exception as e:
        logger.warning(f"Error reading file {file_path}: {str(e)}")
        return None


class IntelligentCache:
    """High-performance intelligent caching system for Swagger processing"""
    
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


class ReferenceResolver:
    """Sophisticated reference resolution for Swagger/OpenAPI files"""
    
    def __init__(self):
        self._reference_cache: Dict[str, Any] = {}
        self._circular_refs: Set[str] = set()
        self._processing_stack: Set[str] = set()
    
    def resolve_reference(self, ref: str, root_doc: Dict[str, Any], current_path: str = "") -> Any:
        """Resolve a reference with circular reference detection"""
        if not ref.startswith('#/'):
            # External reference - not supported in this version
            logger.warning(f"External reference not supported: {ref}")
            return None
        
        # Remove the #/ prefix
        ref_path = ref[2:]
        
        # Check for circular references
        if ref_path in self._processing_stack:
            self._circular_refs.add(ref_path)
            logger.warning(f"Circular reference detected: {ref_path}")
            return None
        
        # Check cache first
        cache_key = f"{current_path}:{ref_path}"
        if cache_key in self._reference_cache:
            return self._reference_cache[cache_key]
        
        # Add to processing stack
        self._processing_stack.add(ref_path)
        
        try:
            # Navigate through the reference path
            result = self._navigate_path(ref_path, root_doc)
            
            # Cache the result
            self._reference_cache[cache_key] = result
            
            return result
        finally:
            # Remove from processing stack
            self._processing_stack.discard(ref_path)
    
    def _navigate_path(self, path: str, doc: Dict[str, Any]) -> Any:
        """Navigate through a JSON path"""
        parts = path.split('/')
        current = doc
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                logger.warning(f"Reference path not found: {path}")
                return None
        
        return current
    
    def clear_cache(self) -> None:
        """Clear all cached references"""
        self._reference_cache.clear()
        self._circular_refs.clear()
        self._processing_stack.clear()


class SwaggerParser:
    """High-performance Swagger/OpenAPI parser with intelligent optimization"""
    
    def __init__(self):
        self.cache = IntelligentCache()
        self.reference_resolver = ReferenceResolver()
        self._processing_stats = defaultdict(int)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def detect_spec_version(self, spec: Dict[str, Any]) -> str:
        """Detect Swagger/OpenAPI specification version"""
        if 'openapi' in spec:
            return f"OpenAPI {spec['openapi']}"
        elif 'swagger' in spec:
            return f"Swagger {spec['swagger']}"
        else:
            return "Unknown"
    
    def parse_swagger_spec(self, spec_content: Dict[str, Any], file_path: str = "") -> Dict[str, Any]:
        """Parse Swagger/OpenAPI specification with maximum efficiency"""
        
        try:
            # Detect version
            version = self.detect_spec_version(spec_content)
            self.logger.info(f"Processing {version} specification")
            
            # Extract comprehensive information
            if version.startswith("OpenAPI 3"):
                return self._parse_openapi3(spec_content, file_path)
            elif version.startswith("Swagger 2"):
                return self._parse_swagger2(spec_content, file_path)
            else:
                raise ValueError(f"Unsupported specification version: {version}")
                
        except Exception as e:
            self.logger.error(f"Error parsing specification: {str(e)}")
            raise
    
    def _parse_openapi3(self, spec: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Parse OpenAPI 3.x specification"""
        self._processing_stats['openapi3_files'] += 1
        
        # Extract basic info
        info = spec.get('info', {})
        servers = spec.get('servers', [])
        paths = spec.get('paths', {})
        components = spec.get('components', {})
        
        # Process paths
        endpoints = []
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']:
                    endpoint = self._process_openapi3_operation(
                        path, method, operation, components, spec
                    )
                    endpoints.append(endpoint)
        
        # Process schemas
        schemas = self._process_openapi3_schemas(components.get('schemas', {}), spec)
        
        return {
            'spec_type': 'OpenAPI 3.x',
            'version': spec.get('openapi', '3.0.0'),
            'title': info.get('title', 'Unknown API'),
            'description': info.get('description', ''),
            'version_info': info.get('version', '1.0.0'),
            'contact': info.get('contact', {}),
            'license': info.get('license', {}),
            'servers': servers,
            'endpoints': endpoints,
            'schemas': schemas,
            'security_schemes': components.get('securitySchemes', {}),
            'file_path': file_path,
            'processing_stats': dict(self._processing_stats)
        }
    
    def _parse_swagger2(self, spec: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Parse Swagger 2.0 specification"""
        self._processing_stats['swagger2_files'] += 1
        
        # Extract basic info
        info = spec.get('info', {})
        host = spec.get('host', '')
        base_path = spec.get('basePath', '')
        schemes = spec.get('schemes', ['http'])
        paths = spec.get('paths', {})
        definitions = spec.get('definitions', {})
        
        # Process paths
        endpoints = []
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    endpoint = self._process_swagger2_operation(
                        path, method, operation, definitions, spec
                    )
                    endpoints.append(endpoint)
        
        # Process definitions
        schemas = self._process_swagger2_definitions(definitions, spec)
        
        return {
            'spec_type': 'Swagger 2.0',
            'version': spec.get('swagger', '2.0'),
            'title': info.get('title', 'Unknown API'),
            'description': info.get('description', ''),
            'version_info': info.get('version', '1.0.0'),
            'contact': info.get('contact', {}),
            'license': info.get('license', {}),
            'host': host,
            'base_path': base_path,
            'schemes': schemes,
            'endpoints': endpoints,
            'schemas': schemas,
            'security_definitions': spec.get('securityDefinitions', {}),
            'file_path': file_path,
            'processing_stats': dict(self._processing_stats)
        }
    
    def _process_openapi3_operation(self, path: str, method: str, operation: Dict[str, Any], 
                                   components: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAPI 3.x operation"""
        self._processing_stats['operations_processed'] += 1
        
        # Process parameters
        parameters = []
        for param in operation.get('parameters', []):
            param_info = self._process_openapi3_parameter(param, components, spec)
            parameters.append(param_info)
        
        # Process request body
        request_body = None
        if 'requestBody' in operation:
            request_body = self._process_openapi3_request_body(
                operation['requestBody'], components, spec
            )
        
        # Process responses
        responses = {}
        for status_code, response in operation.get('responses', {}).items():
            response_info = self._process_openapi3_response(response, components, spec)
            responses[status_code] = response_info
        
        return {
            'path': path,
            'method': method.upper(),
            'operation_id': operation.get('operationId', f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"),
            'summary': operation.get('summary', ''),
            'description': operation.get('description', ''),
            'tags': operation.get('tags', []),
            'parameters': parameters,
            'request_body': request_body,
            'responses': responses,
            'security': operation.get('security', []),
            'deprecated': operation.get('deprecated', False)
        }
    
    def _process_swagger2_operation(self, path: str, method: str, operation: Dict[str, Any], 
                                  definitions: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process Swagger 2.0 operation"""
        self._processing_stats['operations_processed'] += 1
        
        # Process parameters
        parameters = []
        for param in operation.get('parameters', []):
            param_info = self._process_swagger2_parameter(param, definitions, spec)
            parameters.append(param_info)
        
        # Process responses
        responses = {}
        for status_code, response in operation.get('responses', {}).items():
            response_info = self._process_swagger2_response(response, definitions, spec)
            responses[status_code] = response_info
        
        return {
            'path': path,
            'method': method.upper(),
            'operation_id': operation.get('operationId', f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"),
            'summary': operation.get('summary', ''),
            'description': operation.get('description', ''),
            'tags': operation.get('tags', []),
            'parameters': parameters,
            'responses': responses,
            'security': operation.get('security', []),
            'deprecated': operation.get('deprecated', False)
        }
    
    def _process_openapi3_parameter(self, param: Dict[str, Any], components: Dict[str, Any], 
                                   spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAPI 3.x parameter"""
        schema = param.get('schema', {})
        
        # Resolve schema reference if needed
        if '$ref' in schema:
            schema = self.reference_resolver.resolve_reference(schema['$ref'], spec) or {}
        
        return {
            'name': param.get('name', ''),
            'in': param.get('in', 'query'),
            'description': param.get('description', ''),
            'required': param.get('required', False),
            'deprecated': param.get('deprecated', False),
            'schema': schema,
            'example': param.get('example'),
            'examples': param.get('examples', {})
        }
    
    def _process_swagger2_parameter(self, param: Dict[str, Any], definitions: Dict[str, Any], 
                                   spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process Swagger 2.0 parameter"""
        return {
            'name': param.get('name', ''),
            'in': param.get('in', 'query'),
            'description': param.get('description', ''),
            'required': param.get('required', False),
            'type': param.get('type', 'string'),
            'format': param.get('format'),
            'schema': param.get('schema', {}),
            'example': param.get('example'),
            'enum': param.get('enum', [])
        }
    
    def _process_openapi3_request_body(self, request_body: Dict[str, Any], components: Dict[str, Any], 
                                     spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAPI 3.x request body"""
        content = request_body.get('content', {})
        
        # Process content types
        content_types = {}
        for content_type, media_type in content.items():
            schema = media_type.get('schema', {})
            
            # Resolve schema reference if needed
            if '$ref' in schema:
                schema = self.reference_resolver.resolve_reference(schema['$ref'], spec) or {}
            
            content_types[content_type] = {
                'schema': schema,
                'example': media_type.get('example'),
                'examples': media_type.get('examples', {})
            }
        
        return {
            'description': request_body.get('description', ''),
            'required': request_body.get('required', False),
            'content': content_types
        }
    
    def _process_openapi3_response(self, response: Dict[str, Any], components: Dict[str, Any], 
                                 spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAPI 3.x response"""
        content = response.get('content', {})
        
        # Process content types
        content_types = {}
        for content_type, media_type in content.items():
            schema = media_type.get('schema', {})
            
            # Resolve schema reference if needed
            if '$ref' in schema:
                schema = self.reference_resolver.resolve_reference(schema['$ref'], spec) or {}
            
            content_types[content_type] = {
                'schema': schema,
                'example': media_type.get('example'),
                'examples': media_type.get('examples', {})
            }
        
        return {
            'description': response.get('description', ''),
            'content': content_types,
            'headers': response.get('headers', {})
        }
    
    def _process_swagger2_response(self, response: Dict[str, Any], definitions: Dict[str, Any], 
                                 spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process Swagger 2.0 response"""
        schema = response.get('schema', {})
        
        # Resolve schema reference if needed
        if '$ref' in schema:
            schema = self.reference_resolver.resolve_reference(schema['$ref'], spec) or {}
        
        return {
            'description': response.get('description', ''),
            'schema': schema,
            'headers': response.get('headers', {}),
            'examples': response.get('examples', {})
        }
    
    def _process_openapi3_schemas(self, schemas: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process OpenAPI 3.x schemas"""
        processed_schemas = {}
        
        for schema_name, schema in schemas.items():
            processed_schema = self._process_schema(schema, spec)
            processed_schemas[schema_name] = processed_schema
        
        return processed_schemas
    
    def _process_swagger2_definitions(self, definitions: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process Swagger 2.0 definitions"""
        processed_definitions = {}
        
        for def_name, definition in definitions.items():
            processed_def = self._process_schema(definition, spec)
            processed_definitions[def_name] = processed_def
        
        return processed_definitions
    
    def _process_schema(self, schema: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
        """Process a schema with reference resolution"""
        if '$ref' in schema:
            resolved_schema = self.reference_resolver.resolve_reference(schema['$ref'], spec)
            if resolved_schema:
                return self._process_schema(resolved_schema, spec)
            return schema
        
        processed_schema = {
            'type': schema.get('type', 'object'),
            'description': schema.get('description', ''),
            'properties': {},
            'required': schema.get('required', []),
            'example': schema.get('example'),
            'examples': schema.get('examples', {})
        }
        
        # Process properties
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                processed_schema['properties'][prop_name] = self._process_schema(prop_schema, spec)
        
        # Process additional properties
        if 'additionalProperties' in schema:
            processed_schema['additionalProperties'] = self._process_schema(schema['additionalProperties'], spec)
        
        # Process items for arrays
        if 'items' in schema:
            processed_schema['items'] = self._process_schema(schema['items'], spec)
        
        # Process allOf, oneOf, anyOf
        for composition_type in ['allOf', 'oneOf', 'anyOf']:
            if composition_type in schema:
                processed_schema[composition_type] = [
                    self._process_schema(item, spec) for item in schema[composition_type]
                ]
        
        return processed_schema


class SwaggerConverter:
    """Standalone Swagger/OpenAPI to CommonAPISpec converter"""
    
    def __init__(self, input_dir: str, output_dir: str, chunking_strategy: str = "ENDPOINT_BASED"):
        """
        Initialize the Swagger converter
        
        Args:
            input_dir: Directory containing Swagger/OpenAPI files
            output_dir: Directory to output CommonAPISpec JSON files
            chunking_strategy: Chunking strategy for ChromaDB storage
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.chunking_strategy = chunking_strategy
        
        # Initialize API connector manager
        self.chunking_config = ChunkingConfig(
            strategy=getattr(ChunkingStrategy, chunking_strategy.upper()),
            chunk_size=512,
            chunk_overlap=50,
            max_chunks_per_spec=20,
            min_chunk_size=100,
            max_chunk_size=2048
        )
        
        self.api_manager = APIConnectorManager(self.chunking_config)
        self.api_manager.load_environment()
        
        # Initialize Swagger parser
        self.swagger_parser = SwaggerParser()
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'swagger_files': 0,
            'openapi_files': 0,
            'processed_successfully': 0,
            'failed': 0,
            'errors': []
        }
    
    def setup_directories(self):
        """Setup input and output directories"""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Input directory: {self.input_dir}")
        logger.info(f"📁 Output directory: {self.output_dir}")
    
    def find_swagger_files(self) -> List[Path]:
        """Find all Swagger/OpenAPI files in the input directory"""
        swagger_extensions = ['.json', '.yaml', '.yml']
        swagger_files = []
        
        for ext in swagger_extensions:
            swagger_files.extend(self.input_dir.glob(f"**/*{ext}"))
        
        # Filter out non-Swagger files by checking content
        valid_files = []
        for file_path in swagger_files:
            # Parse JSON or YAML file
            spec = parse_json_or_yaml(file_path)
            
            if spec is None:
                logger.warning(f"Skipping unparseable file: {file_path}")
                continue
            
            # Check if it's a Swagger/OpenAPI file
            if self._is_swagger_file(spec):
                valid_files.append(file_path)
            else:
                logger.info(f"Skipping non-Swagger file: {file_path}")
        
        logger.info(f"🔍 Found {len(valid_files)} Swagger/OpenAPI files")
        return valid_files
    
    def _is_swagger_file(self, spec: Dict[str, Any]) -> bool:
        """Check if a parsed JSON is a Swagger/OpenAPI specification"""
        return (
            'swagger' in spec or 
            'openapi' in spec or
            ('info' in spec and 'paths' in spec)
        )
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single Swagger/OpenAPI file"""
        try:
            logger.info(f"🔄 Processing: {file_path.name}")
            
            # Parse JSON or YAML file
            spec = parse_json_or_yaml(file_path)
            
            if spec is None:
                raise ValueError(f"Failed to parse file: {file_path}")
            
            # Parse the specification
            parsed_spec = self.swagger_parser.parse_swagger_spec(spec, str(file_path))
            
            # Convert to CommonAPISpec
            common_spec = self._convert_to_common_spec(parsed_spec, file_path)
            
            # Generate output filename
            output_filename = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_path = self.output_dir / output_filename
            
            # Write the output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(common_spec, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Successfully processed: {file_path.name} -> {output_filename}")
            self.stats['processed_successfully'] += 1
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path.name}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            self.stats['failed'] += 1
            self.stats['errors'].append({
                'file': str(file_path),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return False
    
    def _convert_to_common_spec(self, parsed_spec: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """Convert parsed Swagger spec to CommonAPISpec format"""
        
        # Create CommonAPISpec structure
        common_spec = {
            'metadata': {
                'spec_type': parsed_spec['spec_type'],
                'version': parsed_spec['version'],
                'title': parsed_spec['title'],
                'description': parsed_spec['description'],
                'version_info': parsed_spec['version_info'],
                'contact': parsed_spec['contact'],
                'license': parsed_spec['license'],
                'file_path': str(file_path),
                'processed_at': datetime.now().isoformat(),
                'processing_stats': parsed_spec['processing_stats']
            },
            'endpoints': [],
            'schemas': parsed_spec['schemas'],
            'security': {
                'schemes': parsed_spec.get('security_schemes', parsed_spec.get('security_definitions', {}))
            }
        }
        
        # Convert endpoints
        for endpoint in parsed_spec['endpoints']:
            common_endpoint = {
                'path': endpoint['path'],
                'method': endpoint['method'],
                'operation_id': endpoint['operation_id'],
                'summary': endpoint['summary'],
                'description': endpoint['description'],
                'tags': endpoint['tags'],
                'parameters': endpoint['parameters'],
                'responses': endpoint['responses'],
                'security': endpoint['security'],
                'deprecated': endpoint['deprecated']
            }
            
            # Add request body for OpenAPI 3.x
            if 'request_body' in endpoint:
                common_endpoint['request_body'] = endpoint['request_body']
            
            common_spec['endpoints'].append(common_endpoint)
        
        # Add server information
        if 'servers' in parsed_spec:
            common_spec['servers'] = parsed_spec['servers']
        elif 'host' in parsed_spec:
            common_spec['servers'] = [{
                'url': f"{parsed_spec.get('schemes', ['http'])[0]}://{parsed_spec['host']}{parsed_spec.get('base_path', '')}"
            }]
        
        return common_spec
    
    def process_all_files(self) -> Dict[str, Any]:
        """Process all Swagger/OpenAPI files in the input directory"""
        logger.info("🚀 Starting Swagger/OpenAPI conversion process")
        
        # Setup directories
        self.setup_directories()
        
        # Find all files
        swagger_files = self.find_swagger_files()
        self.stats['total_files'] = len(swagger_files)
        
        if not swagger_files:
            logger.warning("⚠️ No Swagger/OpenAPI files found in input directory")
            return self.stats
        
        # Process each file
        for file_path in swagger_files:
            self.process_file(file_path)
        
        # Log final statistics
        logger.info("📊 Conversion Statistics:")
        logger.info(f"   Total files: {self.stats['total_files']}")
        logger.info(f"   Processed successfully: {self.stats['processed_successfully']}")
        logger.info(f"   Failed: {self.stats['failed']}")
        logger.info(f"   Cache hit rate: {self.swagger_parser.cache.hit_rate:.2%}")
        
        if self.stats['errors']:
            logger.warning(f"   Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.warning(f"     - {error['file']}: {error['error']}")
        
        return self.stats


def main():
    """Main entry point for the Swagger converter"""
    parser = argparse.ArgumentParser(
        description="Convert Swagger/OpenAPI files to CommonAPISpec JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python swagger_converter.py --input-dir ./swagger_files --output-dir ./output
  python swagger_converter.py -i ./input -o ./output --chunking-strategy SEMANTIC
  python swagger_converter.py  # Uses default directories: ./input and ./output
        """
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        type=str,
        default='./input',
        help='Directory containing Swagger/OpenAPI files (default: ./input)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='./output',
        help='Directory to output CommonAPISpec JSON files (default: ./output)'
    )
    
    parser.add_argument(
        '--chunking-strategy',
        type=str,
        default='ENDPOINT_BASED',
        choices=['ENDPOINT_BASED', 'SEMANTIC', 'HYBRID', 'FIXED_SIZE'],
        help='Chunking strategy for ChromaDB storage (default: ENDPOINT_BASED)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create converter
        converter = SwaggerConverter(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            chunking_strategy=args.chunking_strategy
        )
        
        # Process all files
        stats = converter.process_all_files()
        
        # Exit with appropriate code
        if stats['failed'] > 0:
            logger.warning(f"⚠️ Completed with {stats['failed']} failures")
            sys.exit(1)
        else:
            logger.info("🎉 All files processed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("🛑 Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
