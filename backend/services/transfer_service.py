"""
Call transfer service - Transfer calls to human agents
"""
from twilio.rest import Client
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class TransferService:
    """Handle call transfers to human agents"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Client(
            self.settings.twilio_account_sid,
            self.settings.twilio_auth_token
        )
        
        # Human agent phone numbers
        self.agent_numbers = {
            "support": "+1234567890",  # Replace with actual agent number
            "manager": "+1234567891",  # Replace with manager number
            "sales": "+1234567892"     # Replace with sales number
        }
    
    def should_transfer(self, conversation_history: list, emotion: str) -> bool:
        """
        Decide if call should be transferred to human
        
        Triggers:
        - Customer explicitly asks for human
        - Customer is frustrated/angry
        - AI failed to help after 3 attempts
        - Complex query detected
        """
        
        # Check for explicit transfer requests
        transfer_keywords = [
            "speak to human", "talk to person", "real person",
            "manager", "supervisor", "human agent"
        ]
        
        last_message = conversation_history[-1]["content"].lower() if conversation_history else ""
        
        for keyword in transfer_keywords:
            if keyword in last_message:
                logger.info(f"Transfer triggered by keyword: {keyword}")
                return True
        
        # Check emotion
        if emotion in ["angry", "frustrated"]:
            logger.info(f"Transfer triggered by emotion: {emotion}")
            return True
        
        # Check if AI is stuck (same response multiple times)
        if len(conversation_history) >= 6:
            recent_ai_responses = [
                msg["content"] for msg in conversation_history[-6:]
                if msg["role"] == "assistant"
            ]
            if len(set(recent_ai_responses)) <= 2:
                logger.info("Transfer triggered: AI seems stuck")
                return True
        
        return False
    
    def transfer_call(self, call_sid: str, agent_type: str = "support") -> dict:
        """
        Transfer active call to human agent
        
        Args:
            call_sid: Twilio call SID
            agent_type: Type of agent (support, manager, sales)
        """
        try:
            agent_number = self.agent_numbers.get(agent_type, self.agent_numbers["support"])
            
            # Update call to transfer
            call = self.client.calls(call_sid).update(
                twiml=f'''
                <Response>
                    <Say>Please hold while I transfer you to a human agent.</Say>
                    <Dial>{agent_number}</Dial>
                </Response>
                '''
            )
            
            logger.info(f"Call {call_sid} transferred to {agent_type} agent")
            
            return {
                "success": True,
                "call_sid": call_sid,
                "transferred_to": agent_type,
                "agent_number": agent_number
            }
            
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
