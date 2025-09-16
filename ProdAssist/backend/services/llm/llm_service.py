"""
LLM service for integrating with OpenAI and other language models
"""
import openai
from typing import Optional, Dict, Any, List
import json
import tiktoken

from config.settings import settings
from models.schemas.schemas import LLMRequest, LLMResponse
from utils.logging import LoggerMixin


class LLMService(LoggerMixin):
    """Service for LLM operations"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.model)
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def generate_response(
        self, 
        request: LLMRequest,
        api_specs: Optional[List[Dict[str, Any]]] = None
    ) -> LLMResponse:
        """Generate LLM response with optional API specification context"""
        
        try:
            # Build system prompt with API context
            system_prompt = self._build_system_prompt(api_specs)
            
            # Build user message with context
            user_message = self._build_user_message(request)
            
            # Prepare messages for API call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Add context if provided
            if request.context:
                context_message = f"Additional context: {json.dumps(request.context, indent=2)}"
                messages.append({"role": "user", "content": context_message})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature or self.temperature,
                max_tokens=request.max_tokens or self.max_tokens,
                stream=False
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
            
            self.logger.info(f"✅ Generated LLM response - Tokens used: {tokens_used}")
            
            return LLMResponse(
                response=content,
                chain_of_thought=chain_of_thought,
                tokens_used=tokens_used,
                model_used=self.model
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error generating LLM response: {str(e)}")
            raise
    
    def _build_system_prompt(self, api_specs: Optional[List[Dict[str, Any]]]) -> str:
        """Build system prompt with API specifications context"""
        
        base_prompt = """You are ProdAssist, an AI assistant specialized in helping developers work with API specifications. 
You can help with:
- Explaining API endpoints and their usage
- Generating code examples
- Troubleshooting API issues
- Providing best practices for API development
- Analyzing API specifications for improvements

Always provide clear, accurate, and helpful responses. When referencing API specifications, be specific about endpoints, parameters, and expected responses."""

        if api_specs:
            api_context = "\n\nAvailable API Specifications:\n"
            for spec in api_specs:
                api_context += f"- {spec.get('name', 'Unknown')} ({spec.get('api_type', 'Unknown')}): {spec.get('description', 'No description')}\n"
            
            base_prompt += api_context
        
        return base_prompt
    
    def _build_user_message(self, request: LLMRequest) -> str:
        """Build user message from request"""
        message = request.message
        
        if request.include_chain_of_thought:
            message += "\n\nPlease provide your reasoning process (Chain of Thought) before giving the final answer."
        
        return message
    
    def _extract_chain_of_thought(self, content: str) -> Optional[str]:
        """Extract chain of thought from LLM response"""
        if "Chain of Thought:" in content:
            parts = content.split("Chain of Thought:", 1)
            if len(parts) > 1:
                cot_part = parts[1].split("\n\n", 1)[0]
                return cot_part.strip()
        return None
    
    def generate_code_example(
        self, 
        endpoint: Dict[str, Any], 
        language: str = "python"
    ) -> str:
        """Generate code example for an API endpoint"""
        
        prompt = f"""Generate a {language} code example for the following API endpoint:

Endpoint: {endpoint.get('path', 'Unknown')}
Method: {endpoint.get('method', 'Unknown')}
Description: {endpoint.get('description', 'No description')}

Please provide a complete, working example that demonstrates how to call this endpoint."""
        
        request = LLMRequest(message=prompt)
        response = self.generate_response(request)
        
        return response.response
    
    def analyze_api_spec(self, api_spec: Dict[str, Any]) -> str:
        """Analyze API specification and provide insights"""
        
        prompt = f"""Analyze the following API specification and provide insights:

API Name: {api_spec.get('name', 'Unknown')}
Type: {api_spec.get('api_type', 'Unknown')}
Version: {api_spec.get('version', 'Unknown')}
Description: {api_spec.get('description', 'No description')}

Please provide:
1. Overall assessment of the API design
2. Potential improvements or issues
3. Best practices recommendations
4. Security considerations (if any)"""
        
        request = LLMRequest(message=prompt)
        response = self.generate_response(request)
        
        return response.response
