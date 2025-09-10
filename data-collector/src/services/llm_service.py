import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

class LLMQueryService:
    """Service for handling LLM-powered queries on API specifications"""
    
    def __init__(self):
        """Initialize the LLM query service"""
        self.load_environment()
        self.initialize_openai()
        self.initialize_chromadb()
        
    def load_environment(self):
        """Load environment variables"""
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
    def initialize_openai(self):
        """Initialize OpenAI client"""
        try:
            # Initialize OpenAI client with proper configuration
            self.client = openai.OpenAI(
                api_key=self.openai_api_key,
                timeout=30.0
            )
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
            self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
            self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing OpenAI: {str(e)}")
            # Don't raise the error, just set client to None
            self.client = None
            self.model = 'gpt-4'
            self.max_tokens = 4000
            self.temperature = 0.7
            
    def initialize_chromadb(self):
        """Initialize ChromaDB client"""
        try:
            persist_directory = os.getenv('CHROMADB_PERSIST_DIRECTORY', './chroma_db')
            self.chroma_client = chromadb.PersistentClient(path=persist_directory)
            self.collection_name = os.getenv('CHROMADB_COLLECTION', 'api_specifications')
            print("✅ ChromaDB client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {str(e)}")
            raise
            
    def get_collection(self):
        """Get the ChromaDB collection"""
        try:
            return self.chroma_client.get_collection(name=self.collection_name)
        except Exception as e:
            print(f"❌ Error getting collection: {str(e)}")
            return None
            
    def search_api_specs(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant API specifications using ChromaDB"""
        try:
            collection = self.get_collection()
            if not collection:
                return []
                
            # Perform similarity search
            results = collection.query(
                query_texts=[query],
                n_results=max_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })
                    
            return formatted_results
            
        except Exception as e:
            print(f"❌ Error searching API specs: {str(e)}")
            return []
            
    def generate_answer(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate an answer using OpenAI based on the question and context"""
        try:
            if not self.client:
                return "OpenAI client is not available. Please check your API key configuration."
                
            # Prepare context from documents
            context_text = ""
            for doc in context_docs:
                context_text += f"API Specification:\n{doc['document']}\n\n"
                
            # Create system prompt
            system_prompt = """You are an expert API integration consultant with access to a comprehensive knowledge base of API documentation. Your job is to help users understand and work with API specifications from various sources.

Given a user's question and relevant API specification documents from the knowledge base, provide a comprehensive, helpful answer that:
1. Directly addresses the user's question
2. References specific API endpoints, parameters, or features from the specifications
3. Provides practical guidance and examples where appropriate
4. Explains any technical concepts clearly
5. Suggests best practices or common use cases
6. Mentions which API(s) or service(s) the information comes from

Be concise but thorough, and always base your answer on the provided API specification data from the knowledge base."""

            # Create user prompt
            user_prompt = f"""Question: {question}

Relevant API Specifications:
{context_text}

Please provide a comprehensive answer to the user's question based on the API specifications above."""

            # Get OpenAI response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating answer: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
            
    def calculate_confidence_score(self, distances: List[float]) -> float:
        """Calculate confidence score based on search distances"""
        if not distances:
            return 0.0
            
        # Convert distances to confidence scores (lower distance = higher confidence)
        # ChromaDB uses cosine distance, so 0 = perfect match, 2 = no match
        avg_distance = sum(distances) / len(distances)
        confidence = max(0.0, min(1.0, 1.0 - (avg_distance / 2.0)))
        return round(confidence, 2)
        
    def ask_question(self, question: str, application_id: Optional[int] = None, 
                    api_spec_id: Optional[int] = None, max_results: int = 5) -> Dict[str, Any]:
        """Main method to ask a question and get a comprehensive answer"""
        start_time = time.time()
        
        try:
            # Search for relevant API specifications
            search_results = self.search_api_specs(question, max_results)
            
            if not search_results:
                return {
                    'question': question,
                    'answer': "I couldn't find any relevant API documentation to answer your question. Please make sure API specifications have been uploaded and processed into the knowledge base.",
                    'relevant_api_specs': [],
                    'sources': [],
                    'confidence_score': 0.0,
                    'processing_time': time.time() - start_time,
                    'timestamp': datetime.now()
                }
            
            # Extract documents and distances for processing
            context_docs = search_results
            distances = [doc['distance'] for doc in context_docs]
            
            # Generate answer using LLM
            answer = self.generate_answer(question, context_docs)
            
            # Calculate confidence score
            confidence_score = self.calculate_confidence_score(distances)
            
            # Prepare sources
            sources = []
            for doc in context_docs:
                sources.append({
                    'content': doc['document'][:200] + "..." if len(doc['document']) > 200 else doc['document'],
                    'metadata': doc['metadata'],
                    'relevance_score': 1.0 - doc['distance']
                })
            
            return {
                'question': question,
                'answer': answer,
                'relevant_api_specs': [],  # Will be populated by the API endpoint
                'sources': sources,
                'confidence_score': confidence_score,
                'processing_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Error in ask_question: {str(e)}")
            return {
                'question': question,
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'relevant_api_specs': [],
                'sources': [],
                'confidence_score': 0.0,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now()
            }
