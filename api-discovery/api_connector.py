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
import argparse
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
                        'parameters': operation.get('parameters', []),
                        'request_body': operation.get('requestBody', {}),
                        'responses': operation.get('responses', {}),
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
                        'parameters': operation.get('parameters', []),
                        'responses': operation.get('responses', {}),
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
        operations = root.findall('.//wsdl:operation', self.namespaces)
        
        for operation in operations:
            operation_name = operation.get('name', '')
            if operation_name:
                endpoint = {
                    'path': f"/{operation_name}",
                    'method': 'POST',  # SOAP typically uses POST
                    'summary': operation_name,
                    'description': '',
                    'parameters': [],
                    'request_body': {},
                    'responses': {},
                    'tags': ['soap'],
                    'operation_id': operation_name,
                    'deprecated': False,
                    'soap_action': self._extract_soap_action(operation)
                }
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_soap_action(self, operation: ET.Element) -> str:
        """Extract SOAP action from operation"""
        
        soap_operations = operation.findall('.//soap:operation', self.namespaces)
        if soap_operations:
            return soap_operations[0].get('soapAction', '')
        
        return ''
    
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
        """Extract type definitions from WSDL"""
        
        types_info = {
            'schemas': [],
            'elements': [],
            'complex_types': []
        }
        
        # Look for schema elements
        schemas = root.findall('.//xsd:schema', self.namespaces)
        for schema in schemas:
            schema_info = {
                'target_namespace': schema.get('targetNamespace', ''),
                'elements': [],
                'complex_types': []
            }
            
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

class APIConnectorManager:
    """Main manager for API connectors"""
    
    def __init__(self):
        self.swagger_connector = SwaggerConnector()
        self.wsdl_connector = WSDLConnector()
        self.chroma_client = None
        self.collection_name = "api_specifications"
        
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
            sys.exit(1)
    
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
    
    def convert_and_store(self, file_path: str, api_type: str = 'auto') -> bool:
        """Convert API spec to common structure and store in ChromaDB"""
        
        try:
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
            
            # Create comprehensive text representation
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
                documents=[doc_text],
                metadatas=[metadata],
                ids=[api_id]
            )
            
            print(f"✅ Successfully converted and stored {common_spec.api_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error storing in ChromaDB: {str(e)}")
            return False
    
    def list_stored_apis(self):
        """List all stored API specifications"""
        
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            count = collection.count()
            
            if count == 0:
                print("📭 No API specifications found in ChromaDB")
                return
            
            print(f"📚 Found {count} API specifications in ChromaDB:")
            print("=" * 80)
            
            # Get all documents
            results = collection.get()
            
            for i, (id, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
                api_name = metadata.get('api_name', 'Unknown')
                category = metadata.get('category', 'Unknown')
                version = metadata.get('version', 'Unknown')
                description = metadata.get('description', 'No description')
                
                print(f"{i+1:2d}. {api_name} (v{version})")
                print(f"     Category: {category}")
                print(f"     Description: {description[:100]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error listing APIs: {str(e)}")

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(
        description="🔗 CatalystAI API Connector - Convert Swagger/WSDL to common structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python api_connector.py convert swagger.json                    # Convert Swagger file
  python api_connector.py convert service.wsdl --type wsdl      # Convert WSDL file
  python api_connector.py convert-url https://api.example.com/swagger.json  # Convert from URL
  python api_connector.py list                                  # List stored APIs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert API specification file')
    convert_parser.add_argument('file_path', help='Path to API specification file')
    convert_parser.add_argument('--type', choices=['swagger', 'wsdl', 'auto'], default='auto',
                               help='API specification type (default: auto-detect)')
    
    # Convert URL command
    convert_url_parser = subparsers.add_parser('convert-url', help='Convert API specification from URL')
    convert_url_parser.add_argument('url', help='URL to API specification')
    convert_url_parser.add_argument('--type', choices=['swagger', 'wsdl', 'auto'], default='auto',
                                   help='API specification type (default: auto-detect)')
    
    # List command
    subparsers.add_parser('list', help='List all stored API specifications')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize the connector manager
    manager = APIConnectorManager()
    manager.load_environment()
    manager.initialize_chromadb()
    
    try:
        if args.command == 'convert':
            print(f"🔄 Converting API specification: {args.file_path}")
            success = manager.convert_and_store(args.file_path, args.type)
            if success:
                print("✅ API specification successfully converted and stored")
            else:
                print("❌ Failed to convert API specification")
                
        elif args.command == 'convert-url':
            print(f"🔄 Converting API specification from URL: {args.url}")
            success = manager.convert_from_url(args.url, args.type)
            if success:
                print("✅ API specification successfully converted and stored")
            else:
                print("❌ Failed to convert API specification")
                
        elif args.command == 'list':
            manager.list_stored_apis()
            
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
