#!/usr/bin/env python3
"""
🔗 CatalystAI API Connector

This module provides connectors to convert various API specification formats
(Swagger/OpenAPI, WSDL) into a common structure for vector database storage.

Supported Formats:
- Swagger/OpenAPI 2.0 & 3.0
- WSDL 1.1 & 2.0
- GraphQL Schema
- AsyncAPI
- RAML (future)

Common Structure:
- Standardized metadata
- Endpoint definitions
- Authentication methods
- Rate limiting information
- Integration guidelines
"""

import os
import json
import yaml
import xml.etree.ElementTree as ET
import sys
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
from urllib.parse import urlparse, urljoin

# ChromaDB integration
import chromadb
from chromadb.config import Settings

# Utilities
from dotenv import load_dotenv

@dataclass
class CommonAPISpec:
    """Common structure for API specifications"""
    api_name: str
    version: str
    description: str
    base_url: str
    category: str
    endpoints: List[Dict[str, Any]]
    authentication: Dict[str, Any]
    rate_limits: Dict[str, Any]
    pricing: Optional[str]
    sdk_languages: List[str]
    documentation_url: str
    integration_steps: List[str]
    best_practices: List[str]
    common_use_cases: List[str]
    tags: List[str]
    contact_info: Dict[str, str]
    license_info: Dict[str, str]
    external_docs: List[Dict[str, str]]
    examples: List[Dict[str, Any]]
    namespaces: Dict[str, str] = None
    schema_version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""

class SwaggerConnector:
    """Connector for Swagger/OpenAPI specifications"""
    
    def __init__(self):
        self.supported_versions = ["2.0", "3.0.0", "3.0.1", "3.0.2", "3.0.3"]
    
    def parse_swagger_file(self, file_path: str) -> CommonAPISpec:
        """Parse Swagger/OpenAPI file and convert to common structure"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    spec_data = yaml.safe_load(f)
                else:
                    spec_data = json.load(f)
            
            return self._convert_swagger_to_common(spec_data, file_path)
            
        except Exception as e:
            raise ValueError(f"Error parsing Swagger file {file_path}: {str(e)}")
    
    def parse_swagger_url(self, url: str) -> CommonAPISpec:
        """Parse Swagger/OpenAPI from URL"""
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if 'yaml' in response.headers.get('content-type', '') or url.endswith(('.yaml', '.yml')):
                spec_data = yaml.safe_load(response.text)
            else:
                spec_data = response.json()
            
            return self._convert_swagger_to_common(spec_data, url)
            
        except Exception as e:
            raise ValueError(f"Error parsing Swagger URL {url}: {str(e)}")
    
    def _convert_swagger_to_common(self, spec_data: Dict[str, Any], source: str) -> CommonAPISpec:
        """Convert Swagger/OpenAPI spec to common structure"""
        
        # Determine version
        version = self._get_swagger_version(spec_data)
        
        if version.startswith("3."):
            return self._convert_openapi3_to_common(spec_data, source)
        else:
            return self._convert_swagger2_to_common(spec_data, source)
    
    def _get_swagger_version(self, spec_data: Dict[str, Any]) -> str:
        """Get Swagger/OpenAPI version"""
        return spec_data.get('openapi', spec_data.get('swagger', '2.0'))
    
    def _convert_openapi3_to_common(self, spec_data: Dict[str, Any], source: str) -> CommonAPISpec:
        """Convert OpenAPI 3.x to common structure"""
        
        info = spec_data.get('info', {})
        servers = spec_data.get('servers', [])
        paths = spec_data.get('paths', {})
        components = spec_data.get('components', {})
        
        # Extract base URL
        base_url = ""
        if servers:
            base_url = servers[0].get('url', '')
        
        # Extract endpoints
        endpoints = []
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': self._extract_detailed_parameters(operation.get('parameters', [])),
                        'request_body': self._extract_detailed_request_body(operation.get('requestBody', {})),
                        'responses': self._extract_detailed_responses(operation.get('responses', {})),
                        'tags': operation.get('tags', []),
                        'operation_id': operation.get('operationId', ''),
                        'deprecated': operation.get('deprecated', False)
                    }
                    endpoints.append(endpoint)
        
        # Extract authentication
        auth_info = self._extract_openapi3_auth(components)
        
        # Extract rate limits
        rate_limits = self._extract_rate_limits_from_spec(spec_data)
        
        return CommonAPISpec(
            api_name=info.get('title', 'Unknown API'),
            version=info.get('version', '1.0.0'),
            description=info.get('description', ''),
            base_url=base_url,
            category=self._categorize_api(info.get('title', ''), endpoints),
            endpoints=endpoints,
            authentication=auth_info,
            rate_limits=rate_limits,
            pricing=None,  # Not typically in OpenAPI spec
            sdk_languages=self._extract_sdk_languages(spec_data),
            documentation_url=source if source.startswith('http') else '',
            integration_steps=self._generate_integration_steps(endpoints, auth_info),
            best_practices=self._generate_best_practices(endpoints, auth_info),
            common_use_cases=self._generate_use_cases(endpoints),
            tags=info.get('tags', []),
            contact_info=self._extract_contact_info(info),
            license_info=self._extract_license_info(info),
            external_docs=spec_data.get('externalDocs', []),
            examples=self._extract_examples(endpoints),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    def _convert_swagger2_to_common(self, spec_data: Dict[str, Any], source: str) -> CommonAPISpec:
        """Convert Swagger 2.0 to common structure"""
        
        info = spec_data.get('info', {})
        host = spec_data.get('host', '')
        base_path = spec_data.get('basePath', '')
        paths = spec_data.get('paths', {})
        security_definitions = spec_data.get('securityDefinitions', {})
        
        # Extract base URL
        base_url = f"https://{host}{base_path}" if host else base_path
        
        # Extract endpoints
        endpoints = []
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': self._extract_detailed_parameters(operation.get('parameters', [])),
                        'request_body': self._extract_detailed_request_body_swagger2(operation),
                        'responses': self._extract_detailed_responses_swagger2(operation.get('responses', {})),
                        'tags': operation.get('tags', []),
                        'operation_id': operation.get('operationId', ''),
                        'deprecated': operation.get('deprecated', False)
                    }
                    endpoints.append(endpoint)
        
        # Extract authentication
        auth_info = self._extract_swagger2_auth(security_definitions)
        
        # Extract rate limits
        rate_limits = self._extract_rate_limits_from_spec(spec_data)
        
        return CommonAPISpec(
            api_name=info.get('title', 'Unknown API'),
            version=info.get('version', '1.0.0'),
            description=info.get('description', ''),
            base_url=base_url,
            category=self._categorize_api(info.get('title', ''), endpoints),
            endpoints=endpoints,
            authentication=auth_info,
            rate_limits=rate_limits,
            pricing=None,
            sdk_languages=self._extract_sdk_languages(spec_data),
            documentation_url=source if source.startswith('http') else '',
            integration_steps=self._generate_integration_steps(endpoints, auth_info),
            best_practices=self._generate_best_practices(endpoints, auth_info),
            common_use_cases=self._generate_use_cases(endpoints),
            tags=info.get('tags', []),
            contact_info=self._extract_contact_info(info),
            license_info=self._extract_license_info(info),
            external_docs=[],
            examples=self._extract_examples(endpoints),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    def _extract_openapi3_auth(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Extract authentication info from OpenAPI 3.x components"""
        
        security_schemes = components.get('securitySchemes', {})
        auth_info = {
            'type': 'none',
            'schemes': [],
            'description': ''
        }
        
        for scheme_name, scheme in security_schemes.items():
            scheme_type = scheme.get('type', '')
            if scheme_type in ['http', 'oauth2', 'apiKey', 'openIdConnect']:
                auth_info['schemes'].append({
                    'name': scheme_name,
                    'type': scheme_type,
                    'description': scheme.get('description', ''),
                    'in': scheme.get('in', ''),
                    'scheme': scheme.get('scheme', ''),
                    'bearer_format': scheme.get('bearerFormat', '')
                })
                
                if not auth_info['type'] or auth_info['type'] == 'none':
                    auth_info['type'] = scheme_type
        
        return auth_info
    
    def _extract_swagger2_auth(self, security_definitions: Dict[str, Any]) -> Dict[str, Any]:
        """Extract authentication info from Swagger 2.0 security definitions"""
        
        auth_info = {
            'type': 'none',
            'schemes': [],
            'description': ''
        }
        
        for scheme_name, scheme in security_definitions.items():
            scheme_type = scheme.get('type', '')
            if scheme_type in ['basic', 'apiKey', 'oauth2']:
                auth_info['schemes'].append({
                    'name': scheme_name,
                    'type': scheme_type,
                    'description': scheme.get('description', ''),
                    'in': scheme.get('in', ''),
                    'name': scheme.get('name', ''),
                    'flow': scheme.get('flow', ''),
                    'authorization_url': scheme.get('authorizationUrl', ''),
                    'token_url': scheme.get('tokenUrl', ''),
                    'scopes': scheme.get('scopes', {})
                })
                
                if not auth_info['type'] or auth_info['type'] == 'none':
                    auth_info['type'] = scheme_type
        
        return auth_info
    
    def _extract_rate_limits_from_spec(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract rate limiting information from spec"""
        
        # Look for rate limiting in extensions
        rate_limits = {
            'requests_per_second': None,
            'requests_per_minute': None,
            'requests_per_hour': None,
            'requests_per_day': None,
            'description': ''
        }
        
        # Check for common rate limiting extensions
        extensions = spec_data.get('x-rate-limit', {})
        if extensions:
            rate_limits.update(extensions)
        
        return rate_limits
    
    def _categorize_api(self, title: str, endpoints: List[Dict[str, Any]]) -> str:
        """Categorize API based on title and endpoints"""
        
        title_lower = title.lower()
        
        # Category mapping based on common patterns
        categories = {
            'payment': ['payment', 'stripe', 'paypal', 'square', 'billing', 'charge'],
            'authentication': ['auth', 'oauth', 'jwt', 'login', 'user', 'identity'],
            'communication': ['email', 'sms', 'notification', 'message', 'chat', 'slack'],
            'storage': ['storage', 'file', 'upload', 's3', 'cloud', 'bucket'],
            'analytics': ['analytics', 'tracking', 'metrics', 'stats', 'report'],
            'social': ['social', 'facebook', 'twitter', 'linkedin', 'instagram'],
            'ecommerce': ['shop', 'store', 'product', 'order', 'cart', 'inventory'],
            'finance': ['finance', 'banking', 'accounting', 'transaction', 'wallet'],
            'ai': ['ai', 'ml', 'machine', 'learning', 'neural', 'openai'],
            'maps': ['map', 'location', 'geocoding', 'directions', 'places']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        # Check endpoints for categorization
        endpoint_text = ' '.join([ep.get('summary', '') + ' ' + ep.get('description', '') for ep in endpoints])
        endpoint_text_lower = endpoint_text.lower()
        
        for category, keywords in categories.items():
            if any(keyword in endpoint_text_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_sdk_languages(self, spec_data: Dict[str, Any]) -> List[str]:
        """Extract supported SDK languages from spec"""
        
        # Common SDK languages - this would typically come from external sources
        # or be inferred from the API's documentation
        return ['Python', 'JavaScript', 'Java', 'C#', 'Go', 'Ruby', 'PHP', 'Swift', 'Kotlin']
    
    def _generate_integration_steps(self, endpoints: List[Dict[str, Any]], auth_info: Dict[str, Any]) -> List[str]:
        """Generate integration steps based on endpoints and auth"""
        
        steps = []
        
        # Authentication setup
        if auth_info['type'] != 'none':
            if auth_info['type'] == 'apiKey':
                steps.append("Obtain API key from provider")
                steps.append("Include API key in request headers")
            elif auth_info['type'] == 'oauth2':
                steps.append("Register application with OAuth provider")
                steps.append("Implement OAuth 2.0 flow")
                steps.append("Obtain access token")
                steps.append("Include access token in requests")
            elif auth_info['type'] == 'basic':
                steps.append("Obtain username and password")
                steps.append("Include basic auth in requests")
        
        # General integration steps
        steps.extend([
            "Review API documentation",
            "Choose appropriate SDK or implement HTTP client",
            "Implement error handling",
            "Add request/response logging",
            "Test integration in development environment",
            "Implement rate limiting and retry logic",
            "Deploy to production with monitoring"
        ])
        
        return steps
    
    def _generate_best_practices(self, endpoints: List[Dict[str, Any]], auth_info: Dict[str, Any]) -> List[str]:
        """Generate best practices based on API structure"""
        
        practices = [
            "Always use HTTPS in production",
            "Implement proper error handling",
            "Use appropriate HTTP status codes",
            "Implement request/response validation",
            "Add comprehensive logging",
            "Use connection pooling for HTTP clients",
            "Implement circuit breaker pattern",
            "Monitor API usage and performance"
        ]
        
        # Add auth-specific practices
        if auth_info['type'] != 'none':
            practices.extend([
                "Store credentials securely",
                "Implement token refresh logic",
                "Use least privilege principle",
                "Rotate credentials regularly"
            ])
        
        return practices
    
    def _generate_use_cases(self, endpoints: List[Dict[str, Any]]) -> List[str]:
        """Generate common use cases based on endpoints"""
        
        use_cases = []
        endpoint_text = ' '.join([ep.get('summary', '') + ' ' + ep.get('description', '') for ep in endpoints])
        endpoint_text_lower = endpoint_text.lower()
        
        # Common use case patterns
        use_case_patterns = {
            'user_management': ['user', 'account', 'profile', 'register', 'login'],
            'data_processing': ['process', 'transform', 'convert', 'parse'],
            'file_operations': ['upload', 'download', 'file', 'storage'],
            'notifications': ['notification', 'alert', 'email', 'sms', 'push'],
            'analytics': ['analytics', 'track', 'metric', 'report', 'dashboard'],
            'integration': ['webhook', 'callback', 'sync', 'import', 'export']
        }
        
        for use_case, keywords in use_case_patterns.items():
            if any(keyword in endpoint_text_lower for keyword in keywords):
                use_cases.append(use_case.replace('_', ' ').title())
        
        if not use_cases:
            use_cases = ['API Integration', 'Data Exchange', 'Service Integration']
        
        return use_cases
    
    def _extract_detailed_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract detailed parameter information"""
        detailed_params = []
        
        for param in parameters:
            param_info = {
                'name': param.get('name', ''),
                'in': param.get('in', ''),
                'description': param.get('description', ''),
                'required': param.get('required', False),
                'type': param.get('type', ''),
                'format': param.get('format', ''),
                'schema': param.get('schema', {}),
                'example': param.get('example', ''),
                'enum': param.get('enum', []),
                'default': param.get('default', ''),
                'minimum': param.get('minimum', ''),
                'maximum': param.get('maximum', ''),
                'min_length': param.get('minLength', ''),
                'max_length': param.get('maxLength', ''),
                'pattern': param.get('pattern', '')
            }
            detailed_params.append(param_info)
        
        return detailed_params
    
    def _extract_detailed_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed request body information for OpenAPI 3.x"""
        if not request_body:
            return {
                'description': '',
                'required': False,
                'content': {},
                'all_attributes': [],
                'searchable_content': ''
            }
        
        detailed_body = {
            'description': request_body.get('description', ''),
            'required': request_body.get('required', False),
            'content': {},
            'all_attributes': [],
            'searchable_content': ''
        }
        
        content = request_body.get('content', {})
        all_attributes = []
        searchable_parts = []
        
        for content_type, content_schema in content.items():
            schema_info = content_schema.get('schema', {})
            properties = self._extract_schema_properties(schema_info)
            
            detailed_body['content'][content_type] = {
                'schema': schema_info,
                'example': content_schema.get('example', ''),
                'examples': content_schema.get('examples', {}),
                'properties': properties
            }
            
            # Collect all attributes for vectorization
            all_attributes.extend(list(properties.values()))
            searchable_parts.append(f"Content-Type: {content_type}")
            if content_schema.get('example'):
                searchable_parts.append(f"Example: {content_schema['example']}")
        
        detailed_body['all_attributes'] = all_attributes
        detailed_body['searchable_content'] = ' '.join(searchable_parts)
        
        return detailed_body
    
    def _extract_detailed_request_body_swagger2(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed request body information for Swagger 2.0"""
        # In Swagger 2.0, request body is typically in parameters with 'in': 'body'
        body_params = [p for p in operation.get('parameters', []) if p.get('in') == 'body']
        
        if not body_params:
            return {
                'description': '',
                'required': False,
                'schema': {},
                'properties': {},
                'all_attributes': [],
                'searchable_content': ''
            }
        
        body_param = body_params[0]  # Usually only one body parameter
        schema = body_param.get('schema', {})
        
        properties = self._extract_schema_properties(schema)
        
        return {
            'description': body_param.get('description', ''),
            'required': body_param.get('required', False),
            'schema': schema,
            'properties': properties,
            'all_attributes': properties,
            'searchable_content': f"Schema: {schema.get('type', 'object')} Description: {body_param.get('description', '')}"
        }
    
    def _extract_detailed_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed response information for OpenAPI 3.x"""
        detailed_responses = {}
        
        for status_code, response_info in responses.items():
            detailed_response = {
                'description': response_info.get('description', ''),
                'headers': response_info.get('headers', {}),
                'content': {},
                'all_attributes': [],
                'searchable_content': ''
            }
            
            content = response_info.get('content', {})
            all_attributes = []
            searchable_parts = []
            
            for content_type, content_schema in content.items():
                schema_info = content_schema.get('schema', {})
                properties = self._extract_schema_properties(schema_info)
                
                detailed_response['content'][content_type] = {
                    'schema': schema_info,
                    'example': content_schema.get('example', ''),
                    'examples': content_schema.get('examples', {}),
                    'properties': properties
                }
                
                # Collect all attributes for vectorization
                all_attributes.extend(properties)
                searchable_parts.append(f"Status: {status_code} Content-Type: {content_type}")
                if content_schema.get('example'):
                    searchable_parts.append(f"Example: {content_schema['example']}")
            
            detailed_response['all_attributes'] = all_attributes
            detailed_response['searchable_content'] = ' '.join(searchable_parts)
            detailed_responses[status_code] = detailed_response
        
        return detailed_responses
    
    def _extract_detailed_responses_swagger2(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed response information for Swagger 2.0"""
        detailed_responses = {}
        
        for status_code, response_info in responses.items():
            schema = response_info.get('schema', {})
            properties = self._extract_schema_properties(schema)
            detailed_responses[status_code] = {
                'description': response_info.get('description', ''),
                'schema': schema,
                'headers': response_info.get('headers', {}),
                'properties': properties,
                'all_attributes': list(properties.values()),
                'searchable_content': f"Status: {status_code} Description: {response_info.get('description', '')} Schema: {schema.get('type', 'object')}"
            }
        
        return detailed_responses
    
    def _extract_schema_properties(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract properties from a schema"""
        if not schema:
            return {}
        
        properties = {}
        schema_props = schema.get('properties', {})
        
        for prop_name, prop_info in schema_props.items():
            properties[prop_name] = {
                'type': prop_info.get('type', ''),
                'format': prop_info.get('format', ''),
                'description': prop_info.get('description', ''),
                'example': prop_info.get('example', ''),
                'default': prop_info.get('default', ''),
                'required': prop_name in schema.get('required', []),
                'enum': prop_info.get('enum', []),
                'minimum': prop_info.get('minimum', ''),
                'maximum': prop_info.get('maximum', ''),
                'min_length': prop_info.get('minLength', ''),
                'max_length': prop_info.get('maxLength', ''),
                'pattern': prop_info.get('pattern', ''),
                'items': prop_info.get('items', {}),
                'additional_properties': prop_info.get('additionalProperties', {})
            }
        
        return properties
    
    def _extract_contact_info(self, info: Dict[str, Any]) -> Dict[str, str]:
        """Extract contact information"""
        
        contact = info.get('contact', {})
        return {
            'name': contact.get('name', ''),
            'email': contact.get('email', ''),
            'url': contact.get('url', '')
        }
    
    def _extract_license_info(self, info: Dict[str, Any]) -> Dict[str, str]:
        """Extract license information"""
        
        license_info = info.get('license', {})
        return {
            'name': license_info.get('name', ''),
            'url': license_info.get('url', '')
        }
    
    def _extract_examples(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract examples from endpoints"""
        
        examples = []
        for endpoint in endpoints:
            if endpoint.get('examples'):
                examples.append({
                    'endpoint': f"{endpoint['method']} {endpoint['path']}",
                    'examples': endpoint['examples']
                })
        
        return examples
    
    def display_vectorization_metrics(self, common_spec: CommonAPISpec) -> Dict[str, Any]:
        """
        Display comprehensive metrics for vectorization and embedding preparation
        
        Args:
            common_spec: The CommonAPISpec object to analyze
            
        Returns:
            Dictionary containing all metrics for programmatic access
        """
        metrics = {
            'api_overview': {},
            'endpoint_metrics': [],
            'attribute_metrics': {},
            'text_content_metrics': {},
            'embedding_preparation': {},
            'quality_indicators': {},
            'recommendations': []
        }
        
        print("\n" + "=" * 100)
        print("🔍 **VECTORIZATION & EMBEDDING METRICS ANALYSIS**")
        print("=" * 100)
        
        # 1. API Overview Metrics
        print("\n📊 **1. API OVERVIEW METRICS**")
        print("-" * 50)
        
        metrics['api_overview'] = {
            'api_name': common_spec.api_name,
            'api_version': common_spec.version,
            'total_endpoints': len(common_spec.endpoints),
            'api_type': getattr(common_spec, 'api_type', 'unknown'),
            'base_url': common_spec.base_url,
            'description_length': len(common_spec.description) if common_spec.description else 0,
            'has_namespaces': bool(getattr(common_spec, 'namespaces', None)),
            'namespace_count': len(common_spec.namespaces) if hasattr(common_spec, 'namespaces') and common_spec.namespaces else 0
        }
        
        print(f"🏷️  API Name: {metrics['api_overview']['api_name']}")
        print(f"📝 API Version: {metrics['api_overview']['api_version']}")
        print(f"🔗 Total Endpoints: {metrics['api_overview']['total_endpoints']}")
        print(f"📋 API Type: {metrics['api_overview']['api_type']}")
        print(f"🌐 Base URL: {metrics['api_overview']['base_url']}")
        print(f"📄 Description Length: {metrics['api_overview']['description_length']} chars")
        print(f"🏗️  Has Namespaces: {metrics['api_overview']['has_namespaces']}")
        if metrics['api_overview']['has_namespaces']:
            print(f"📦 Namespace Count: {metrics['api_overview']['namespace_count']}")
        
        # 2. Endpoint-Level Metrics
        print("\n📊 **2. ENDPOINT-LEVEL METRICS**")
        print("-" * 50)
        
        total_parameters = 0
        total_request_attributes = 0
        total_response_attributes = 0
        total_nested_attributes = 0
        
        for i, endpoint in enumerate(common_spec.endpoints):
            endpoint_metrics = {
                'endpoint_index': i,
                'path': endpoint['path'],
                'method': endpoint['method'],
                'parameter_count': len(endpoint['parameters']),
                'request_attribute_count': len(endpoint['request_body']['all_attributes']),
                'response_attribute_count': sum(len(resp['all_attributes']) for resp in endpoint['responses'].values()),
                'nested_attribute_count': sum(len(param.get('nested_attributes', [])) for param in endpoint['parameters']),
                'has_request_body': bool(endpoint['request_body']['all_attributes']),
                'response_count': len(endpoint['responses']),
                'searchable_content_length': len(endpoint['request_body']['searchable_content']) + 
                                           sum(len(resp['searchable_content']) for resp in endpoint['responses'].values())
            }
            
            metrics['endpoint_metrics'].append(endpoint_metrics)
            
            total_parameters += endpoint_metrics['parameter_count']
            total_request_attributes += endpoint_metrics['request_attribute_count']
            total_response_attributes += endpoint_metrics['response_attribute_count']
            total_nested_attributes += endpoint_metrics['nested_attribute_count']
            
            print(f"📍 Endpoint {i+1}: {endpoint['path']} ({endpoint['method']})")
            print(f"   📥 Parameters: {endpoint_metrics['parameter_count']}")
            print(f"   📋 Request Attributes: {endpoint_metrics['request_attribute_count']}")
            print(f"   📤 Response Attributes: {endpoint_metrics['response_attribute_count']}")
            print(f"   🔗 Nested Attributes: {endpoint_metrics['nested_attribute_count']}")
            print(f"   📄 Searchable Content: {endpoint_metrics['searchable_content_length']} chars")
            print()
        
        # 3. Attribute-Level Metrics
        print("\n📊 **3. ATTRIBUTE-LEVEL METRICS**")
        print("-" * 50)
        
        metrics['attribute_metrics'] = {
            'total_parameters': total_parameters,
            'total_request_attributes': total_request_attributes,
            'total_response_attributes': total_response_attributes,
            'total_nested_attributes': total_nested_attributes,
            'total_attributes': total_request_attributes + total_response_attributes + total_nested_attributes,
            'avg_attributes_per_endpoint': (total_request_attributes + total_response_attributes + total_nested_attributes) / len(common_spec.endpoints) if common_spec.endpoints else 0
        }
        
        print(f"📥 Total Parameters: {metrics['attribute_metrics']['total_parameters']}")
        print(f"📋 Total Request Attributes: {metrics['attribute_metrics']['total_request_attributes']}")
        print(f"📤 Total Response Attributes: {metrics['attribute_metrics']['total_response_attributes']}")
        print(f"🔗 Total Nested Attributes: {metrics['attribute_metrics']['total_nested_attributes']}")
        print(f"📊 Total Attributes: {metrics['attribute_metrics']['total_attributes']}")
        print(f"📈 Avg Attributes per Endpoint: {metrics['attribute_metrics']['avg_attributes_per_endpoint']:.2f}")
        
        # 4. Text Content Analysis
        print("\n📊 **4. TEXT CONTENT ANALYSIS**")
        print("-" * 50)
        
        all_text_content = []
        if common_spec.description:
            all_text_content.append(common_spec.description)
        
        for endpoint in common_spec.endpoints:
            all_text_content.append(endpoint['request_body']['searchable_content'])
            for response in endpoint['responses'].values():
                all_text_content.append(response['searchable_content'])
        
        combined_text = ' '.join(all_text_content)
        
        metrics['text_content_metrics'] = {
            'total_text_length': len(combined_text),
            'word_count': len(combined_text.split()),
            'unique_words': len(set(combined_text.lower().split())),
            'avg_word_length': sum(len(word) for word in combined_text.split()) / len(combined_text.split()) if combined_text.split() else 0,
            'text_density': len(combined_text) / metrics['attribute_metrics']['total_attributes'] if metrics['attribute_metrics']['total_attributes'] > 0 else 0,
            'has_meaningful_content': len(combined_text.strip()) > 100
        }
        
        print(f"📄 Total Text Length: {metrics['text_content_metrics']['total_text_length']} chars")
        print(f"📝 Word Count: {metrics['text_content_metrics']['word_count']}")
        print(f"🔤 Unique Words: {metrics['text_content_metrics']['unique_words']}")
        print(f"📏 Avg Word Length: {metrics['text_content_metrics']['avg_word_length']:.2f}")
        print(f"📊 Text Density: {metrics['text_content_metrics']['text_density']:.2f} chars/attribute")
        print(f"✅ Has Meaningful Content: {metrics['text_content_metrics']['has_meaningful_content']}")
        
        # 5. Embedding Preparation Metrics
        print("\n📊 **5. EMBEDDING PREPARATION METRICS**")
        print("-" * 50)
        
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(combined_text) // 4
        
        metrics['embedding_preparation'] = {
            'estimated_tokens': estimated_tokens,
            'embedding_dimensions_needed': min(1536, max(384, len(combined_text) // 10)),  # Adaptive dimension sizing
            'chunking_recommended': len(combined_text) > 8000,  # OpenAI context limit consideration
            'optimal_chunk_size': min(512, max(128, len(combined_text) // 20)),
            'chunk_overlap_recommended': 50,
            'vector_db_storage_size': len(combined_text) * 2,  # Rough estimate including metadata
            'embedding_cost_estimate': estimated_tokens * 0.0001  # Rough OpenAI pricing
        }
        
        print(f"🎯 Estimated Tokens: {metrics['embedding_preparation']['estimated_tokens']}")
        print(f"📐 Recommended Embedding Dimensions: {metrics['embedding_preparation']['embedding_dimensions_needed']}")
        print(f"✂️  Chunking Recommended: {metrics['embedding_preparation']['chunking_recommended']}")
        print(f"📏 Optimal Chunk Size: {metrics['embedding_preparation']['optimal_chunk_size']}")
        print(f"🔄 Recommended Chunk Overlap: {metrics['embedding_preparation']['chunk_overlap_recommended']}")
        print(f"💾 Estimated Vector DB Storage: {metrics['embedding_preparation']['vector_db_storage_size']} bytes")
        print(f"💰 Estimated Embedding Cost: ${metrics['embedding_preparation']['embedding_cost_estimate']:.4f}")
        
        # 6. Quality Indicators
        print("\n📊 **6. QUALITY INDICATORS**")
        print("-" * 50)
        
        quality_score = 0
        max_score = 100
        
        # Check various quality factors
        if metrics['api_overview']['description_length'] > 50:
            quality_score += 15
        if metrics['attribute_metrics']['total_attributes'] > 0:
            quality_score += 20
        if metrics['text_content_metrics']['has_meaningful_content']:
            quality_score += 25
        if metrics['attribute_metrics']['total_nested_attributes'] > 0:
            quality_score += 15
        if metrics['api_overview']['has_namespaces']:
            quality_score += 10
        if metrics['endpoint_metrics'] and len(metrics['endpoint_metrics']) > 0:
            quality_score += 15
        
        metrics['quality_indicators'] = {
            'overall_quality_score': quality_score,
            'max_possible_score': max_score,
            'quality_percentage': (quality_score / max_score) * 100,
            'has_description': metrics['api_overview']['description_length'] > 0,
            'has_attributes': metrics['attribute_metrics']['total_attributes'] > 0,
            'has_nested_structure': metrics['attribute_metrics']['total_nested_attributes'] > 0,
            'has_namespaces': metrics['api_overview']['has_namespaces'],
            'is_ready_for_embedding': quality_score >= 60
        }
        
        print(f"⭐ Overall Quality Score: {quality_score}/{max_score} ({metrics['quality_indicators']['quality_percentage']:.1f}%)")
        print(f"📝 Has Description: {metrics['quality_indicators']['has_description']}")
        print(f"📋 Has Attributes: {metrics['quality_indicators']['has_attributes']}")
        print(f"🔗 Has Nested Structure: {metrics['quality_indicators']['has_nested_structure']}")
        print(f"🏗️  Has Namespaces: {metrics['quality_indicators']['has_namespaces']}")
        print(f"✅ Ready for Embedding: {metrics['quality_indicators']['is_ready_for_embedding']}")
        
        # 7. Recommendations
        print("\n📊 **7. RECOMMENDATIONS**")
        print("-" * 50)
        
        recommendations = []
        
        if not metrics['quality_indicators']['has_description']:
            recommendations.append("Add API description to improve searchability")
        
        if metrics['attribute_metrics']['total_attributes'] == 0:
            recommendations.append("No attributes found - check API specification parsing")
        
        if metrics['text_content_metrics']['total_text_length'] < 100:
            recommendations.append("Very little text content - consider adding more descriptive information")
        
        if metrics['embedding_preparation']['chunking_recommended']:
            recommendations.append("Consider chunking for large content to optimize embedding performance")
        
        if metrics['quality_indicators']['quality_percentage'] < 60:
            recommendations.append("Quality score below 60% - review API specification completeness")
        
        if metrics['attribute_metrics']['total_nested_attributes'] == 0 and metrics['attribute_metrics']['total_attributes'] > 0:
            recommendations.append("Consider adding nested structures for better attribute organization")
        
        if not recommendations:
            recommendations.append("API specification looks good for vectorization!")
        
        metrics['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"💡 {i}. {rec}")
        
        print("\n" + "=" * 100)
        print("✅ **VECTORIZATION METRICS ANALYSIS COMPLETE**")
        print("=" * 100)
        
        return metrics

class WSDLConnector:
    """Connector for WSDL specifications"""
    
    def __init__(self):
        self.namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'soap12': 'http://schemas.xmlsoap.org/wsdl/soap12/',
            'http': 'http://schemas.xmlsoap.org/wsdl/http/',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'tns': 'http://tempuri.org/'  # Default namespace
        }
    
    def parse_wsdl_file(self, file_path: str) -> CommonAPISpec:
        """Parse WSDL file and convert to common structure"""
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            return self._convert_wsdl_to_common(root, file_path)
            
        except Exception as e:
            raise ValueError(f"Error parsing WSDL file {file_path}: {str(e)}")
    
    def parse_wsdl_url(self, url: str) -> CommonAPISpec:
        """Parse WSDL from URL"""
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            return self._convert_wsdl_to_common(root, url)
            
        except Exception as e:
            raise ValueError(f"Error parsing WSDL URL {url}: {str(e)}")
    
    def _convert_wsdl_to_common(self, root: ET.Element, source: str) -> CommonAPISpec:
        """Convert WSDL to common structure"""
        
        # Extract service information
        service_name = self._extract_service_name(root)
        service_description = self._extract_service_description(root)
        
        # Extract endpoints (operations)
        endpoints = self._extract_wsdl_endpoints(root)
        
        # Extract binding information
        bindings = self._extract_wsdl_bindings(root)
        
        # Extract types/schemas
        types_info = self._extract_wsdl_types(root)
        
        return CommonAPISpec(
            api_name=service_name,
            version='1.0.0',  # WSDL doesn't typically have version info
            description=service_description,
            base_url=self._extract_service_url(root),
            category='soap',
            endpoints=endpoints,
            authentication=self._extract_wsdl_auth(root),
            rate_limits={'description': 'Not specified in WSDL'},
            pricing=None,
            sdk_languages=['Java', 'C#', 'Python', 'PHP', 'Ruby'],
            documentation_url=source if source.startswith('http') else '',
            integration_steps=self._generate_soap_integration_steps(),
            best_practices=self._generate_soap_best_practices(),
            common_use_cases=['SOAP Service Integration', 'Enterprise Integration', 'Legacy System Integration'],
            tags=['soap', 'wsdl', 'enterprise'],
            contact_info={},
            license_info={},
            external_docs=[],
            examples=self._generate_soap_examples(endpoints),
            namespaces=types_info.get('namespaces', {}),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
    
    def _extract_service_name(self, root: ET.Element) -> str:
        """Extract service name from WSDL"""
        
        service_elements = root.findall('.//wsdl:service', self.namespaces)
        if service_elements:
            return service_elements[0].get('name', 'Unknown SOAP Service')
        
        return 'Unknown SOAP Service'
    
    def _extract_service_description(self, root: ET.Element) -> str:
        """Extract service description from WSDL"""
        
        # Look for documentation elements
        docs = root.findall('.//wsdl:documentation', self.namespaces)
        if docs:
            return docs[0].text or ''
        
        return 'SOAP Web Service'
    
    def _extract_service_url(self, root: ET.Element) -> str:
        """Extract service URL from WSDL"""
        
        # Look for soap:address elements
        addresses = root.findall('.//soap:address', self.namespaces)
        if addresses:
            return addresses[0].get('location', '')
        
        # Look for soap12:address elements
        addresses = root.findall('.//soap12:address', self.namespaces)
        if addresses:
            return addresses[0].get('location', '')
        
        return ''
    
    def _extract_wsdl_endpoints(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract endpoints (operations) from WSDL"""
        
        endpoints = []
        # Look for operations in portType sections (where they're defined)
        port_types = root.findall('.//wsdl:portType', self.namespaces)
        
        for port_type in port_types:
            operations = port_type.findall('wsdl:operation', self.namespaces)
            
            for operation in operations:
                operation_name = operation.get('name', '')
                if operation_name:
                    # Extract detailed input/output messages
                    input_msg = self._extract_operation_input_message(operation, root)
                    output_msg = self._extract_operation_output_message(operation, root)
                    
                    endpoint = {
                        'path': f"/{operation_name}",
                        'method': 'POST',  # SOAP typically uses POST
                        'summary': operation_name,
                        'description': self._extract_operation_description(operation),
                        'parameters': self._extract_soap_parameters(input_msg, root),
                        'request_body': self._extract_soap_request_body(input_msg, root),
                        'responses': self._extract_soap_responses(output_msg, root),
                        'tags': ['soap'],
                        'operation_id': operation_name,
                        'deprecated': False,
                        'soap_action': self._extract_soap_action_from_binding(operation_name, root)
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_soap_action(self, operation: ET.Element) -> str:
        """Extract SOAP action from operation"""
        
        soap_operations = operation.findall('.//soap:operation', self.namespaces)
        if soap_operations:
            return soap_operations[0].get('soapAction', '')
        
        return ''
    
    def _extract_soap_action_from_binding(self, operation_name: str, root: ET.Element) -> str:
        """Extract SOAP action from binding section"""
        # Look for the operation in binding sections
        bindings = root.findall('.//wsdl:binding', self.namespaces)
        
        for binding in bindings:
            operations = binding.findall('wsdl:operation', self.namespaces)
            for operation in operations:
                if operation.get('name') == operation_name:
                    soap_operation = operation.find('soap:operation', self.namespaces)
                    if soap_operation is not None:
                        return soap_operation.get('soapAction', '')
        
        return ''
    
    def _extract_operation_input_message(self, operation: ET.Element, root: ET.Element) -> ET.Element:
        """Extract input message from operation"""
        input_elem = operation.find('wsdl:input', self.namespaces)
        if input_elem is not None:
            message_ref = input_elem.get('message', '')
            # Handle qualified names (e.g., "tns:GetWeatherSoapIn")
            if ':' in message_ref:
                prefix, message_name = message_ref.split(':', 1)
                # Find the message definition in the root
                message_elem = root.find(f'.//wsdl:message[@name="{message_name}"]', self.namespaces)
                return message_elem
            else:
                # Direct message name
                message_elem = root.find(f'.//wsdl:message[@name="{message_ref}"]', self.namespaces)
                return message_elem
        return None
    
    def _extract_operation_output_message(self, operation: ET.Element, root: ET.Element) -> ET.Element:
        """Extract output message from operation"""
        output_elem = operation.find('wsdl:output', self.namespaces)
        if output_elem is not None:
            message_ref = output_elem.get('message', '')
            # Handle qualified names (e.g., "tns:GetWeatherSoapOut")
            if ':' in message_ref:
                prefix, message_name = message_ref.split(':', 1)
                # Find the message definition in the root
                message_elem = root.find(f'.//wsdl:message[@name="{message_name}"]', self.namespaces)
                return message_elem
            else:
                # Direct message name
                message_elem = root.find(f'.//wsdl:message[@name="{message_ref}"]', self.namespaces)
                return message_elem
        return None
    
    def _extract_operation_description(self, operation: ET.Element) -> str:
        """Extract operation description"""
        doc_elem = operation.find('wsdl:documentation', self.namespaces)
        if doc_elem is not None and doc_elem.text:
            return doc_elem.text.strip()
        return ''
    
    def _extract_soap_parameters(self, input_msg: ET.Element, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract SOAP parameters from input message with detailed schema attributes"""
        if input_msg is None:
            return []
        
        parameters = []
        parts = input_msg.findall('wsdl:part', self.namespaces)
        
        for part in parts:
            part_name = part.get('name', '')
            element_name = part.get('element', '')
            type_name = part.get('type', '')
            
            # Extract detailed schema information
            schema_details = self._extract_element_schema_details(element_name, root)
            
            param_info = {
                'name': part_name,
                'in': 'body',
                'description': f'SOAP part: {part_name}',
                'required': True,
                'type': 'object',
                'element': element_name,
                'type_name': type_name,
                'soap_part': True,
                'schema_details': schema_details,
                'attributes': schema_details.get('attributes', []),
                'nested_attributes': schema_details.get('nested_attributes', []),
                'searchable_content': self._create_searchable_content(schema_details)
            }
            parameters.append(param_info)
        
        return parameters
    
    def _extract_soap_request_body(self, input_msg: ET.Element, root: ET.Element) -> Dict[str, Any]:
        """Extract SOAP request body from input message with detailed schema"""
        if input_msg is None:
            return {}
        
        parts = input_msg.findall('wsdl:part', self.namespaces)
        body_info = {
            'description': 'SOAP request body',
            'required': True,
            'content_type': 'text/xml',
            'soap_envelope': True,
            'parts': [],
            'all_attributes': [],
            'searchable_content': ''
        }
        
        all_attributes = []
        searchable_parts = []
        
        for part in parts:
            element_name = part.get('element', '')
            schema_details = self._extract_element_schema_details(element_name, root)
            
            part_info = {
                'name': part.get('name', ''),
                'element': element_name,
                'type': part.get('type', ''),
                'schema_details': schema_details,
                'attributes': schema_details.get('attributes', []),
                'nested_attributes': schema_details.get('nested_attributes', []),
                'searchable_content': self._create_searchable_content(schema_details)
            }
            body_info['parts'].append(part_info)
            
            # Collect all attributes for easy searching (including nested)
            all_attributes.extend(schema_details.get('attributes', []))
            all_attributes.extend(schema_details.get('nested_attributes', []))
            searchable_parts.append(self._create_searchable_content(schema_details))
        
        body_info['all_attributes'] = all_attributes
        body_info['searchable_content'] = ' '.join(searchable_parts)
        
        return body_info
    
    def _extract_soap_responses(self, output_msg: ET.Element, root: ET.Element) -> Dict[str, Any]:
        """Extract SOAP responses from output message with detailed schema"""
        if output_msg is None:
            return {}
        
        parts = output_msg.findall('wsdl:part', self.namespaces)
        response_info = {
            '200': {
                'description': 'SOAP response',
                'content_type': 'text/xml',
                'soap_envelope': True,
                'parts': [],
                'all_attributes': [],
                'searchable_content': ''
            }
        }
        
        all_attributes = []
        searchable_parts = []
        
        for part in parts:
            element_name = part.get('element', '')
            schema_details = self._extract_element_schema_details(element_name, root)
            
            part_info = {
                'name': part.get('name', ''),
                'element': element_name,
                'type': part.get('type', ''),
                'schema_details': schema_details,
                'attributes': schema_details.get('attributes', []),
                'nested_attributes': schema_details.get('nested_attributes', []),
                'searchable_content': self._create_searchable_content(schema_details)
            }
            response_info['200']['parts'].append(part_info)
            
            # Collect all attributes for easy searching (including nested)
            all_attributes.extend(schema_details.get('attributes', []))
            all_attributes.extend(schema_details.get('nested_attributes', []))
            searchable_parts.append(self._create_searchable_content(schema_details))
        
        response_info['200']['all_attributes'] = all_attributes
        response_info['200']['searchable_content'] = ' '.join(searchable_parts)
        
        return response_info
    
    def _extract_element_schema_details(self, element_name: str, root: ET.Element) -> Dict[str, Any]:
        """Extract detailed schema information for an element"""
        if not element_name:
            return {'attributes': [], 'complex_type': None, 'description': ''}
        
        # Handle qualified names (e.g., "tns:GetWeatherRequest")
        if ':' in element_name:
            prefix, local_name = element_name.split(':', 1)
        else:
            local_name = element_name
        
        # Find the element definition in the schema
        element_elem = root.find(f'.//xsd:element[@name="{local_name}"]', self.namespaces)
        if element_elem is None:
            return {'attributes': [], 'complex_type': None, 'description': ''}
        
        schema_details = {
            'element_name': local_name,
            'qualified_name': element_name,
            'attributes': [],
            'complex_type': None,
            'description': '',
            'type': element_elem.get('type', ''),
            'min_occurs': element_elem.get('minOccurs', '1'),
            'max_occurs': element_elem.get('maxOccurs', '1')
        }
        
        # Look for inline complex type definition
        complex_type = element_elem.find('xsd:complexType', self.namespaces)
        if complex_type is not None:
            schema_details['complex_type'] = self._extract_complex_type_details(complex_type, root)
            schema_details['attributes'] = schema_details['complex_type'].get('attributes', [])
            schema_details['nested_attributes'] = schema_details['complex_type'].get('nested_attributes', [])
        
        # Look for referenced complex type definition
        elif schema_details['type'] and ':' in schema_details['type']:
            # Handle qualified type names (e.g., "tns:GetWeatherRequest")
            prefix, type_name = schema_details['type'].split(':', 1)
            referenced_complex_type = root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
            
            if referenced_complex_type is not None:
                schema_details['complex_type'] = self._extract_complex_type_details(referenced_complex_type, root)
                schema_details['attributes'] = schema_details['complex_type'].get('attributes', [])
                schema_details['nested_attributes'] = schema_details['complex_type'].get('nested_attributes', [])
        
        # Look for simple type definition
        simple_type = element_elem.find('xsd:simpleType', self.namespaces)
        if simple_type is not None:
            schema_details['simple_type'] = self._extract_simple_type_details(simple_type)
        
        return schema_details
    
    def _extract_complex_type_details(self, complex_type: ET.Element, root: ET.Element = None) -> Dict[str, Any]:
        """Extract details from a complex type definition with recursive nested element collection and inheritance support"""
        details = {
            'type': 'complex',
            'attributes': [],
            'elements': [],
            'sequences': [],
            'nested_attributes': [],  # New field for all nested leaf attributes
            'inherited_attributes': []  # New field for inherited attributes
        }
        
        # Check for complexContent with extension (inheritance)
        complex_content = complex_type.find('xsd:complexContent', self.namespaces)
        if complex_content is not None:
            extension = complex_content.find('xsd:extension', self.namespaces)
            if extension is not None:
                base_type = extension.get('base', '')
                print(f"Found inheritance: extending {base_type}")
                
                # Extract inherited attributes from base type
                if base_type and ':' in base_type:
                    prefix, type_name = base_type.split(':', 1)
                    base_complex_type = root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
                    if base_complex_type is not None:
                        base_details = self._extract_complex_type_details(base_complex_type, root)
                        details['inherited_attributes'] = base_details.get('attributes', [])
                        details['attributes'].extend(base_details.get('attributes', []))
                
                # Extract sequences from extension
                sequences = extension.findall('xsd:sequence', self.namespaces)
                for sequence in sequences:
                    sequence_details = {
                        'elements': []
                    }
                    
                    elements = sequence.findall('xsd:element', self.namespaces)
                    for element in elements:
                        element_details = {
                            'name': element.get('name', ''),
                            'type': element.get('type', ''),
                            'min_occurs': element.get('minOccurs', '1'),
                            'max_occurs': element.get('maxOccurs', '1'),
                            'nillable': element.get('nillable', 'false'),
                            'description': ''
                        }
                        
                        # Look for documentation
                        doc = element.find('xsd:annotation/xsd:documentation', self.namespaces)
                        if doc is not None and doc.text:
                            element_details['description'] = doc.text.strip()
                        
                        sequence_details['elements'].append(element_details)
                        details['attributes'].append(element_details)
                        
                        # Check if this element has nested complex type (recursive extraction)
                        if root is not None:
                            nested_attributes = self._extract_nested_attributes(element, root)
                            details['nested_attributes'].extend(nested_attributes)
                    
                    details['sequences'].append(sequence_details)
        
        # Extract direct sequence elements (for non-inherited complex types)
        sequences = complex_type.findall('xsd:sequence', self.namespaces)
        for sequence in sequences:
            sequence_details = {
                'elements': []
            }
            
            elements = sequence.findall('xsd:element', self.namespaces)
            for element in elements:
                element_details = {
                    'name': element.get('name', ''),
                    'type': element.get('type', ''),
                    'min_occurs': element.get('minOccurs', '1'),
                    'max_occurs': element.get('maxOccurs', '1'),
                    'nillable': element.get('nillable', 'false'),
                    'description': ''
                }
                
                # Look for documentation
                doc = element.find('xsd:annotation/xsd:documentation', self.namespaces)
                if doc is not None and doc.text:
                    element_details['description'] = doc.text.strip()
                
                sequence_details['elements'].append(element_details)
                details['attributes'].append(element_details)
                
                # Check if this element has nested complex type (recursive extraction)
                if root is not None:
                    nested_attributes = self._extract_nested_attributes(element, root)
                    details['nested_attributes'].extend(nested_attributes)
            
            details['sequences'].append(sequence_details)
        
        # Extract choice elements
        choices = complex_type.findall('xsd:choice', self.namespaces)
        for choice in choices:
            choice_details = {
                'elements': []
            }
            
            elements = choice.findall('xsd:element', self.namespaces)
            for element in elements:
                element_details = {
                    'name': element.get('name', ''),
                    'type': element.get('type', ''),
                    'min_occurs': element.get('minOccurs', '1'),
                    'max_occurs': element.get('maxOccurs', '1'),
                    'nillable': element.get('nillable', 'false'),
                    'description': ''
                }
                
                choice_details['elements'].append(element_details)
                details['attributes'].append(element_details)
                
                # Check if this element has nested complex type (recursive extraction)
                if root is not None:
                    nested_attributes = self._extract_nested_attributes(element, root)
                    details['nested_attributes'].extend(nested_attributes)
        
        return details
    
    def _extract_nested_attributes(self, element: ET.Element, root: ET.Element, parent_path: str = "") -> List[Dict[str, Any]]:
        """Recursively extract all nested attributes until leaf nodes"""
        nested_attributes = []
        element_name = element.get('name', '')
        element_type = element.get('type', '')
        
        # Build the path for nested elements
        current_path = f"{parent_path}.{element_name}" if parent_path else element_name
        
        # Check if this element has a complex type definition
        if element_type and ':' in element_type:
            # Handle qualified type names (e.g., "tns:DailyForecast")
            prefix, type_name = element_type.split(':', 1)
            complex_type_elem = root.find(f'.//xsd:complexType[@name="{type_name}"]', self.namespaces)
            
            if complex_type_elem is not None:
                # Recursively extract nested complex type details
                nested_details = self._extract_complex_type_details(complex_type_elem, root)
                
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
                                    current_path
                                )
                            )
        
        # Also check for inline complex type definition
        inline_complex_type = element.find('xsd:complexType', self.namespaces)
        if inline_complex_type is not None:
            nested_details = self._extract_complex_type_details(inline_complex_type, root)
            
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
                                current_path
                            )
                        )
        
        return nested_attributes
    
    def _extract_simple_type_details(self, simple_type: ET.Element) -> Dict[str, Any]:
        """Extract details from a simple type definition"""
        details = {
            'type': 'simple',
            'base_type': '',
            'restrictions': []
        }
        
        # Look for restriction
        restriction = simple_type.find('xsd:restriction', self.namespaces)
        if restriction is not None:
            details['base_type'] = restriction.get('base', '')
            
            # Extract restrictions
            restrictions = restriction.findall('*')
            for rest_elem in restrictions:
                rest_details = {
                    'type': rest_elem.tag.split('}')[-1] if '}' in rest_elem.tag else rest_elem.tag,
                    'value': rest_elem.get('value', ''),
                    'base': rest_elem.get('base', '')
                }
                details['restrictions'].append(rest_details)
        
        return details
    
    def _create_searchable_content(self, schema_details: Dict[str, Any]) -> str:
        """Create searchable text content from schema details"""
        searchable_parts = []
        
        # Add element name
        if schema_details.get('element_name'):
            searchable_parts.append(f"element {schema_details['element_name']}")
        
        # Add all attribute names and types
        for attr in schema_details.get('attributes', []):
            if attr.get('name'):
                searchable_parts.append(f"attribute {attr['name']}")
                if attr.get('type'):
                    searchable_parts.append(f"type {attr['type']}")
                if attr.get('description'):
                    searchable_parts.append(attr['description'])
        
        # Add complex type information
        if schema_details.get('complex_type'):
            complex_type = schema_details['complex_type']
            for attr in complex_type.get('attributes', []):
                if attr.get('name'):
                    searchable_parts.append(f"field {attr['name']}")
                    if attr.get('type'):
                        searchable_parts.append(f"data type {attr['type']}")
                    if attr.get('description'):
                        searchable_parts.append(attr['description'])
        
        return ' '.join(searchable_parts)
    
    def _extract_wsdl_bindings(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract binding information from WSDL"""
        
        bindings = []
        binding_elements = root.findall('.//wsdl:binding', self.namespaces)
        
        for binding in binding_elements:
            binding_info = {
                'name': binding.get('name', ''),
                'type': binding.get('type', ''),
                'protocol': 'SOAP'
            }
            bindings.append(binding_info)
        
        return bindings
    
    def _extract_wsdl_types(self, root: ET.Element) -> Dict[str, Any]:
        """Extract type definitions and namespace information from WSDL"""
        
        types_info = {
            'schemas': [],
            'elements': [],
            'complex_types': [],
            'namespaces': {}
        }
        
        # Extract all namespace declarations from the root element
        all_namespaces = {}
        
        # Extract from XML string using regex
        try:
            import xml.etree.ElementTree as ET
            import re
            xml_str = ET.tostring(root, encoding='unicode')
            xmlns_pattern = r'xmlns(?::(\w+))?="([^"]+)"'
            matches = re.findall(xmlns_pattern, xml_str)
            
            for match in matches:
                prefix = match[0] if match[0] else 'default'
                uri = match[1]
                all_namespaces[prefix] = uri
                
        except Exception as e:
            print(f"Warning: Could not extract namespaces: {e}")
        
        # Also extract targetNamespace from attributes
        if 'targetNamespace' in root.attrib:
            all_namespaces['targetNamespace'] = root.attrib['targetNamespace']
        
        # Get comprehensive namespace information
        namespace_info = self._extract_namespace_info(root)
        types_info['namespaces'] = all_namespaces
        types_info['detailed_namespaces'] = namespace_info
        
        # Look for schema elements
        schemas = root.findall('.//xsd:schema', self.namespaces)
        for schema in schemas:
            schema_info = {
                'target_namespace': schema.get('targetNamespace', ''),
                'element_form_default': schema.get('elementFormDefault', 'unqualified'),
                'attribute_form_default': schema.get('attributeFormDefault', 'unqualified'),
                'namespaces': {},
                'elements': [],
                'complex_types': []
            }
            
            # Extract namespace declarations from schema element
            schema_namespaces = {}
            for prefix, uri in schema.attrib.items():
                if prefix.startswith('xmlns'):
                    if prefix == 'xmlns':
                        schema_namespaces['default'] = uri
                    else:
                        ns_prefix = prefix.split(':', 1)[1] if ':' in prefix else prefix[6:]
                        schema_namespaces[ns_prefix] = uri
            
            schema_info['namespaces'] = schema_namespaces
            
            # Extract elements
            elements = schema.findall('.//xsd:element', self.namespaces)
            for element in elements:
                element_info = {
                    'name': element.get('name', ''),
                    'type': element.get('type', ''),
                    'min_occurs': element.get('minOccurs', ''),
                    'max_occurs': element.get('maxOccurs', '')
                }
                schema_info['elements'].append(element_info)
            
            # Extract complex types
            complex_types = schema.findall('.//xsd:complexType', self.namespaces)
            for complex_type in complex_types:
                complex_type_info = {
                    'name': complex_type.get('name', ''),
                    'elements': []
                }
                
                # Extract elements within complex type
                ct_elements = complex_type.findall('.//xsd:element', self.namespaces)
                for ct_element in ct_elements:
                    ct_element_info = {
                        'name': ct_element.get('name', ''),
                        'type': ct_element.get('type', ''),
                        'min_occurs': ct_element.get('minOccurs', ''),
                        'max_occurs': ct_element.get('maxOccurs', '')
                    }
                    complex_type_info['elements'].append(ct_element_info)
                
                schema_info['complex_types'].append(complex_type_info)
            
            types_info['schemas'].append(schema_info)
        
        return types_info
    
    def _extract_namespace_info(self, root: ET.Element) -> Dict[str, Any]:
        """Extract comprehensive namespace information from WSDL"""
        namespace_info = {
            'root_namespaces': {},
            'schema_namespaces': [],
            'target_namespaces': [],
            'imported_namespaces': []
        }
        
        # Extract root-level namespaces from the XML string
        try:
            # Parse the XML string to get namespace declarations
            import xml.etree.ElementTree as ET
            xml_str = ET.tostring(root, encoding='unicode')
            
            # Extract xmlns declarations using regex
            import re
            xmlns_pattern = r'xmlns(?::(\w+))?="([^"]+)"'
            matches = re.findall(xmlns_pattern, xml_str)
            
            for match in matches:
                prefix = match[0] if match[0] else 'default'
                uri = match[1]
                namespace_info['root_namespaces'][prefix] = uri
                
        except Exception as e:
            print(f"Warning: Could not extract root namespaces: {e}")
        
        # Also extract from root attributes (for targetNamespace)
        for prefix, uri in root.attrib.items():
            if prefix == 'targetNamespace':
                namespace_info['root_namespaces']['targetNamespace'] = uri
        
        # Extract schema-level namespaces
        schemas = root.findall('.//xsd:schema', self.namespaces)
        for schema in schemas:
            schema_ns = {
                'target_namespace': schema.get('targetNamespace', ''),
                'element_form_default': schema.get('elementFormDefault', 'unqualified'),
                'attribute_form_default': schema.get('attributeFormDefault', 'unqualified'),
                'namespaces': {}
            }
            
            # Extract namespaces declared in this schema
            for prefix, uri in schema.attrib.items():
                if prefix.startswith('xmlns'):
                    if prefix == 'xmlns':
                        schema_ns['namespaces']['default'] = uri
                    else:
                        ns_prefix = prefix.split(':', 1)[1] if ':' in prefix else prefix[6:]
                        schema_ns['namespaces'][ns_prefix] = uri
            
            namespace_info['schema_namespaces'].append(schema_ns)
            
            # Collect target namespaces
            if schema_ns['target_namespace']:
                namespace_info['target_namespaces'].append(schema_ns['target_namespace'])
        
        # Extract imported namespaces
        imports = root.findall('.//xsd:import', self.namespaces)
        for imp in imports:
            import_info = {
                'namespace': imp.get('namespace', ''),
                'schema_location': imp.get('schemaLocation', '')
            }
            namespace_info['imported_namespaces'].append(import_info)
        
        return namespace_info
    
    def _extract_wsdl_auth(self, root: ET.Element) -> Dict[str, Any]:
        """Extract authentication information from WSDL"""
        
        # WSDL doesn't typically contain auth info, but we can infer SOAP-specific auth
        return {
            'type': 'soap',
            'schemes': [{
                'name': 'SOAP Authentication',
                'type': 'soap',
                'description': 'SOAP-specific authentication mechanisms',
                'ws_security': True,
                'basic_auth': True,
                'certificate_auth': True
            }],
            'description': 'SOAP services typically use WS-Security, Basic Auth, or Certificate-based authentication'
        }
    
    def _generate_soap_integration_steps(self) -> List[str]:
        """Generate SOAP-specific integration steps"""
        
        return [
            "Obtain WSDL file or URL",
            "Generate client stubs using WSDL",
            "Configure SOAP client",
            "Implement authentication (WS-Security, Basic Auth, etc.)",
            "Handle SOAP faults and errors",
            "Implement request/response logging",
            "Test with SOAP client tools",
            "Deploy with proper error handling"
        ]
    
    def _generate_soap_best_practices(self) -> List[str]:
        """Generate SOAP-specific best practices"""
        
        return [
            "Always use HTTPS for SOAP endpoints",
            "Implement proper SOAP fault handling",
            "Use WS-Security for authentication",
            "Validate SOAP messages against schema",
            "Implement request/response logging",
            "Use connection pooling for SOAP clients",
            "Handle timeouts appropriately",
            "Implement retry logic for transient failures",
            "Monitor SOAP service performance",
            "Use appropriate SOAP version (1.1 or 1.2)"
        ]
    
    def _generate_soap_examples(self, endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate SOAP examples"""
        
        examples = []
        for endpoint in endpoints:
            example = {
                'endpoint': f"SOAP {endpoint['operation_id']}",
                'soap_action': endpoint.get('soap_action', ''),
                'request_example': f"""
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Header>
        <!-- Authentication headers -->
    </soap:Header>
    <soap:Body>
        <{endpoint['operation_id']}>
            <!-- Request parameters -->
        </{endpoint['operation_id']}>
    </soap:Body>
</soap:Envelope>
                """.strip(),
                'response_example': f"""
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <{endpoint['operation_id']}Response>
            <!-- Response data -->
        </{endpoint['operation_id']}Response>
    </soap:Body>
</soap:Envelope>
                """.strip()
            }
            examples.append(example)
        
        return examples
    
    def convert_to_json(self, common_spec: CommonAPISpec, indent: int = 2, ensure_ascii: bool = False) -> str:
        """
        Convert CommonAPISpec to JSON format
        
        Args:
            common_spec: The CommonAPISpec object to convert
            indent: JSON indentation level (default: 2)
            ensure_ascii: Whether to ensure ASCII encoding (default: False)
            
        Returns:
            JSON string representation of the CommonAPISpec
        """
        try:
            # Convert to dictionary using asdict
            spec_dict = asdict(common_spec)
            
            # Convert to JSON string
            json_str = json.dumps(spec_dict, indent=indent, ensure_ascii=ensure_ascii)
            
            return json_str
            
        except Exception as e:
            raise ValueError(f"Error converting CommonAPISpec to JSON: {str(e)}")
    
    def convert_to_json_file(self, common_spec: CommonAPISpec, file_path: str, indent: int = 2, ensure_ascii: bool = False) -> bool:
        """
        Convert CommonAPISpec to JSON and save to file
        
        Args:
            common_spec: The CommonAPISpec object to convert
            file_path: Path where to save the JSON file
            indent: JSON indentation level (default: 2)
            ensure_ascii: Whether to ensure ASCII encoding (default: False)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to JSON string
            json_str = self.convert_to_json(common_spec, indent, ensure_ascii)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            print(f"✅ JSON file saved successfully: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving JSON file: {str(e)}")
            return False
    
    def print_json(self, common_spec: CommonAPISpec, indent: int = 2, ensure_ascii: bool = False) -> None:
        """
        Print CommonAPISpec as formatted JSON to console
        
        Args:
            common_spec: The CommonAPISpec object to print
            indent: JSON indentation level (default: 2)
            ensure_ascii: Whether to ensure ASCII encoding (default: False)
        """
        try:
            json_str = self.convert_to_json(common_spec, indent, ensure_ascii)
            print("\n" + "=" * 80)
            print("📋 **WSDL API SPECIFICATION (JSON FORMAT)**")
            print("=" * 80)
            print(json_str)
            print("\n" + "=" * 80)
            print("✅ **JSON CONVERSION COMPLETE**")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ Error printing JSON: {str(e)}")
    
    def display_vectorization_metrics(self, common_spec: CommonAPISpec) -> Dict[str, Any]:
        """
        Display comprehensive metrics for vectorization and embedding preparation
        
        Args:
            common_spec: The CommonAPISpec object to analyze
            
        Returns:
            Dictionary containing all metrics for programmatic access
        """
        metrics = {
            'api_overview': {},
            'endpoint_metrics': [],
            'attribute_metrics': {},
            'text_content_metrics': {},
            'embedding_preparation': {},
            'quality_indicators': {},
            'recommendations': []
        }
        
        print("\n" + "=" * 100)
        print("🔍 **VECTORIZATION & EMBEDDING METRICS ANALYSIS**")
        print("=" * 100)
        
        # 1. API Overview Metrics
        print("\n📊 **1. API OVERVIEW METRICS**")
        print("-" * 50)
        
        metrics['api_overview'] = {
            'api_name': common_spec.api_name,
            'api_version': common_spec.version,
            'total_endpoints': len(common_spec.endpoints),
            'api_type': getattr(common_spec, 'api_type', 'unknown'),
            'base_url': common_spec.base_url,
            'description_length': len(common_spec.description) if common_spec.description else 0,
            'has_namespaces': bool(getattr(common_spec, 'namespaces', None)),
            'namespace_count': len(common_spec.namespaces) if hasattr(common_spec, 'namespaces') and common_spec.namespaces else 0
        }
        
        print(f"🏷️  API Name: {metrics['api_overview']['api_name']}")
        print(f"📝 API Version: {metrics['api_overview']['api_version']}")
        print(f"🔗 Total Endpoints: {metrics['api_overview']['total_endpoints']}")
        print(f"📋 API Type: {metrics['api_overview']['api_type']}")
        print(f"🌐 Base URL: {metrics['api_overview']['base_url']}")
        print(f"📄 Description Length: {metrics['api_overview']['description_length']} chars")
        print(f"🏗️  Has Namespaces: {metrics['api_overview']['has_namespaces']}")
        if metrics['api_overview']['has_namespaces']:
            print(f"📦 Namespace Count: {metrics['api_overview']['namespace_count']}")
        
        # 2. Endpoint-Level Metrics
        print("\n📊 **2. ENDPOINT-LEVEL METRICS**")
        print("-" * 50)
        
        total_parameters = 0
        total_request_attributes = 0
        total_response_attributes = 0
        total_nested_attributes = 0
        
        for i, endpoint in enumerate(common_spec.endpoints):
            endpoint_metrics = {
                'endpoint_index': i,
                'path': endpoint['path'],
                'method': endpoint['method'],
                'parameter_count': len(endpoint['parameters']),
                'request_attribute_count': len(endpoint['request_body']['all_attributes']),
                'response_attribute_count': sum(len(resp['all_attributes']) for resp in endpoint['responses'].values()),
                'nested_attribute_count': sum(len(param.get('nested_attributes', [])) for param in endpoint['parameters']),
                'has_request_body': bool(endpoint['request_body']['all_attributes']),
                'response_count': len(endpoint['responses']),
                'searchable_content_length': len(endpoint['request_body']['searchable_content']) + 
                                           sum(len(resp['searchable_content']) for resp in endpoint['responses'].values())
            }
            
            metrics['endpoint_metrics'].append(endpoint_metrics)
            
            total_parameters += endpoint_metrics['parameter_count']
            total_request_attributes += endpoint_metrics['request_attribute_count']
            total_response_attributes += endpoint_metrics['response_attribute_count']
            total_nested_attributes += endpoint_metrics['nested_attribute_count']
            
            print(f"📍 Endpoint {i+1}: {endpoint['path']} ({endpoint['method']})")
            print(f"   📥 Parameters: {endpoint_metrics['parameter_count']}")
            print(f"   📋 Request Attributes: {endpoint_metrics['request_attribute_count']}")
            print(f"   📤 Response Attributes: {endpoint_metrics['response_attribute_count']}")
            print(f"   🔗 Nested Attributes: {endpoint_metrics['nested_attribute_count']}")
            print(f"   📄 Searchable Content: {endpoint_metrics['searchable_content_length']} chars")
            print()
        
        # 3. Attribute-Level Metrics
        print("\n📊 **3. ATTRIBUTE-LEVEL METRICS**")
        print("-" * 50)
        
        metrics['attribute_metrics'] = {
            'total_parameters': total_parameters,
            'total_request_attributes': total_request_attributes,
            'total_response_attributes': total_response_attributes,
            'total_nested_attributes': total_nested_attributes,
            'total_attributes': total_request_attributes + total_response_attributes + total_nested_attributes,
            'avg_attributes_per_endpoint': (total_request_attributes + total_response_attributes + total_nested_attributes) / len(common_spec.endpoints) if common_spec.endpoints else 0
        }
        
        print(f"📥 Total Parameters: {metrics['attribute_metrics']['total_parameters']}")
        print(f"📋 Total Request Attributes: {metrics['attribute_metrics']['total_request_attributes']}")
        print(f"📤 Total Response Attributes: {metrics['attribute_metrics']['total_response_attributes']}")
        print(f"🔗 Total Nested Attributes: {metrics['attribute_metrics']['total_nested_attributes']}")
        print(f"📊 Total Attributes: {metrics['attribute_metrics']['total_attributes']}")
        print(f"📈 Avg Attributes per Endpoint: {metrics['attribute_metrics']['avg_attributes_per_endpoint']:.2f}")
        
        # 4. Text Content Analysis
        print("\n📊 **4. TEXT CONTENT ANALYSIS**")
        print("-" * 50)
        
        all_text_content = []
        if common_spec.description:
            all_text_content.append(common_spec.description)
        
        for endpoint in common_spec.endpoints:
            all_text_content.append(endpoint['request_body']['searchable_content'])
            for response in endpoint['responses'].values():
                all_text_content.append(response['searchable_content'])
        
        combined_text = ' '.join(all_text_content)
        
        metrics['text_content_metrics'] = {
            'total_text_length': len(combined_text),
            'word_count': len(combined_text.split()),
            'unique_words': len(set(combined_text.lower().split())),
            'avg_word_length': sum(len(word) for word in combined_text.split()) / len(combined_text.split()) if combined_text.split() else 0,
            'text_density': len(combined_text) / metrics['attribute_metrics']['total_attributes'] if metrics['attribute_metrics']['total_attributes'] > 0 else 0,
            'has_meaningful_content': len(combined_text.strip()) > 100
        }
        
        print(f"📄 Total Text Length: {metrics['text_content_metrics']['total_text_length']} chars")
        print(f"📝 Word Count: {metrics['text_content_metrics']['word_count']}")
        print(f"🔤 Unique Words: {metrics['text_content_metrics']['unique_words']}")
        print(f"📏 Avg Word Length: {metrics['text_content_metrics']['avg_word_length']:.2f}")
        print(f"📊 Text Density: {metrics['text_content_metrics']['text_density']:.2f} chars/attribute")
        print(f"✅ Has Meaningful Content: {metrics['text_content_metrics']['has_meaningful_content']}")
        
        # 5. Embedding Preparation Metrics
        print("\n📊 **5. EMBEDDING PREPARATION METRICS**")
        print("-" * 50)
        
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(combined_text) // 4
        
        metrics['embedding_preparation'] = {
            'estimated_tokens': estimated_tokens,
            'embedding_dimensions_needed': min(1536, max(384, len(combined_text) // 10)),  # Adaptive dimension sizing
            'chunking_recommended': len(combined_text) > 8000,  # OpenAI context limit consideration
            'optimal_chunk_size': min(512, max(128, len(combined_text) // 20)),
            'chunk_overlap_recommended': 50,
            'vector_db_storage_size': len(combined_text) * 2,  # Rough estimate including metadata
            'embedding_cost_estimate': estimated_tokens * 0.0001  # Rough OpenAI pricing
        }
        
        print(f"🎯 Estimated Tokens: {metrics['embedding_preparation']['estimated_tokens']}")
        print(f"📐 Recommended Embedding Dimensions: {metrics['embedding_preparation']['embedding_dimensions_needed']}")
        print(f"✂️  Chunking Recommended: {metrics['embedding_preparation']['chunking_recommended']}")
        print(f"📏 Optimal Chunk Size: {metrics['embedding_preparation']['optimal_chunk_size']}")
        print(f"🔄 Recommended Chunk Overlap: {metrics['embedding_preparation']['chunk_overlap_recommended']}")
        print(f"💾 Estimated Vector DB Storage: {metrics['embedding_preparation']['vector_db_storage_size']} bytes")
        print(f"💰 Estimated Embedding Cost: ${metrics['embedding_preparation']['embedding_cost_estimate']:.4f}")
        
        # 6. Quality Indicators
        print("\n📊 **6. QUALITY INDICATORS**")
        print("-" * 50)
        
        quality_score = 0
        max_score = 100
        
        # Check various quality factors
        if metrics['api_overview']['description_length'] > 50:
            quality_score += 15
        if metrics['attribute_metrics']['total_attributes'] > 0:
            quality_score += 20
        if metrics['text_content_metrics']['has_meaningful_content']:
            quality_score += 25
        if metrics['attribute_metrics']['total_nested_attributes'] > 0:
            quality_score += 15
        if metrics['api_overview']['has_namespaces']:
            quality_score += 10
        if metrics['endpoint_metrics'] and len(metrics['endpoint_metrics']) > 0:
            quality_score += 15
        
        metrics['quality_indicators'] = {
            'overall_quality_score': quality_score,
            'max_possible_score': max_score,
            'quality_percentage': (quality_score / max_score) * 100,
            'has_description': metrics['api_overview']['description_length'] > 0,
            'has_attributes': metrics['attribute_metrics']['total_attributes'] > 0,
            'has_nested_structure': metrics['attribute_metrics']['total_nested_attributes'] > 0,
            'has_namespaces': metrics['api_overview']['has_namespaces'],
            'is_ready_for_embedding': quality_score >= 60
        }
        
        print(f"⭐ Overall Quality Score: {quality_score}/{max_score} ({metrics['quality_indicators']['quality_percentage']:.1f}%)")
        print(f"📝 Has Description: {metrics['quality_indicators']['has_description']}")
        print(f"📋 Has Attributes: {metrics['quality_indicators']['has_attributes']}")
        print(f"🔗 Has Nested Structure: {metrics['quality_indicators']['has_nested_structure']}")
        print(f"🏗️  Has Namespaces: {metrics['quality_indicators']['has_namespaces']}")
        print(f"✅ Ready for Embedding: {metrics['quality_indicators']['is_ready_for_embedding']}")
        
        # 7. Recommendations
        print("\n📊 **7. RECOMMENDATIONS**")
        print("-" * 50)
        
        recommendations = []
        
        if not metrics['quality_indicators']['has_description']:
            recommendations.append("Add API description to improve searchability")
        
        if metrics['attribute_metrics']['total_attributes'] == 0:
            recommendations.append("No attributes found - check API specification parsing")
        
        if metrics['text_content_metrics']['total_text_length'] < 100:
            recommendations.append("Very little text content - consider adding more descriptive information")
        
        if metrics['embedding_preparation']['chunking_recommended']:
            recommendations.append("Consider chunking for large content to optimize embedding performance")
        
        if metrics['quality_indicators']['quality_percentage'] < 60:
            recommendations.append("Quality score below 60% - review API specification completeness")
        
        if metrics['attribute_metrics']['total_nested_attributes'] == 0 and metrics['attribute_metrics']['total_attributes'] > 0:
            recommendations.append("Consider adding nested structures for better attribute organization")
        
        if not recommendations:
            recommendations.append("API specification looks good for vectorization!")
        
        metrics['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"💡 {i}. {rec}")
        
        print("\n" + "=" * 100)
        print("✅ **VECTORIZATION METRICS ANALYSIS COMPLETE**")
        print("=" * 100)
        
        return metrics
    
    def display_vectorization_metrics(self, common_spec: CommonAPISpec) -> Dict[str, Any]:
        """
        Display comprehensive metrics for vectorization and embedding preparation
        
        Args:
            common_spec: The CommonAPISpec object to analyze
            
        Returns:
            Dictionary containing all metrics for programmatic access
        """
        metrics = {
            'api_overview': {},
            'endpoint_metrics': [],
            'attribute_metrics': {},
            'text_content_metrics': {},
            'embedding_preparation': {},
            'quality_indicators': {},
            'recommendations': []
        }
        
        print("\n" + "=" * 100)
        print("🔍 **VECTORIZATION & EMBEDDING METRICS ANALYSIS**")
        print("=" * 100)
        
        # 1. API Overview Metrics
        print("\n📊 **1. API OVERVIEW METRICS**")
        print("-" * 50)
        
        metrics['api_overview'] = {
            'api_name': common_spec.api_name,
            'api_version': common_spec.version,
            'total_endpoints': len(common_spec.endpoints),
            'api_type': getattr(common_spec, 'api_type', 'unknown'),
            'base_url': common_spec.base_url,
            'description_length': len(common_spec.description) if common_spec.description else 0,
            'has_namespaces': bool(getattr(common_spec, 'namespaces', None)),
            'namespace_count': len(common_spec.namespaces) if hasattr(common_spec, 'namespaces') and common_spec.namespaces else 0
        }
        
        print(f"🏷️  API Name: {metrics['api_overview']['api_name']}")
        print(f"📝 API Version: {metrics['api_overview']['api_version']}")
        print(f"🔗 Total Endpoints: {metrics['api_overview']['total_endpoints']}")
        print(f"📋 API Type: {metrics['api_overview']['api_type']}")
        print(f"🌐 Base URL: {metrics['api_overview']['base_url']}")
        print(f"📄 Description Length: {metrics['api_overview']['description_length']} chars")
        print(f"🏗️  Has Namespaces: {metrics['api_overview']['has_namespaces']}")
        if metrics['api_overview']['has_namespaces']:
            print(f"📦 Namespace Count: {metrics['api_overview']['namespace_count']}")
        
        # 2. Endpoint-Level Metrics
        print("\n📊 **2. ENDPOINT-LEVEL METRICS**")
        print("-" * 50)
        
        total_parameters = 0
        total_request_attributes = 0
        total_response_attributes = 0
        total_nested_attributes = 0
        
        for i, endpoint in enumerate(common_spec.endpoints):
            endpoint_metrics = {
                'endpoint_index': i,
                'path': endpoint['path'],
                'method': endpoint['method'],
                'parameter_count': len(endpoint['parameters']),
                'request_attribute_count': len(endpoint['request_body']['all_attributes']),
                'response_attribute_count': sum(len(resp['all_attributes']) for resp in endpoint['responses'].values()),
                'nested_attribute_count': sum(len(param.get('nested_attributes', [])) for param in endpoint['parameters']),
                'has_request_body': bool(endpoint['request_body']['all_attributes']),
                'response_count': len(endpoint['responses']),
                'searchable_content_length': len(endpoint['request_body']['searchable_content']) + 
                                           sum(len(resp['searchable_content']) for resp in endpoint['responses'].values())
            }
            
            metrics['endpoint_metrics'].append(endpoint_metrics)
            
            total_parameters += endpoint_metrics['parameter_count']
            total_request_attributes += endpoint_metrics['request_attribute_count']
            total_response_attributes += endpoint_metrics['response_attribute_count']
            total_nested_attributes += endpoint_metrics['nested_attribute_count']
            
            print(f"📍 Endpoint {i+1}: {endpoint['path']} ({endpoint['method']})")
            print(f"   📥 Parameters: {endpoint_metrics['parameter_count']}")
            print(f"   📋 Request Attributes: {endpoint_metrics['request_attribute_count']}")
            print(f"   📤 Response Attributes: {endpoint_metrics['response_attribute_count']}")
            print(f"   🔗 Nested Attributes: {endpoint_metrics['nested_attribute_count']}")
            print(f"   📄 Searchable Content: {endpoint_metrics['searchable_content_length']} chars")
            print()
        
        # 3. Attribute-Level Metrics
        print("\n📊 **3. ATTRIBUTE-LEVEL METRICS**")
        print("-" * 50)
        
        metrics['attribute_metrics'] = {
            'total_parameters': total_parameters,
            'total_request_attributes': total_request_attributes,
            'total_response_attributes': total_response_attributes,
            'total_nested_attributes': total_nested_attributes,
            'total_attributes': total_request_attributes + total_response_attributes + total_nested_attributes,
            'avg_attributes_per_endpoint': (total_request_attributes + total_response_attributes + total_nested_attributes) / len(common_spec.endpoints) if common_spec.endpoints else 0
        }
        
        print(f"📥 Total Parameters: {metrics['attribute_metrics']['total_parameters']}")
        print(f"📋 Total Request Attributes: {metrics['attribute_metrics']['total_request_attributes']}")
        print(f"📤 Total Response Attributes: {metrics['attribute_metrics']['total_response_attributes']}")
        print(f"🔗 Total Nested Attributes: {metrics['attribute_metrics']['total_nested_attributes']}")
        print(f"📊 Total Attributes: {metrics['attribute_metrics']['total_attributes']}")
        print(f"📈 Avg Attributes per Endpoint: {metrics['attribute_metrics']['avg_attributes_per_endpoint']:.2f}")
        
        # 4. Text Content Analysis
        print("\n📊 **4. TEXT CONTENT ANALYSIS**")
        print("-" * 50)
        
        all_text_content = []
        if common_spec.description:
            all_text_content.append(common_spec.description)
        
        for endpoint in common_spec.endpoints:
            all_text_content.append(endpoint['request_body']['searchable_content'])
            for response in endpoint['responses'].values():
                all_text_content.append(response['searchable_content'])
        
        combined_text = ' '.join(all_text_content)
        
        metrics['text_content_metrics'] = {
            'total_text_length': len(combined_text),
            'word_count': len(combined_text.split()),
            'unique_words': len(set(combined_text.lower().split())),
            'avg_word_length': sum(len(word) for word in combined_text.split()) / len(combined_text.split()) if combined_text.split() else 0,
            'text_density': len(combined_text) / metrics['attribute_metrics']['total_attributes'] if metrics['attribute_metrics']['total_attributes'] > 0 else 0,
            'has_meaningful_content': len(combined_text.strip()) > 100
        }
        
        print(f"📄 Total Text Length: {metrics['text_content_metrics']['total_text_length']} chars")
        print(f"📝 Word Count: {metrics['text_content_metrics']['word_count']}")
        print(f"🔤 Unique Words: {metrics['text_content_metrics']['unique_words']}")
        print(f"📏 Avg Word Length: {metrics['text_content_metrics']['avg_word_length']:.2f}")
        print(f"📊 Text Density: {metrics['text_content_metrics']['text_density']:.2f} chars/attribute")
        print(f"✅ Has Meaningful Content: {metrics['text_content_metrics']['has_meaningful_content']}")
        
        # 5. Embedding Preparation Metrics
        print("\n📊 **5. EMBEDDING PREPARATION METRICS**")
        print("-" * 50)
        
        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(combined_text) // 4
        
        metrics['embedding_preparation'] = {
            'estimated_tokens': estimated_tokens,
            'embedding_dimensions_needed': min(1536, max(384, len(combined_text) // 10)),  # Adaptive dimension sizing
            'chunking_recommended': len(combined_text) > 8000,  # OpenAI context limit consideration
            'optimal_chunk_size': min(512, max(128, len(combined_text) // 20)),
            'chunk_overlap_recommended': 50,
            'vector_db_storage_size': len(combined_text) * 2,  # Rough estimate including metadata
            'embedding_cost_estimate': estimated_tokens * 0.0001  # Rough OpenAI pricing
        }
        
        print(f"🎯 Estimated Tokens: {metrics['embedding_preparation']['estimated_tokens']}")
        print(f"📐 Recommended Embedding Dimensions: {metrics['embedding_preparation']['embedding_dimensions_needed']}")
        print(f"✂️  Chunking Recommended: {metrics['embedding_preparation']['chunking_recommended']}")
        print(f"📏 Optimal Chunk Size: {metrics['embedding_preparation']['optimal_chunk_size']}")
        print(f"🔄 Recommended Chunk Overlap: {metrics['embedding_preparation']['chunk_overlap_recommended']}")
        print(f"💾 Estimated Vector DB Storage: {metrics['embedding_preparation']['vector_db_storage_size']} bytes")
        print(f"💰 Estimated Embedding Cost: ${metrics['embedding_preparation']['embedding_cost_estimate']:.4f}")
        
        # 6. Quality Indicators
        print("\n📊 **6. QUALITY INDICATORS**")
        print("-" * 50)
        
        quality_score = 0
        max_score = 100
        
        # Check various quality factors
        if metrics['api_overview']['description_length'] > 50:
            quality_score += 15
        if metrics['attribute_metrics']['total_attributes'] > 0:
            quality_score += 20
        if metrics['text_content_metrics']['has_meaningful_content']:
            quality_score += 25
        if metrics['attribute_metrics']['total_nested_attributes'] > 0:
            quality_score += 15
        if metrics['api_overview']['has_namespaces']:
            quality_score += 10
        if metrics['endpoint_metrics'] and len(metrics['endpoint_metrics']) > 0:
            quality_score += 15
        
        metrics['quality_indicators'] = {
            'overall_quality_score': quality_score,
            'max_possible_score': max_score,
            'quality_percentage': (quality_score / max_score) * 100,
            'has_description': metrics['api_overview']['description_length'] > 0,
            'has_attributes': metrics['attribute_metrics']['total_attributes'] > 0,
            'has_nested_structure': metrics['attribute_metrics']['total_nested_attributes'] > 0,
            'has_namespaces': metrics['api_overview']['has_namespaces'],
            'is_ready_for_embedding': quality_score >= 60
        }
        
        print(f"⭐ Overall Quality Score: {quality_score}/{max_score} ({metrics['quality_indicators']['quality_percentage']:.1f}%)")
        print(f"📝 Has Description: {metrics['quality_indicators']['has_description']}")
        print(f"📋 Has Attributes: {metrics['quality_indicators']['has_attributes']}")
        print(f"🔗 Has Nested Structure: {metrics['quality_indicators']['has_nested_structure']}")
        print(f"🏗️  Has Namespaces: {metrics['quality_indicators']['has_namespaces']}")
        print(f"✅ Ready for Embedding: {metrics['quality_indicators']['is_ready_for_embedding']}")
        
        # 7. Recommendations
        print("\n📊 **7. RECOMMENDATIONS**")
        print("-" * 50)
        
        recommendations = []
        
        if not metrics['quality_indicators']['has_description']:
            recommendations.append("Add API description to improve searchability")
        
        if metrics['attribute_metrics']['total_attributes'] == 0:
            recommendations.append("No attributes found - check WSDL parsing")
        
        if metrics['text_content_metrics']['total_text_length'] < 100:
            recommendations.append("Very little text content - consider adding more descriptive information")
        
        if metrics['embedding_preparation']['chunking_recommended']:
            recommendations.append("Consider chunking for large content to optimize embedding performance")
        
        if metrics['quality_indicators']['quality_percentage'] < 60:
            recommendations.append("Quality score below 60% - review API specification completeness")
        
        if metrics['attribute_metrics']['total_nested_attributes'] == 0 and metrics['attribute_metrics']['total_attributes'] > 0:
            recommendations.append("Consider adding nested structures for better attribute organization")
        
        if not recommendations:
            recommendations.append("API specification looks good for vectorization!")
        
        metrics['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"💡 {i}. {rec}")
        
        print("\n" + "=" * 100)
        print("✅ **VECTORIZATION METRICS ANALYSIS COMPLETE**")
        print("=" * 100)
        
class APIConnectorManager:
    """Main manager for API connectors"""
    
    def __init__(self):
        self.swagger_connector = SwaggerConnector()
        self.wsdl_connector = WSDLConnector()
        self.chroma_client = None
        self.collection_name = "api_specifications"
        self.last_converted_spec = None
        self.last_metrics = None
        
    def load_environment(self):
        """Load environment variables"""
        load_dotenv()
        print("✅ Environment loaded successfully")
    
    def initialize_chromadb(self):
        """Initialize ChromaDB client"""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path="./chroma_db"
            )
            print("✅ ChromaDB initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {str(e)}")
            raise e
    
    def get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"✅ Using existing collection: {self.collection_name}")
            return collection
        except:
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "API specifications converted to common structure"}
            )
            print(f"✅ Created new collection: {self.collection_name}")
            return collection
    
    def convert_and_store(self, file_path: str, api_type: str = 'auto', metrics: bool = False) -> bool:
        """Convert API spec to common structure and store in ChromaDB"""
        
        try:
            # Initialize ChromaDB if not already done
            if self.chroma_client is None:
                self.initialize_chromadb()
            
            # Determine API type if auto
            if api_type == 'auto':
                api_type = self._detect_api_type(file_path)
            
            # Convert to common structure
            if api_type == 'swagger':
                common_spec = self.swagger_connector.parse_swagger_file(file_path)
            elif api_type == 'wsdl':
                common_spec = self.wsdl_connector.parse_wsdl_file(file_path)
            else:
                raise ValueError(f"Unsupported API type: {api_type}")
            
            # Display metrics if requested
            if metrics:
                if api_type == 'wsdl':
                    metrics_data = self.wsdl_connector.display_vectorization_metrics(common_spec)
                else:
                    metrics_data = self.swagger_connector.display_vectorization_metrics(common_spec)
                self.last_metrics = metrics_data
            
            # Store the last converted spec for API access
            self.last_converted_spec = common_spec
            
            # Store in ChromaDB
            return self._store_in_chromadb(common_spec)
            
        except Exception as e:
            print(f"❌ Error converting and storing {file_path}: {str(e)}")
            return False
    
    def convert_from_url(self, url: str, api_type: str = 'auto') -> bool:
        """Convert API spec from URL to common structure and store in ChromaDB"""
        
        try:
            # Determine API type if auto
            if api_type == 'auto':
                api_type = self._detect_api_type_from_url(url)
            
            # Convert to common structure
            if api_type == 'swagger':
                common_spec = self.swagger_connector.parse_swagger_url(url)
            elif api_type == 'wsdl':
                common_spec = self.wsdl_connector.parse_wsdl_url(url)
            else:
                raise ValueError(f"Unsupported API type: {api_type}")
            
            # Store in ChromaDB
            return self._store_in_chromadb(common_spec)
            
        except Exception as e:
            print(f"❌ Error converting and storing from URL {url}: {str(e)}")
            return False
    
    def _detect_api_type(self, file_path: str) -> str:
        """Detect API type from file extension and content"""
        
        if file_path.endswith(('.wsdl', '.xml')):
            return 'wsdl'
        elif file_path.endswith(('.json', '.yaml', '.yml')):
            return 'swagger'
        else:
            # Try to detect from content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1000 characters
                    
                if '<wsdl:' in content or '<definitions' in content:
                    return 'wsdl'
                elif '"swagger"' in content or '"openapi"' in content or 'swagger:' in content or 'openapi:' in content:
                    return 'swagger'
            except:
                pass
            
            return 'swagger'  # Default to swagger
    
    def _detect_api_type_from_url(self, url: str) -> str:
        """Detect API type from URL"""
        
        if url.endswith('.wsdl'):
            return 'wsdl'
        elif url.endswith(('.json', '.yaml', '.yml')):
            return 'swagger'
        else:
            return 'swagger'  # Default to swagger
    
    def _store_in_chromadb(self, common_spec: CommonAPISpec) -> bool:
        """Store common API spec in ChromaDB"""
        
        try:
            collection = self.get_or_create_collection()
            
            # Create comprehensive text representation for searchability
            doc_text = f"""
API: {common_spec.api_name}
Version: {common_spec.version}
Description: {common_spec.description}
Base URL: {common_spec.base_url}
Category: {common_spec.category}
Endpoints: {len(common_spec.endpoints)} endpoints
Authentication: {common_spec.authentication.get('type', 'none')}
Rate Limits: {common_spec.rate_limits.get('description', 'Not specified')}
SDK Languages: {', '.join(common_spec.sdk_languages)}
Integration Steps: {' '.join(common_spec.integration_steps)}
Best Practices: {' '.join(common_spec.best_practices)}
Use Cases: {' '.join(common_spec.common_use_cases)}
Tags: {', '.join(common_spec.tags)}
            """.strip()
            
            # Create JSON representation for detailed attribute searching
            doc_json = json.dumps(asdict(common_spec), indent=2)
            
            # Convert to dict for ChromaDB metadata
            metadata = asdict(common_spec)
            
            # Convert complex data structures to strings for ChromaDB
            for key, value in metadata.items():
                if value is None:
                    metadata[key] = ''
                elif isinstance(value, (list, dict)):
                    metadata[key] = json.dumps(value) if value else '[]'
                elif not isinstance(value, (str, int, float, bool)):
                    metadata[key] = str(value)
            
            # Generate unique ID
            api_id = f"api_{common_spec.api_name.lower().replace(' ', '_').replace('-', '_')}_{int(datetime.now().timestamp())}"
            
            # Add to ChromaDB
            collection.add(
                documents=[doc_json],
                metadatas=[metadata],
                ids=[api_id]
            )
            
            print(f"✅ Successfully converted and stored {common_spec.api_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error storing in ChromaDB: {str(e)}")
            return False
    
    def get_last_converted_spec(self):
        """Get the last converted CommonAPISpec"""
        return self.last_converted_spec
    
    def get_last_metrics(self):
        """Get the last metrics data"""
        return self.last_metrics
