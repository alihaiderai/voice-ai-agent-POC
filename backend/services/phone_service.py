"""
Twilio phone service for inbound/outbound calls
"""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Say
from typing import Optional
import logging
from config.settings import get_settings

logger = logging.getLogger(__name__)


class PhoneService:
    """Handle phone calls via Twilio"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = Client(
            self.settings.twilio_account_sid,
            self.settings.twilio_auth_token
        )
        self.phone_number = self.settings.twilio_phone_number
    
    def create_inbound_response(self, user_input: Optional[str] = None) -> str:
        """
        Create TwiML response for inbound calls
        
        Args:
            user_input: User's speech input (if any)
            
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        if not user_input:
            # Initial greeting
            response.say(
                "Hello! Welcome to our AI voice agent. How can I help you today?",
                voice='Polly.Joanna'
            )
        else:
            # Echo back for now (we'll connect to AI later)
            response.say(
                f"You said: {user_input}. Let me help you with that.",
                voice='Polly.Joanna'
            )
        
        # Gather user input
        gather = Gather(
            input='speech',
            action='/api/phone/voice',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        
        response.append(gather)
        
        # If no input, say goodbye
        response.say("Thank you for calling. Goodbye!", voice='Polly.Joanna')
        
        return str(response)
    
    def make_outbound_call(
        self,
        to_number: str,
        message: str
    ) -> dict:
        """
        Make an outbound call
        
        Args:
            to_number: Phone number to call (E.164 format)
            message: Message to speak
            
        Returns:
            Call details
        """
        try:
            # Create TwiML for outbound call
            response = VoiceResponse()
            response.say(message, voice='Polly.Joanna')
            
            # Make the call
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                twiml=str(response)
            )
            
            logger.info(f"Outbound call initiated to {to_number}: {call.sid}")
            
            return {
                "success": True,
                "call_sid": call.sid,
                "to": to_number,
                "status": call.status
            }
            
        except Exception as e:
            logger.error(f"Outbound call error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_call_status(self, call_sid: str) -> dict:
        """Get status of a call"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "from": call.from_,
                "to": call.to
            }
        except Exception as e:
            logger.error(f"Error fetching call status: {e}")
            return {"error": str(e)}
