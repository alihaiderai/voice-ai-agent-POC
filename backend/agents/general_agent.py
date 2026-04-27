"""
General conversational agent
"""
from typing import List, Dict, Any
import logging
from agents.base_agent import BaseAgent
from models.conversation import Message, AgentResponse, AgentType
from config.prompts import GENERAL_AGENT_PROMPT, PROACTIVE_PROMPT

logger = logging.getLogger(__name__)


class GeneralAgent(BaseAgent):
    """General purpose conversational agent"""
    
    def __init__(self, llm_service, rag_service=None, emotion_service=None):
        super().__init__(
            agent_type=AgentType.GENERAL,
            llm_service=llm_service,
            rag_service=rag_service,
            emotion_service=emotion_service
        )
    
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get general agent system prompt"""
        knowledge_context = context.get("rag_context", "")
        conversation_history = context.get("conversation_history", "")
        emotion = context.get("emotion", "neutral")
        
        prompt = GENERAL_AGENT_PROMPT.format(
            knowledge_context=knowledge_context,
            conversation_history=conversation_history,
            emotion=emotion
        )
        
        # Add proactive behavior guidance
        prompt = f"{prompt}\n\n{PROACTIVE_PROMPT}"
        
        return prompt
    
    async def process(
        self,
        user_message: str,
        conversation_history: List[Message],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Process general conversation"""
        try:
            logger.info(f"General agent processing: '{user_message[:50]}...'")
            
            # Detect emotion
            emotion, emotion_confidence = await self._detect_emotion(user_message)
            
            # Get RAG context if query seems informational
            rag_context = ""
            rag_sources = []
            if self._is_informational_query(user_message):
                rag_context = await self._get_rag_context(user_message)
                if rag_context:
                    rag_sources = [{"content": rag_context, "source": "knowledge_base"}]
            
            # Prepare context
            agent_context = {
                "rag_context": rag_context,
                "conversation_history": self._format_conversation_history(conversation_history),
                "emotion": emotion.value
            }
            
            # Get system prompt
            system_prompt = self.get_system_prompt(agent_context)
            
            # Generate response
            response_content = await self.llm_service.generate_response(
                messages=conversation_history + [
                    Message(role="user", content=user_message)
                ],
                system_prompt=system_prompt,
                temperature=0.8  # More creative for general conversation
            )
            
            logger.info(f"General agent response: '{response_content[:50]}...'")
            
            return self._create_response(
                content=response_content,
                emotion=emotion,
                rag_sources=rag_sources,
                confidence=0.85,
                metadata={
                    "emotion_confidence": emotion_confidence,
                    "used_rag": bool(rag_context)
                }
            )
            
        except Exception as e:
            logger.error(f"General agent error: {e}")
            return self._create_response(
                content="I apologize, I'm having a moment. Could you rephrase that?",
                confidence=0.3,
                metadata={"error": str(e)}
            )
    
    def _is_informational_query(self, message: str) -> bool:
        """Check if message is asking for information"""
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'tell me', 'explain']
        message_lower = message.lower()
        return any(word in message_lower for word in question_words)
