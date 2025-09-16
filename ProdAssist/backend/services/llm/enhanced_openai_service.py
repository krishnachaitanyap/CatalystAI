"""
Enhanced OpenAI Service with Advanced Capabilities
Optimized for API specification analysis and chat responses
"""
import openai
from typing import Optional, Dict, Any, List, Union
import json
import tiktoken
import asyncio
from datetime import datetime

from config.settings import settings
from models.schemas.schemas import LLMRequest, LLMResponse
from utils.logging import LoggerMixin


class EnhancedOpenAIService(LoggerMixin):
    """Enhanced OpenAI service with advanced API specification capabilities"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # System prompts for different tasks
        self.system_prompts = {
            'api_analysis': self._get_api_analysis_prompt(),
            'code_generation': self._get_code_generation_prompt(),
            'chat_assistant': self._get_chat_assistant_prompt(),
            'api_documentation': self._get_api_documentation_prompt(),
            'troubleshooting': self._get_troubleshooting_prompt()
        }
    
    def _get_api_analysis_prompt(self) -> str:
        """System prompt for API analysis tasks"""
        return """You are an expert API analyst specializing in SOAP and REST API specifications. 
Your role is to analyze API specifications and provide detailed insights about:

1. API Design Quality: Evaluate the overall design patterns, consistency, and best practices
2. Security Analysis: Identify potential security issues and recommendations
3. Performance Considerations: Analyze potential performance bottlenecks
4. Documentation Quality: Assess completeness and clarity of API documentation
5. Integration Patterns: Suggest optimal integration approaches
6. Error Handling: Review error handling strategies and suggest improvements

Always provide specific, actionable recommendations with examples when possible."""
    
    def _get_code_generation_prompt(self) -> str:
        """System prompt for code generation tasks"""
        return """You are an expert software developer specializing in API integration and development.
Your role is to generate high-quality, production-ready code examples for API specifications.

Guidelines:
1. Use modern, best-practice coding patterns
2. Include proper error handling and validation
3. Add comprehensive comments and documentation
4. Follow language-specific conventions and idioms
5. Include examples for different scenarios (success, error, edge cases)
6. Provide both synchronous and asynchronous examples when applicable
7. Include proper logging and monitoring

Always generate complete, runnable code examples with clear explanations."""
    
    def _get_chat_assistant_prompt(self) -> str:
        """System prompt for chat assistant tasks"""
        return """You are ProdAssist, an AI assistant specialized in helping developers work with API specifications.
You can help with:

- Explaining API endpoints and their usage
- Generating code examples in multiple languages
- Troubleshooting API integration issues
- Providing best practices for API development
- Analyzing API specifications for improvements
- Security recommendations and compliance
- Performance optimization suggestions

Always provide clear, accurate, and helpful responses. When referencing API specifications, be specific about endpoints, parameters, and expected responses. Use markdown formatting for better readability."""
    
    def _get_api_documentation_prompt(self) -> str:
        """System prompt for API documentation tasks"""
        return """You are an expert technical writer specializing in API documentation.
Your role is to create comprehensive, clear, and user-friendly API documentation.

Guidelines:
1. Use clear, concise language accessible to developers of all levels
2. Include practical examples and use cases
3. Provide step-by-step tutorials when appropriate
4. Include troubleshooting sections
5. Use consistent formatting and structure
6. Include interactive examples and code snippets
7. Cover authentication, error handling, and rate limiting

Focus on making complex API concepts accessible and actionable."""
    
    def _get_troubleshooting_prompt(self) -> str:
        """System prompt for troubleshooting tasks"""
        return """You are an expert API troubleshooting specialist with deep knowledge of common integration issues.
Your role is to help developers diagnose and resolve API-related problems.

Approach:
1. Analyze error messages and symptoms systematically
2. Consider common causes and edge cases
3. Provide step-by-step debugging procedures
4. Suggest preventive measures
5. Include relevant code examples and solutions
6. Consider different environments and configurations

Always provide actionable solutions with clear explanations of the root cause."""
    
    def generate_response(
        self, 
        request: LLMRequest,
        task_type: str = 'chat_assistant',
        api_specs: Optional[List[Dict[str, Any]]] = None,
        search_context: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        """Generate enhanced LLM response with context and task-specific prompting"""
        
        try:
            # Get task-specific system prompt
            system_prompt = self.system_prompts.get(task_type, self.system_prompts['chat_assistant'])
            
            # Build enhanced context
            enhanced_context = self._build_enhanced_context(
                api_specs, 
                search_context, 
                request.context
            )
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._build_user_message(request, enhanced_context)}
            ]
            
            # Add context if available
            if enhanced_context:
                context_message = self._format_context_message(enhanced_context)
                messages.append({"role": "user", "content": context_message})
            
            # Make API call with enhanced parameters
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature or self.temperature,
                max_tokens=request.max_tokens or self.max_tokens,
                stream=False,
                # Enhanced parameters for better responses
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            # Extract response
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Extract chain of thought if requested
            chain_of_thought = None
            if request.include_chain_of_thought:
                chain_of_thought = self._extract_chain_of_thought(content)
                if chain_of_thought:
                    content = content.replace(f"Chain of Thought: {chain_of_thought}", "").strip()
            
            self.logger.info(f"✅ Generated {task_type} response - Tokens used: {tokens_used}")
            
            return LLMResponse(
                response=content,
                chain_of_thought=chain_of_thought,
                tokens_used=tokens_used,
                model_used=self.model
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error generating LLM response: {str(e)}")
            raise
    
    def _build_enhanced_context(
        self, 
        api_specs: Optional[List[Dict[str, Any]]], 
        search_context: Optional[List[Dict[str, Any]]],
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build enhanced context from multiple sources"""
        
        context = {
            'api_specifications': [],
            'search_results': [],
            'user_context': user_context or {},
            'context_timestamp': datetime.utcnow().isoformat()
        }
        
        # Add API specifications context
        if api_specs:
            for spec in api_specs:
                spec_context = {
                    'id': spec.get('id'),
                    'name': spec.get('name'),
                    'api_type': spec.get('api_type'),
                    'description': spec.get('description'),
                    'seal_id': spec.get('seal_id'),
                    'application': spec.get('application'),
                    'endpoint_count': len(spec.get('endpoints', [])),
                    'data_type_count': len(spec.get('data_types', []))
                }
                context['api_specifications'].append(spec_context)
        
        # Add search results context
        if search_context:
            for result in search_context:
                result_context = {
                    'content_preview': result.get('content', '')[:200] + '...' if len(result.get('content', '')) > 200 else result.get('content', ''),
                    'metadata': result.get('metadata', {}),
                    'score': result.get('score', 0.0),
                    'collection': result.get('collection', '')
                }
                context['search_results'].append(result_context)
        
        return context
    
    def _build_user_message(self, request: LLMRequest, context: Dict[str, Any]) -> str:
        """Build enhanced user message"""
        message = request.message
        
        # Add task-specific instructions
        if request.include_chain_of_thought:
            message += "\n\nPlease provide your reasoning process (Chain of Thought) before giving the final answer."
        
        # Add context hints
        if context.get('api_specifications'):
            message += f"\n\nAvailable API specifications: {len(context['api_specifications'])}"
        
        if context.get('search_results'):
            message += f"\n\nRelevant search results: {len(context['search_results'])}"
        
        return message
    
    def _format_context_message(self, context: Dict[str, Any]) -> str:
        """Format context as a structured message"""
        context_parts = []
        
        # Add API specifications
        if context.get('api_specifications'):
            context_parts.append("## Available API Specifications:")
            for spec in context['api_specifications']:
                context_parts.append(f"- {spec['name']} ({spec['api_type']}): {spec['description']}")
                context_parts.append(f"  - Seal ID: {spec['seal_id']}, Application: {spec['application']}")
                context_parts.append(f"  - Endpoints: {spec['endpoint_count']}, Data Types: {spec['data_type_count']}")
        
        # Add search results
        if context.get('search_results'):
            context_parts.append("\n## Relevant Search Results:")
            for i, result in enumerate(context['search_results'][:5], 1):  # Limit to top 5
                context_parts.append(f"{i}. {result['content_preview']}")
                context_parts.append(f"   Source: {result['collection']}, Score: {result['score']:.3f}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _extract_chain_of_thought(self, content: str) -> Optional[str]:
        """Extract chain of thought from response"""
        if "Chain of Thought:" in content:
            parts = content.split("Chain of Thought:", 1)
            if len(parts) > 1:
                cot_part = parts[1].split("\n\n", 1)[0]
                return cot_part.strip()
        return None
    
    def analyze_api_specification(self, api_spec: Dict[str, Any]) -> str:
        """Analyze API specification and provide detailed insights"""
        
        analysis_prompt = f"""Analyze the following API specification and provide comprehensive insights:

API Name: {api_spec.get('api_name', 'Unknown')}
Type: {api_spec.get('api_type', 'Unknown')}
Version: {api_spec.get('version', 'Unknown')}
Description: {api_spec.get('description', 'No description')}
Endpoints: {len(api_spec.get('endpoints', []))}
Data Types: {len(api_spec.get('data_types', []))}

Please provide:
1. Overall assessment of the API design
2. Security considerations and recommendations
3. Performance implications
4. Documentation quality assessment
5. Integration best practices
6. Potential improvements

Be specific and provide actionable recommendations."""
        
        request = LLMRequest(
            message=analysis_prompt,
            include_chain_of_thought=True
        )
        
        response = self.generate_response(request, task_type='api_analysis')
        return response.response
    
    def generate_code_example(
        self, 
        endpoint: Dict[str, Any], 
        language: str = "python",
        scenario: str = "basic"
    ) -> str:
        """Generate code example for an API endpoint"""
        
        code_prompt = f"""Generate a {language} code example for the following API endpoint:

Endpoint: {endpoint.get('path', 'Unknown')}
Method: {endpoint.get('method', 'Unknown')}
Description: {endpoint.get('description', 'No description')}
Operation: {endpoint.get('operation_name', 'Unknown')}

Scenario: {scenario}

Please provide:
1. A complete, working example
2. Proper error handling
3. Clear comments and documentation
4. Example request/response data
5. Best practices for this specific endpoint

Make the code production-ready and include all necessary imports and dependencies."""
        
        request = LLMRequest(
            message=code_prompt,
            include_chain_of_thought=True
        )
        
        response = self.generate_response(request, task_type='code_generation')
        return response.response
    
    def generate_api_documentation(self, api_spec: Dict[str, Any]) -> str:
        """Generate comprehensive API documentation"""
        
        doc_prompt = f"""Generate comprehensive API documentation for:

API Name: {api_spec.get('api_name', 'Unknown')}
Type: {api_spec.get('api_type', 'Unknown')}
Description: {api_spec.get('description', 'No description')}
Base URL: {api_spec.get('base_url', 'Not specified')}

Please create documentation that includes:
1. API Overview and Introduction
2. Authentication and Authorization
3. Rate Limiting and Usage Guidelines
4. Endpoint Documentation with Examples
5. Data Types and Schemas
6. Error Handling and Status Codes
7. Integration Examples
8. Troubleshooting Guide

Use clear, professional language suitable for developer documentation."""
        
        request = LLMRequest(
            message=doc_prompt,
            include_chain_of_thought=True
        )
        
        response = self.generate_response(request, task_type='api_documentation')
        return response.response
    
    def troubleshoot_api_issue(self, error_description: str, api_spec: Dict[str, Any]) -> str:
        """Provide troubleshooting assistance for API issues"""
        
        troubleshooting_prompt = f"""Help troubleshoot the following API issue:

Error Description: {error_description}

API Context:
- API Name: {api_spec.get('api_name', 'Unknown')}
- Type: {api_spec.get('api_type', 'Unknown')}
- Endpoints: {len(api_spec.get('endpoints', []))}

Please provide:
1. Potential root causes
2. Step-by-step debugging procedure
3. Common solutions and workarounds
4. Prevention strategies
5. Relevant code examples for testing

Be systematic and provide actionable solutions."""
        
        request = LLMRequest(
            message=troubleshooting_prompt,
            include_chain_of_thought=True
        )
        
        response = self.generate_response(request, task_type='troubleshooting')
        return response.response
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage"""
        # GPT-4 pricing (as of 2024)
        input_cost_per_1k = 0.03
        output_cost_per_1k = 0.06
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'tokenizer': self.tokenizer.name if hasattr(self.tokenizer, 'name') else 'cl100k_base',
            'available_tasks': list(self.system_prompts.keys())
        }
