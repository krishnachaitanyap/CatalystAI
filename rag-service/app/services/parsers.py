"""
Specialized parsers for different document types
Each parser extracts API information using domain-specific logic and LLM prompts
"""

import json
import yaml
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from app.services.parsers.base import DocumentParser
from app.models.requests import DocumentMetadata

class OpenAPIParser(DocumentParser):
    """Parser for OpenAPI/Swagger specifications"""
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse OpenAPI specification"""
        try:
            # Parse YAML/JSON content
            if content.strip().startswith('{'):
                spec = json.loads(content)
            else:
                spec = yaml.safe_load(content)
            
            # Extract API information
            api_info = {
                "title": spec.get("info", {}).get("title", "Unknown API"),
                "version": spec.get("info", {}).get("version", "1.0.0"),
                "description": spec.get("info", {}).get("description", ""),
                "base_url": spec.get("servers", [{}])[0].get("url", ""),
                "api_style": "REST",
                "endpoints": self._extract_openapi_endpoints(spec),
                "schemas": self._extract_schemas(spec),
                "security": self._extract_security(spec),
                "tags": spec.get("tags", []),
                "external_docs": spec.get("externalDocs", {}),
                "content": content
            }
            
            return api_info
            
        except Exception as e:
            logger.error(f"Error parsing OpenAPI spec: {str(e)}")
            raise
    
    def _extract_openapi_endpoints(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints from OpenAPI specification"""
        endpoints = []
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    endpoint = {
                        "method": method.upper(),
                        "path": path,
                        "operation_id": operation.get("operationId", f"{method}_{path.replace('/', '_')}"),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody", {}),
                        "responses": operation.get("responses", {}),
                        "tags": operation.get("tags", []),
                        "security": operation.get("security", []),
                        "deprecated": operation.get("deprecated", False),
                        "pii_flagged": self._check_pii_indicators(operation),
                        "rate_limit": self._extract_rate_limit(operation)
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_schemas(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data schemas"""
        return spec.get("components", {}).get("schemas", {})
    
    def _extract_security(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract security definitions"""
        return spec.get("components", {}).get("securitySchemes", {})
    
    def _check_pii_indicators(self, operation: Dict[str, Any]) -> bool:
        """Check if operation handles PII data"""
        pii_keywords = [
            'password', 'ssn', 'credit_card', 'email', 'phone', 'address',
            'personal', 'private', 'sensitive', 'confidential'
        ]
        
        operation_text = json.dumps(operation).lower()
        return any(keyword in operation_text for keyword in pii_keywords)
    
    def _extract_rate_limit(self, operation: Dict[str, Any]) -> Optional[int]:
        """Extract rate limiting information"""
        # Check for rate limiting in extensions or descriptions
        extensions = operation.get("x-", {})
        if "rateLimit" in extensions:
            return extensions["rateLimit"]
        return None

class GraphQLParser(DocumentParser):
    """Parser for GraphQL schemas"""
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse GraphQL schema"""
        try:
            # Extract GraphQL types and operations
            api_info = {
                "title": "GraphQL API",
                "version": "1.0.0",
                "description": "GraphQL API Schema",
                "api_style": "GraphQL",
                "types": self._extract_graphql_types(content),
                "queries": self._extract_queries(content),
                "mutations": self._extract_mutations(content),
                "subscriptions": self._extract_subscriptions(content),
                "directives": self._extract_directives(content),
                "content": content
            }
            
            return api_info
            
        except Exception as e:
            logger.error(f"Error parsing GraphQL schema: {str(e)}")
            raise
    
    def _extract_graphql_types(self, content: str) -> List[Dict[str, Any]]:
        """Extract GraphQL type definitions"""
        types = []
        type_pattern = r'type\s+(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(type_pattern, content, re.MULTILINE):
            type_name = match.group(1)
            type_body = match.group(2)
            fields = self._extract_fields(type_body)
            
            types.append({
                "name": type_name,
                "fields": fields,
                "description": self._extract_description(content, match.start())
            })
        
        return types
    
    def _extract_queries(self, content: str) -> List[Dict[str, Any]]:
        """Extract GraphQL queries"""
        queries = []
        query_pattern = r'type\s+Query\s*\{([^}]+)\}'
        
        match = re.search(query_pattern, content, re.MULTILINE)
        if match:
            query_body = match.group(1)
            queries = self._extract_fields(query_body)
        
        return queries
    
    def _extract_mutations(self, content: str) -> List[Dict[str, Any]]:
        """Extract GraphQL mutations"""
        mutations = []
        mutation_pattern = r'type\s+Mutation\s*\{([^}]+)\}'
        
        match = re.search(mutation_pattern, content, re.MULTILINE)
        if match:
            mutation_body = match.group(1)
            mutations = self._extract_fields(mutation_body)
        
        return mutations
    
    def _extract_subscriptions(self, content: str) -> List[Dict[str, Any]]:
        """Extract GraphQL subscriptions"""
        subscriptions = []
        subscription_pattern = r'type\s+Subscription\s*\{([^}]+)\}'
        
        match = re.search(subscription_pattern, content, re.MULTILINE)
        if match:
            subscription_body = match.group(1)
            subscriptions = self._extract_fields(subscription_body)
        
        return subscriptions
    
    def _extract_fields(self, body: str) -> List[Dict[str, Any]]:
        """Extract fields from GraphQL type body"""
        fields = []
        field_pattern = r'(\w+)\s*:\s*([^,\n]+)'
        
        for match in re.finditer(field_pattern, body):
            field_name = match.group(1)
            field_type = match.group(2).strip()
            
            fields.append({
                "name": field_name,
                "type": field_type,
                "description": self._extract_field_description(body, match.start())
            })
        
        return fields
    
    def _extract_directives(self, content: str) -> List[str]:
        """Extract GraphQL directives"""
        directive_pattern = r'directive\s+@(\w+)'
        return re.findall(directive_pattern, content)
    
    def _extract_description(self, content: str, position: int) -> str:
        """Extract description for a GraphQL element"""
        # Look for comments above the element
        lines = content[:position].split('\n')
        description_lines = []
        
        for line in reversed(lines):
            line = line.strip()
            if line.startswith('#'):
                description_lines.insert(0, line[1:].strip())
            elif line.startswith('"""'):
                # Multi-line description
                description_lines.insert(0, line[3:].strip())
            elif line and not line.startswith('type'):
                break
        
        return ' '.join(description_lines)
    
    def _extract_field_description(self, body: str, position: int) -> str:
        """Extract description for a field"""
        # Similar to _extract_description but for fields
        return ""

class SOAPParser(DocumentParser):
    """Parser for SOAP/WSDL specifications"""
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse SOAP/WSDL specification"""
        try:
            # Extract SOAP operations and messages
            api_info = {
                "title": "SOAP API",
                "version": "1.0.0",
                "description": "SOAP Web Service",
                "api_style": "SOAP",
                "operations": self._extract_soap_operations(content),
                "messages": self._extract_soap_messages(content),
                "types": self._extract_soap_types(content),
                "bindings": self._extract_soap_bindings(content),
                "services": self._extract_soap_services(content),
                "content": content
            }
            
            return api_info
            
        except Exception as e:
            logger.error(f"Error parsing SOAP/WSDL: {str(e)}")
            raise
    
    def _extract_soap_operations(self, content: str) -> List[Dict[str, Any]]:
        """Extract SOAP operations from WSDL"""
        operations = []
        operation_pattern = r'<wsdl:operation\s+name="([^"]+)"[^>]*>'
        
        for match in re.finditer(operation_pattern, content):
            operation_name = match.group(1)
            operation_content = self._extract_operation_content(content, match.start())
            
            operations.append({
                "name": operation_name,
                "input": self._extract_operation_io(operation_content, "input"),
                "output": self._extract_operation_io(operation_content, "output"),
                "fault": self._extract_operation_io(operation_content, "fault"),
                "description": self._extract_operation_description(operation_content)
            })
        
        return operations
    
    def _extract_soap_messages(self, content: str) -> List[Dict[str, Any]]:
        """Extract SOAP message definitions"""
        messages = []
        message_pattern = r'<wsdl:message\s+name="([^"]+)"[^>]*>([^<]+)</wsdl:message>'
        
        for match in re.finditer(message_pattern, content):
            message_name = match.group(1)
            message_body = match.group(2)
            
            messages.append({
                "name": message_name,
                "parts": self._extract_message_parts(message_body),
                "description": self._extract_message_description(message_body)
            })
        
        return messages
    
    def _extract_soap_types(self, content: str) -> List[Dict[str, Any]]:
        """Extract SOAP type definitions"""
        types = []
        type_pattern = r'<xsd:complexType\s+name="([^"]+)"[^>]*>([^<]+)</xsd:complexType>'
        
        for match in re.finditer(type_pattern, content):
            type_name = match.group(1)
            type_body = match.group(2)
            
            types.append({
                "name": type_name,
                "elements": self._extract_type_elements(type_body),
                "description": self._extract_type_description(type_body)
            })
        
        return types
    
    def _extract_soap_bindings(self, content: str) -> List[Dict[str, Any]]:
        """Extract SOAP bindings"""
        bindings = []
        binding_pattern = r'<wsdl:binding\s+name="([^"]+)"[^>]*>([^<]+)</wsdl:binding>'
        
        for match in re.finditer(binding_pattern, content):
            binding_name = match.group(1)
            binding_body = match.group(2)
            
            bindings.append({
                "name": binding_name,
                "protocol": self._extract_binding_protocol(binding_body),
                "operations": self._extract_binding_operations(binding_body)
            })
        
        return bindings
    
    def _extract_soap_services(self, content: str) -> List[Dict[str, Any]]:
        """Extract SOAP service definitions"""
        services = []
        service_pattern = r'<wsdl:service\s+name="([^"]+)"[^>]*>([^<]+)</wsdl:service>'
        
        for match in re.finditer(service_pattern, content):
            service_name = match.group(1)
            service_body = match.group(2)
            
            services.append({
                "name": service_name,
                "ports": self._extract_service_ports(service_body),
                "description": self._extract_service_description(service_body)
            })
        
        return services
    
    def _extract_operation_content(self, content: str, start_pos: int) -> str:
        """Extract content for a specific operation"""
        # Find the end of the operation block
        brace_count = 0
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '<':
                brace_count += 1
            elif char == '>':
                brace_count -= 1
                if brace_count == 0:
                    return content[start_pos:i+1]
        return ""
    
    def _extract_operation_io(self, operation_content: str, io_type: str) -> Optional[str]:
        """Extract input/output/fault information"""
        pattern = f'<wsdl:{io_type}[^>]*>([^<]+)</wsdl:{io_type}>'
        match = re.search(pattern, operation_content)
        return match.group(1) if match else None
    
    def _extract_message_parts(self, message_body: str) -> List[Dict[str, str]]:
        """Extract message parts"""
        parts = []
        part_pattern = r'<wsdl:part\s+name="([^"]+)"\s+type="([^"]+)"[^>]*/>'
        
        for match in re.finditer(part_pattern, message_body):
            parts.append({
                "name": match.group(1),
                "type": match.group(2)
            })
        
        return parts
    
    def _extract_type_elements(self, type_body: str) -> List[Dict[str, str]]:
        """Extract type elements"""
        elements = []
        element_pattern = r'<xsd:element\s+name="([^"]+)"\s+type="([^"]+)"[^>]*/>'
        
        for match in re.finditer(element_pattern, type_body):
            elements.append({
                "name": match.group(1),
                "type": match.group(2)
            })
        
        return elements
    
    def _extract_binding_protocol(self, binding_body: str) -> str:
        """Extract binding protocol"""
        protocol_pattern = r'soap:binding\s+style="([^"]+)"\s+transport="([^"]+)"'
        match = re.search(protocol_pattern, binding_body)
        return f"{match.group(1)} - {match.group(2)}" if match else "Unknown"
    
    def _extract_binding_operations(self, binding_body: str) -> List[str]:
        """Extract binding operations"""
        operations = []
        operation_pattern = r'<wsdl:operation\s+name="([^"]+)"[^>]*>'
        
        for match in re.finditer(operation_pattern, binding_body):
            operations.append(match.group(1))
        
        return operations
    
    def _extract_service_ports(self, service_body: str) -> List[Dict[str, str]]:
        """Extract service ports"""
        ports = []
        port_pattern = r'<wsdl:port\s+name="([^"]+)"\s+binding="([^"]+)"[^>]*>([^<]+)</wsdl:port>'
        
        for match in re.finditer(port_pattern, service_body):
            port_name = match.group(1)
            binding = match.group(2)
            port_body = match.group(3)
            
            # Extract address
            address_match = re.search(r'<soap:address\s+location="([^"]+)"[^>]*/>', port_body)
            address = address_match.group(1) if address_match else ""
            
            ports.append({
                "name": port_name,
                "binding": binding,
                "address": address
            })
        
        return ports
    
    def _extract_operation_description(self, operation_content: str) -> str:
        """Extract operation description"""
        # Look for documentation or comments
        doc_pattern = r'<wsdl:documentation[^>]*>([^<]+)</wsdl:documentation>'
        match = re.search(doc_pattern, operation_content)
        return match.group(1).strip() if match else ""
    
    def _extract_message_description(self, message_body: str) -> str:
        """Extract message description"""
        return ""
    
    def _extract_type_description(self, type_body: str) -> str:
        """Extract type description"""
        return ""
    
    def _extract_service_description(self, service_body: str) -> str:
        """Extract service description"""
        return ""

class MarkdownParser(DocumentParser):
    """Parser for Markdown/Confluence documentation"""
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse Markdown documentation for API information"""
        try:
            # Extract API information from markdown
            api_info = {
                "title": self._extract_title(content),
                "version": "1.0.0",
                "description": self._extract_description(content),
                "api_style": "REST",  # Default for markdown docs
                "endpoints": self._extract_markdown_endpoints(content),
                "code_examples": self._extract_code_examples(content),
                "tables": self._extract_tables(content),
                "links": self._extract_links(content),
                "content": content
            }
            
            return api_info
            
        except Exception as e:
            logger.error(f"Error parsing Markdown: {str(e)}")
            raise
    
    def _extract_title(self, content: str) -> str:
        """Extract document title"""
        # Look for first H1 heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return title_match.group(1).strip() if title_match else "Markdown API Documentation"
    
    def _extract_description(self, content: str) -> str:
        """Extract document description"""
        # Look for description after title
        lines = content.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('#') or line.startswith('---'):
                continue
            if line and not line.startswith('```'):
                description_lines.append(line)
            if len(description_lines) >= 3:  # Take first few lines
                break
        
        return ' '.join(description_lines)
    
    def _extract_markdown_endpoints(self, content: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from markdown"""
        endpoints = []
        
        # Look for common API documentation patterns
        patterns = [
            # Method + Path pattern
            r'(GET|POST|PUT|DELETE|PATCH)\s+`([^`]+)`',
            # Code block with HTTP method
            r'```(?:http|bash|curl)\s*\n(?:GET|POST|PUT|DELETE|PATCH)\s+([^\s]+)',
            # Table rows with endpoint information
            r'\|.*(GET|POST|PUT|DELETE|PATCH).*\|.*`([^`]+)`',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                method = match.group(1).upper()
                path = match.group(2) if len(match.groups()) > 1 else match.group(1)
                
                # Extract context around the endpoint
                context = self._extract_context(content, match.start(), 200)
                
                endpoints.append({
                    "method": method,
                    "path": path,
                    "description": self._extract_endpoint_description(context),
                    "confidence": 0.8,
                    "source": "markdown_pattern"
                })
        
        return endpoints
    
    def _extract_code_examples(self, content: str) -> List[Dict[str, Any]]:
        """Extract code examples from markdown"""
        examples = []
        code_block_pattern = r'```(\w+)\s*\n([^`]+)\n```'
        
        for match in re.finditer(code_block_pattern, content, re.MULTILINE):
            language = match.group(1)
            code = match.group(2)
            
            examples.append({
                "language": language,
                "code": code.strip(),
                "description": self._extract_code_description(content, match.start())
            })
        
        return examples
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract tables from markdown"""
        tables = []
        table_pattern = r'\|(.+)\|\n\|([-:\s|]+)\|\n((?:\|.+\|\n?)+)'
        
        for match in re.finditer(table_pattern, content, re.MULTILINE):
            headers = [h.strip() for h in match.group(1).split('|')]
            rows = []
            
            for row_match in re.finditer(r'\|(.+)\|', match.group(3)):
                row_data = [cell.strip() for cell in row_match.group(1).split('|')]
                if len(row_data) == len(headers):
                    rows.append(dict(zip(headers, row_data)))
            
            if rows:
                tables.append({
                    "headers": headers,
                    "rows": rows
                })
        
        return tables
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from markdown"""
        links = []
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            links.append({
                "text": match.group(1),
                "url": match.group(2)
            })
        
        return links
    
    def _extract_endpoint_description(self, context: str) -> str:
        """Extract description for an endpoint from context"""
        # Look for description text around the endpoint
        lines = context.split('\n')
        description_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('`') and not line.startswith('|'):
                description_lines.append(line)
            if len(description_lines) >= 2:
                break
        
        return ' '.join(description_lines)
    
    def _extract_code_description(self, content: str, position: int) -> str:
        """Extract description for code block"""
        # Look for text before the code block
        before_content = content[:position]
        lines = before_content.split('\n')
        
        for line in reversed(lines):
            line = line.strip()
            if line and not line.startswith('```'):
                return line
        return ""

class PostmanParser(DocumentParser):
    """Parser for Postman collections"""
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse Postman collection"""
        try:
            collection = json.loads(content)
            
            api_info = {
                "title": collection.get("info", {}).get("name", "Postman Collection"),
                "version": collection.get("info", {}).get("schema", "2.1.0"),
                "description": collection.get("info", {}).get("description", ""),
                "api_style": "REST",
                "endpoints": self._extract_postman_endpoints(collection),
                "environments": collection.get("variable", []),
                "auth": collection.get("auth", {}),
                "content": content
            }
            
            return api_info
            
        except Exception as e:
            logger.error(f"Error parsing Postman collection: {str(e)}")
            raise
    
    def _extract_postman_endpoints(self, collection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints from Postman collection"""
        endpoints = []
        
        def process_items(items):
            for item in items:
                if "request" in item:
                    request = item["request"]
                    endpoint = {
                        "method": request.get("method", "GET"),
                        "path": request.get("url", {}).get("path", []),
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "headers": request.get("header", []),
                        "body": request.get("body", {}),
                        "auth": request.get("auth", {}),
                        "tests": item.get("event", [])
                    }
                    endpoints.append(endpoint)
                
                if "item" in item:
                    process_items(item["item"])
        
        process_items(collection.get("item", []))
        return endpoints

class HARParser(DocumentParser):
    """Parser for HTTP Archive (HAR) files"""
    
    async def parse(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """Parse HAR file"""
        try:
            har_data = json.loads(content)
            
            api_info = {
                "title": "HAR API Traces",
                "version": "1.0.0",
                "description": "API endpoints extracted from HTTP Archive",
                "api_style": "REST",
                "endpoints": self._extract_har_endpoints(har_data),
                "total_requests": len(har_data.get("log", {}).get("entries", [])),
                "time_range": self._extract_time_range(har_data),
                "content": content
            }
            
            return api_info
            
        except Exception as e:
            logger.error(f"Error parsing HAR file: {str(e)}")
            raise
    
    def _extract_har_endpoints(self, har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints from HAR data"""
        endpoints = []
        entries = har_data.get("log", {}).get("entries", [])
        
        for entry in entries:
            request = entry.get("request", {})
            response = entry.get("response", {})
            
            endpoint = {
                "method": request.get("method", "GET"),
                "path": request.get("url", ""),
                "status_code": response.get("status", 0),
                "response_time": entry.get("time", 0),
                "headers": request.get("headers", []),
                "query_string": request.get("queryString", []),
                "post_data": request.get("postData", {}),
                "content_type": response.get("content", {}).get("mimeType", ""),
                "content_size": response.get("content", {}).get("size", 0)
            }
            endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_time_range(self, har_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract time range from HAR data"""
        entries = har_data.get("log", {}).get("entries", [])
        if not entries:
            return {}
        
        start_time = entries[0].get("startedDateTime", "")
        end_time = entries[-1].get("startedDateTime", "")
        
        return {
            "start": start_time,
            "end": end_time,
            "duration": self._calculate_duration(start_time, end_time)
        }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between two ISO timestamps"""
        try:
            from datetime import datetime
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except:
            return 0.0
