"""
Booking agent - handles appointment scheduling
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
from agents.base_agent import BaseAgent
from models.conversation import Message, AgentResponse, AgentType
from config.prompts import BOOKING_AGENT_PROMPT

logger = logging.getLogger(__name__)


class BookingAgent(BaseAgent):
    """Appointment booking specialist agent"""
    
    def __init__(self, llm_service, rag_service=None, emotion_service=None):
        super().__init__(
            agent_type=AgentType.BOOKING,
            llm_service=llm_service,
            rag_service=rag_service,
            emotion_service=emotion_service
        )
    
    def _register_tools(self) -> List[Dict[str, Any]]:
        """Register booking-specific tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_availability",
                    "description": "Check available time slots for appointments",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format"
                            },
                            "service_type": {
                                "type": "string",
                                "description": "Type of service/appointment"
                            }
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_appointment",
                    "description": "Book an appointment slot",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string"},
                            "time": {"type": "string"},
                            "service_type": {"type": "string"},
                            "customer_name": {"type": "string"},
                            "customer_email": {"type": "string"},
                            "notes": {"type": "string"}
                        },
                        "required": ["date", "time", "customer_name"]
                    }
                }
            }
        ]
    
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get booking agent system prompt"""
        tools_str = self._format_tools()
        conversation_history = context.get("conversation_history", "")
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")
        timezone = "UTC"  # In production, get from user
        
        return BOOKING_AGENT_PROMPT.format(
            tools=tools_str,
            current_datetime=current_datetime,
            timezone=timezone,
            conversation_history=conversation_history
        )
    
    async def process(
        self,
        user_message: str,
        conversation_history: List[Message],
        context: Dict[str, Any]
    ) -> AgentResponse:
        """Process booking request"""
        try:
            logger.info(f"Booking agent processing: '{user_message[:50]}...'")
            
            # Detect emotion
            emotion, emotion_confidence = await self._detect_emotion(user_message)
            
            # Prepare context
            agent_context = {
                "conversation_history": self._format_conversation_history(conversation_history)
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
            
            logger.info(f"Booking agent response: '{response_content[:50]}...'")
            
            return self._create_response(
                content=response_content,
                emotion=emotion,
                confidence=0.9,
                metadata={
                    "emotion_confidence": emotion_confidence
                }
            )
            
        except Exception as e:
            logger.error(f"Booking agent error: {e}")
            return self._create_response(
                content="I apologize, I'm having trouble with the booking system. Would you like me to have someone call you back to schedule?",
                confidence=0.3,
                metadata={"error": str(e)}
            )
    
    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute booking tools"""
        if tool_name == "check_availability":
            return await self._check_availability(parameters)
        elif tool_name == "book_appointment":
            return await self._book_appointment(parameters)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def _check_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock availability check"""
        # In production, query actual calendar system
        date_str = params.get("date")
        
        # Generate mock available slots
        slots = [
            "09:00 AM", "10:00 AM", "11:00 AM",
            "02:00 PM", "03:00 PM", "04:00 PM"
        ]
        
        return {
            "date": date_str,
            "available_slots": slots,
            "timezone": "UTC"
        }
    
    async def _book_appointment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock appointment booking"""
        # In production, create actual booking
        import uuid
        booking_id = str(uuid.uuid4())[:8]
        
        return {
            "success": True,
            "booking_id": booking_id,
            "date": params.get("date"),
            "time": params.get("time"),
            "customer_name": params.get("customer_name"),
            "confirmation_sent": True
        }
