"""
Orchestrator agent - routes conversations to specialized agents
"""
from typing import List, Dict, Any
import logging
from agents.base_agent import BaseAgent
from models.conversation import Message, AgentResponse, AgentType
from config.prompts import ORCHESTRATOR_PROMPT

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator that analyzes intent and routes to specialized agents
    """
    
    def __init__(self, llm_service, rag_service=None, emotion_service=None):
        super().__init__(
            agent_type=AgentType.ORCHESTRATOR,
            llm_service=llm_service,
            rag_service=rag_service,
            emotion_service=emotion_service
        )
        self.available_agents = {
            "support": AgentType.SUPPORT,
            "booking": AgentType.BOOKING,
            "general": AgentType.GENERAL,
            "analytics": AgentType.ANALYTICS
        }
    
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get orchestrator system prompt"""
        available_agents_str = ", ".join(self.available_agents.keys())
        context_str = context.get("summary", "No prior context")
        
        return ORCHESTRATOR_PROMPT.format(
            context=context_str,
            available_agents=available_agents_str
        )
    
    async def process(
        self,
        user_message: str,
        conversation_history: List[Message],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Analyze intent and route to appropriate agent
        
        Returns:
            AgentResponse with routing decision
        """
        try:
            logger.info(f"Orchestrator analyzing: '{user_message[:50]}...'")
            
            # Detect emotion
            emotion, emotion_confidence = await self._detect_emotion(user_message)
            
            # Analyze intent using LLM
            intent_result = await self.llm_service.analyze_intent(
                user_message,
                context.get("summary")
            )
            
            selected_agent = intent_result.get("agent", "general")
            reasoning = intent_result.get("reasoning", "Default routing")
            confidence = intent_result.get("confidence", 0.7)
            
            logger.info(f"Routing to {selected_agent} agent (confidence: {confidence:.2f})")
            
            # Create routing response
            response_content = f"[ROUTE:{selected_agent}] {reasoning}"
            
            return self._create_response(
                content=response_content,
                emotion=emotion,
                confidence=confidence,
                metadata={
                    "selected_agent": selected_agent,
                    "intent": intent_result.get("intent"),
                    "reasoning": reasoning,
                    "emotion_confidence": emotion_confidence
                }
            )
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            # Default to general agent on error
            return self._create_response(
                content="[ROUTE:general] Error in routing, using general agent",
                confidence=0.5,
                metadata={"selected_agent": "general", "error": str(e)}
            )
    
    def get_agent_type_from_name(self, agent_name: str) -> AgentType:
        """Convert agent name to AgentType enum"""
        return self.available_agents.get(agent_name, AgentType.GENERAL)
