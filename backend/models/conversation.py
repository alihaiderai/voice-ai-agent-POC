"""
Data models for conversation management
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class EmotionType(str, Enum):
    """Detected emotion types"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    EXCITED = "excited"


class AgentType(str, Enum):
    """Available agent types"""
    ORCHESTRATOR = "orchestrator"
    SUPPORT = "support"
    BOOKING = "booking"
    GENERAL = "general"
    ANALYTICS = "analytics"


class Message(BaseModel):
    """Single conversation message"""
    id: str = Field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_type: Optional[AgentType] = None
    emotion: Optional[EmotionType] = None
    emotion_confidence: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class ToolCall(BaseModel):
    """Tool/function call representation"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationContext(BaseModel):
    """Conversation context and state"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    current_agent: AgentType = AgentType.ORCHESTRATOR
    entities: Dict[str, Any] = Field(default_factory=dict)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    unresolved_topics: List[str] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, message: Message):
        """Add message to conversation"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages"""
        return self.messages[-limit:]
    
    def get_conversation_summary(self) -> str:
        """Generate conversation summary"""
        if not self.messages:
            return "No conversation yet."
        
        summary_parts = []
        for msg in self.messages[-5:]:  # Last 5 messages
            # Handle both enum and string values
            role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
            content = msg.content[:100]  # Truncate
            summary_parts.append(f"{role}: {content}")
        
        return "\n".join(summary_parts)
    
    class Config:
        use_enum_values = True


class AudioChunk(BaseModel):
    """Audio data chunk"""
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    timestamp: datetime = Field(default_factory=datetime.now)


class TranscriptionResult(BaseModel):
    """Speech-to-text result"""
    text: str
    confidence: float
    language: str = "en"
    duration: float
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentResponse(BaseModel):
    """Agent response with metadata"""
    content: str
    agent_type: AgentType
    emotion: Optional[EmotionType] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    rag_sources: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ConversationMetrics(BaseModel):
    """Analytics and metrics for a conversation"""
    session_id: str
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    average_response_time: float = 0.0
    sentiment_scores: List[float] = Field(default_factory=list)
    emotions_detected: Dict[str, int] = Field(default_factory=dict)
    agents_used: Dict[str, int] = Field(default_factory=dict)
    tools_called: Dict[str, int] = Field(default_factory=dict)
    duration_seconds: float = 0.0
    resolution_status: Optional[str] = None
    user_satisfaction: Optional[int] = None  # 1-5 scale
    
    def update_from_message(self, message: Message):
        """Update metrics from a message"""
        self.total_messages += 1
        if message.role == MessageRole.USER:
            self.user_messages += 1
        elif message.role == MessageRole.ASSISTANT:
            self.assistant_messages += 1
        
        if message.emotion:
            emotion_str = message.emotion.value
            self.emotions_detected[emotion_str] = self.emotions_detected.get(emotion_str, 0) + 1
        
        if message.agent_type:
            agent_str = message.agent_type.value
            self.agents_used[agent_str] = self.agents_used.get(agent_str, 0) + 1


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # audio, text, control, status, error
    data: Any
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
