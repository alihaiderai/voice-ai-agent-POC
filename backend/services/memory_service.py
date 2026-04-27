"""
Conversation memory and context management
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from models.conversation import ConversationContext, Message, MessageRole

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Manages conversation memory with short-term and long-term storage
    """
    
    def __init__(self):
        # In-memory storage for POC
        # In production, use Redis or database
        self.sessions: Dict[str, ConversationContext] = {}
        self.session_timeout = timedelta(hours=1)
    
    async def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> ConversationContext:
        """Get existing session or create new one"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                # Check if session expired
                if datetime.now() - session.updated_at > self.session_timeout:
                    logger.info(f"Session {session_id} expired, creating new")
                    session = self._create_new_session(session_id, user_id)
                else:
                    logger.info(f"Retrieved existing session {session_id}")
            else:
                logger.info(f"Creating new session {session_id}")
                session = self._create_new_session(session_id, user_id)
            
            self.sessions[session_id] = session
            return session
            
        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            raise
    
    def _create_new_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> ConversationContext:
        """Create a new conversation session"""
        return ConversationContext(
            session_id=session_id,
            user_id=user_id
        )
    
    async def add_message(
        self,
        session_id: str,
        message: Message
    ):
        """Add message to session"""
        try:
            session = await self.get_or_create_session(session_id)
            session.add_message(message)
            logger.info(f"Added message to session {session_id}")
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get conversation history"""
        try:
            session = await self.get_or_create_session(session_id)
            if limit:
                return session.get_recent_messages(limit)
            return session.messages
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return []
    
    async def update_context(
        self,
        session_id: str,
        entities: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Update session context"""
        try:
            session = await self.get_or_create_session(session_id)
            
            if entities:
                session.entities.update(entities)
            
            if preferences:
                session.user_preferences.update(preferences)
            
            if metadata:
                session.metadata.update(metadata)
            
            session.updated_at = datetime.now()
            logger.info(f"Updated context for session {session_id}")
            
        except Exception as e:
            logger.error(f"Context update error: {e}")
            raise
    
    async def extract_entities(
        self,
        session_id: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Extract entities from text
        
        Simple rule-based extraction for POC.
        In production, use NER models.
        """
        entities = {}
        
        # Simple patterns
        import re
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            entities['email'] = emails[0]
        
        # Phone
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            entities['phone'] = phones[0]
        
        # Date/time keywords
        time_keywords = ['today', 'tomorrow', 'monday', 'tuesday', 'wednesday', 
                        'thursday', 'friday', 'saturday', 'sunday', 'next week']
        for keyword in time_keywords:
            if keyword in text.lower():
                entities['time_reference'] = keyword
                break
        
        # Update session if entities found
        if entities:
            await self.update_context(session_id, entities=entities)
        
        return entities
    
    async def get_context_summary(
        self,
        session_id: str
    ) -> str:
        """Get formatted context summary for prompts"""
        try:
            session = await self.get_or_create_session(session_id)
            
            summary_parts = []
            
            # Recent conversation
            recent = session.get_recent_messages(5)
            if recent:
                conv_summary = "\n".join([
                    f"{msg.role.value if hasattr(msg.role, 'value') else str(msg.role)}: {msg.content[:100]}"
                    for msg in recent
                ])
                summary_parts.append(f"Recent conversation:\n{conv_summary}")
            
            # Entities
            if session.entities:
                entities_str = ", ".join([
                    f"{k}: {v}" for k, v in session.entities.items()
                ])
                summary_parts.append(f"Extracted entities: {entities_str}")
            
            # Preferences
            if session.user_preferences:
                prefs_str = ", ".join([
                    f"{k}: {v}" for k, v in session.user_preferences.items()
                ])
                summary_parts.append(f"User preferences: {prefs_str}")
            
            # Unresolved topics
            if session.unresolved_topics:
                topics_str = ", ".join(session.unresolved_topics)
                summary_parts.append(f"Unresolved topics: {topics_str}")
            
            return "\n\n".join(summary_parts) if summary_parts else "No context available."
            
        except Exception as e:
            logger.error(f"Context summary error: {e}")
            return "Error retrieving context."
    
    async def clear_session(self, session_id: str):
        """Clear a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
    
    async def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [
            sid for sid, session in self.sessions.items()
            if now - session.updated_at > self.session_timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
