"""
Chat service for managing chat sessions and messages
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.database.models import ChatSession, ChatMessage, APISpec
from models.schemas.schemas import ChatSessionCreate, ChatSessionUpdate, ChatMessageCreate
from services.llm.llm_service import LLMService
from services.vector_db.vector_db_factory import VectorDatabaseManager
from utils.logging import LoggerMixin


class ChatService(LoggerMixin):
    """Service for chat management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        # Initialize vector database manager
        vector_db_config = {
            'type': 'chromadb',
            'chunking_strategy': 'endpoint_based',
            'max_chunk_size': 1000,
            'chunk_overlap': 200,
            'embedding_model': 'text-embedding-ada-002',
            'persist_directory': './vector_db',
            'collection_name': 'api_specifications'
        }
        self.vector_service = VectorDatabaseManager(vector_db_config)
    
    def create_chat_session(self, user_id: int, session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session"""
        
        try:
            db_session = ChatSession(
                title=session_data.title,
                context=session_data.context or {},
                user_id=user_id,
                api_spec_id=session_data.api_spec_id
            )
            
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            
            self.logger.info(f"✅ Created chat session: {db_session.id}")
            return db_session
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error creating chat session: {str(e)}")
            raise
    
    def get_chat_session(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Get chat session by ID"""
        return self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
    
    def get_user_chat_sessions(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.is_active == True
        ).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
    
    def update_chat_session(self, session_id: int, user_id: int, session_data: ChatSessionUpdate) -> Optional[ChatSession]:
        """Update chat session"""
        
        try:
            db_session = self.get_chat_session(session_id, user_id)
            if not db_session:
                return None
            
            update_data = session_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_session, field, value)
            
            self.db.commit()
            self.db.refresh(db_session)
            
            self.logger.info(f"✅ Updated chat session: {db_session.id}")
            return db_session
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error updating chat session: {str(e)}")
            raise
    
    def delete_chat_session(self, session_id: int, user_id: int) -> bool:
        """Delete chat session (soft delete)"""
        
        try:
            db_session = self.get_chat_session(session_id, user_id)
            if not db_session:
                return False
            
            db_session.is_active = False
            self.db.commit()
            
            self.logger.info(f"✅ Deleted chat session: {db_session.id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error deleting chat session: {str(e)}")
            raise
    
    def add_message(self, session_id: int, message_data: ChatMessageCreate) -> ChatMessage:
        """Add message to chat session"""
        
        try:
            db_message = ChatMessage(
                content=message_data.content,
                role=message_data.role,
                message_type=message_data.message_type,
                metadata=message_data.metadata or {},
                session_id=session_id
            )
            
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
            
            self.logger.info(f"✅ Added message to session {session_id}")
            return db_message
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"❌ Error adding message: {str(e)}")
            raise
    
    def get_session_messages(self, session_id: int, user_id: int, limit: int = 50) -> List[ChatMessage]:
        """Get messages for a chat session"""
        
        # Verify session belongs to user
        session = self.get_chat_session(session_id, user_id)
        if not session:
            return []
        
        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).limit(limit).all()
    
    def generate_response(
        self, 
        session_id: int, 
        user_id: int, 
        user_message: str,
        include_chain_of_thought: bool = True
    ) -> ChatMessage:
        """Generate AI response for user message"""
        
        try:
            # Get chat session
            session = self.get_chat_session(session_id, user_id)
            if not session:
                raise ValueError("Chat session not found")
            
            # Add user message to session
            user_msg = self.add_message(session_id, ChatMessageCreate(
                content=user_message,
                role="user"
            ))
            
            # Get relevant API specifications for context
            api_specs = self._get_relevant_api_specs(session, user_message)
            
            # Search vector database for relevant content
            search_results = self.vector_service.vector_service.search_api_specifications(
                query=user_message,
                api_spec_ids=[spec['id'] for spec in api_specs] if api_specs else None,
                limit=5
            )
            
            # Build context from search results
            context = self._build_context_from_search(search_results)
            
            # Generate LLM response
            from models.schemas.schemas import LLMRequest
            llm_request = LLMRequest(
                message=user_message,
                context=context,
                include_chain_of_thought=include_chain_of_thought
            )
            
            llm_response = self.llm_service.generate_response(llm_request, api_specs)
            
            # Add assistant response to session
            assistant_msg = self.add_message(session_id, ChatMessageCreate(
                content=llm_response.response,
                role="assistant",
                message_type="markdown",
                metadata={
                    "tokens_used": llm_response.tokens_used,
                    "model_used": llm_response.model_used,
                    "search_results_count": len(search_results)
                }
            ))
            
            # Update message with chain of thought if available
            if llm_response.chain_of_thought:
                assistant_msg.chain_of_thought = llm_response.chain_of_thought
                assistant_msg.tokens_used = llm_response.tokens_used
                self.db.commit()
            
            self.logger.info(f"✅ Generated response for session {session_id}")
            return assistant_msg
            
        except Exception as e:
            self.logger.error(f"❌ Error generating response: {str(e)}")
            raise
    
    def _get_relevant_api_specs(self, session: ChatSession, message: str) -> List[Dict[str, Any]]:
        """Get relevant API specifications for the chat session"""
        
        api_specs = []
        
        # If session has specific API spec, use it
        if session.api_spec_id:
            api_spec = self.db.query(APISpec).filter(
                APISpec.id == session.api_spec_id,
                APISpec.is_active == True
            ).first()
            
            if api_spec:
                api_specs.append({
                    'id': api_spec.id,
                    'name': api_spec.name,
                    'api_type': api_spec.api_type,
                    'description': api_spec.description,
                    'seal_id': api_spec.seal_id,
                    'application': api_spec.application
                })
        
        # If no specific API spec or need more context, get user's API specs
        if not api_specs:
            user_api_specs = self.db.query(APISpec).filter(
                APISpec.owner_id == session.user_id,
                APISpec.is_active == True
            ).all()
            
            for spec in user_api_specs:
                api_specs.append({
                    'id': spec.id,
                    'name': spec.name,
                    'api_type': spec.api_type,
                    'description': spec.description,
                    'seal_id': spec.seal_id,
                    'application': spec.application
                })
        
        return api_specs
    
    def _build_context_from_search(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build context from vector search results"""
        
        context = {
            'relevant_content': [],
            'api_specs_referenced': set(),
            'total_results': len(search_results)
        }
        
        for result in search_results:
            context['relevant_content'].append({
                'content': result['content'],
                'metadata': result['metadata'],
                'score': result['score']
            })
            
            if result['api_spec_id']:
                context['api_specs_referenced'].add(result['api_spec_id'])
        
        context['api_specs_referenced'] = list(context['api_specs_referenced'])
        
        return context
    
    def get_chat_history(self, session_id: int, user_id: int) -> Dict[str, Any]:
        """Get complete chat history for a session"""
        
        session = self.get_chat_session(session_id, user_id)
        if not session:
            return {}
        
        messages = self.get_session_messages(session_id, user_id)
        
        return {
            'session': {
                'id': session.id,
                'title': session.title,
                'created_at': session.created_at,
                'updated_at': session.updated_at,
                'api_spec_id': session.api_spec_id
            },
            'messages': [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'role': msg.role,
                    'message_type': msg.message_type,
                    'chain_of_thought': msg.chain_of_thought,
                    'tokens_used': msg.tokens_used,
                    'created_at': msg.created_at,
                    'metadata': msg.metadata
                }
                for msg in messages
            ]
        }
