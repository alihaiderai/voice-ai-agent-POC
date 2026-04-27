"""
Support agent - handles customer support inquiries
"""
from typing import List, Dict, Any
import logging
from agents.base_agent import BaseAgent
from models.conversation import Message, AgentResponse, AgentType
from config.prompts import SUPPORT_AGENT_PROMPT, EMOTION_AWARE_PROMPT

logger = logging.getLogger(__name__)


class SupportAgent(BaseAgent):
    """Customer support specialist agent"""
    
    def __init__(self, llm_service, rag_service=None, emotion_service=None):
        super().__init__(
            agent_type=AgentType.SUPPORT,
            llm_service=llm_service,
            rag_service=rag_service,
            emotion_service=emotion_service
        )
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register support-specific tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the knowledge base for solutions to customer issues",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for the knowledge base"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_support_ticket",
                    "description": "Create a support ticket for complex issues",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"]
                            }
                        },
                        "required": ["title", "description"]
                    }
                }
            }
        ]
    
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get support agent system prompt"""
        tools_str = self._format_tools()
        knowledge_context = context.get("rag_context", "No knowledge base context available")
        conversation_history = context.get("conversation_history", "No prior conversation")
        emotion = context.get("emotion", "neutral")
        
        # Base prompt
        prompt = SUPPORT_AGENT_PROMPT.format(
            tools=tools_str,
            knowledge_context=knowledge_context,
            conversation_history=conversation_history,
            emotion=emotion
        )
        
        # Add emotion-aware guidance
        if emotion != "neutral":
            emotion_guidance = EMOTION_AWARE_PROMPT.format(
                emotion=emotion,
                confidence=context.get("emotion_confidence", 0.5)
            )
            prompt = f"{prompt}\n\n{emotion_guidance}"
        
        return prompt
    
    async def process(
        self,
        user_message: str,
        conversation_history: List[Message],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Process support inquiry"""
        try:
            logger.info(f"Support agent processing: '{user_message[:50]}...'")
            
            # Detect emotion
            emotion, emotion_confidence = await self._detect_emotion(user_message)
            
            # Get RAG context
            rag_context = await self._get_rag_context(user_message)
            rag_sources = []
            if rag_context:
                rag_sources = [{"content": rag_context, "source": "knowledge_base"}]
            
            # Prepare context
            agent_context = {
                "rag_context": rag_context,
                "conversation_history": self._format_conversation_history(conversation_history),
                "emotion": emotion.value,
                "emotion_confidence": emotion_confidence
            }
            
            # Get system prompt
            system_prompt = self.get_system_prompt(agent_context)
            
            # Generate response
            response_content = await self.llm_service.generate_response(
                messages=conversation_history + [
                    Message(role="user", content=user_message)
                ],
                system_prompt=system_prompt,
                tools=self.tools if context.get("enable_tools", True) else None
            )
            
            logger.info(f"Support agent response: '{response_content[:50]}...'")
            
            return self._create_response(
                content=response_content,
                emotion=emotion,
                rag_sources=rag_sources,
                confidence=0.9,
                metadata={
                    "emotion_confidence": emotion_confidence,
                    "used_knowledge_base": bool(rag_context)
                }
            )
            
        except Exception as e:
            logger.error(f"Support agent error: {e}")
            return self._create_response(
                content="I apologize, I'm having trouble processing your request. Let me connect you with a human agent who can better assist you.",
                confidence=0.3,
                metadata={"error": str(e)}
            )
