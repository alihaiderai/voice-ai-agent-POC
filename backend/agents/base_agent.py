"""
Base agent class with common functionality
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from models.conversation import Message, AgentResponse, AgentType, EmotionType
from services.llm_service import LLMService
from services.emotion_service import EmotionService

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(
        self,
        agent_type: AgentType,
        llm_service: LLMService,
        rag_service: Optional[Any] = None,
        emotion_service: Optional[EmotionService] = None
    ):
        self.agent_type = agent_type
        self.llm_service = llm_service
        self.rag_service = rag_service
        self.emotion_service = emotion_service
        self.tools = self._register_tools()
    
    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Get system prompt for this agent
        
        Args:
            context: Context dictionary with conversation state
            
        Returns:
            Formatted system prompt
        """
        pass
    
    @abstractmethod
    async def process(
        self,
        user_message: str,
        conversation_history: List[Message],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Process user message and generate response
        
        Args:
            user_message: User's input
            conversation_history: Previous messages
            context: Additional context
            
        Returns:
            AgentResponse with content and metadata
        """
        pass
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """
        Register tools/functions this agent can use
        
        Override in subclasses to add specific tools.
        """
        return []
    
    async def _get_rag_context(
        self,
        query: str,
        max_results: int = 3
    ) -> str:
        """Get RAG context if available"""
        if not self.rag_service:
            return ""
        
        try:
            context = await self.rag_service.get_context_for_query(
                query,
                max_tokens=500
            )
            return context
        except Exception as e:
            logger.error(f"RAG context error: {e}")
            return ""
    
    async def _detect_emotion(
        self,
        text: str
    ) -> tuple[EmotionType, float]:
        """Detect emotion if service available"""
        if not self.emotion_service:
            return EmotionType.NEUTRAL, 1.0
        
        try:
            return await self.emotion_service.analyze_emotion(text)
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return EmotionType.NEUTRAL, 0.5
    
    def _format_conversation_history(
        self,
        messages: List[Message],
        limit: int = 10
    ) -> str:
        """Format conversation history for prompts"""
        recent = messages[-limit:] if len(messages) > limit else messages
        
        formatted = []
        for msg in recent:
            # Handle both enum and string values
            role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
            content = msg.content[:200]  # Truncate long messages
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def _format_tools(self) -> str:
        """Format tool descriptions for prompts"""
        if not self.tools:
            return "No tools available."
        
        tool_descriptions = []
        for tool in self.tools:
            name = tool.get('function', {}).get('name', 'unknown')
            description = tool.get('function', {}).get('description', '')
            tool_descriptions.append(f"- {name}: {description}")
        
        return "\n".join(tool_descriptions)
    
    async def _execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool/function
        
        Override in subclasses to implement tool execution.
        """
        logger.warning(f"Tool execution not implemented: {tool_name}")
        return {"error": "Tool execution not implemented"}
    
    def _create_response(
        self,
        content: str,
        emotion: Optional[EmotionType] = None,
        tool_calls: Optional[List] = None,
        rag_sources: Optional[List] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Create standardized agent response"""
        return AgentResponse(
            content=content,
            agent_type=self.agent_type,
            emotion=emotion,
            tool_calls=tool_calls or [],
            rag_sources=rag_sources or [],
            confidence=confidence,
            metadata=metadata or {}
        )
