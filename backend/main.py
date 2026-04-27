"""
Main FastAPI application for Voice AI Agent Platform
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
from typing import Dict
import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config.settings import get_settings
from services.llm_service import LLMService
from services.stt_service import STTService
from services.tts_service import TTSService
# from services.rag_service import RAGService  # Disabled for Python 3.14
from services.memory_service import MemoryService
from services.emotion_service import EmotionService
from services.phone_service import PhoneService
from services.analytics_service import AnalyticsService
from agents.orchestrator import OrchestratorAgent
from agents.support_agent import SupportAgent
from agents.booking_agent import BookingAgent
from agents.general_agent import GeneralAgent
from models.conversation import Message, MessageRole, AgentType, WebSocketMessage
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global services
services: Dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    logger.info("Initializing Voice AI Platform...")
    
    try:
        settings = get_settings()
        
        # Initialize services
        services['llm'] = LLMService()
        services['stt'] = STTService()
        services['tts'] = TTSService()
        services['rag'] = None  # Disabled for Python 3.14 compatibility
        services['memory'] = MemoryService()
        services['emotion'] = EmotionService()
        services['phone'] = PhoneService()
        services['analytics'] = AnalyticsService()
        
        # Note: RAG disabled for Python 3.14 compatibility
        logger.info("RAG service disabled (ChromaDB not compatible with Python 3.14)")
        
        # Initialize agents (without RAG)
        services['agents'] = {
            AgentType.ORCHESTRATOR: OrchestratorAgent(
                services['llm'],
                None,  # No RAG
                services['emotion']
            ),
            AgentType.SUPPORT: SupportAgent(
                services['llm'],
                None,  # No RAG
                services['emotion']
            ),
            AgentType.BOOKING: BookingAgent(
                services['llm'],
                None,  # No RAG
                services['emotion']
            ),
            AgentType.GENERAL: GeneralAgent(
                services['llm'],
                None,  # No RAG
                services['emotion']
            )
        }
        
        logger.info("All services initialized successfully")
        
        yield
        
        # Cleanup
        logger.info("Shutting down...")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "app": settings.app_name,
        "version": settings.app_version
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "llm": "ready",
            "stt": "ready",
            "tts": "ready",
            "rag": "ready",
            "memory": "ready"
        }
    }


@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice conversation
    
    Protocol:
    - Client sends: {"type": "audio", "data": base64_audio}
    - Server sends: {"type": "transcript", "data": text}
    - Server sends: {"type": "response", "data": text}
    - Server sends: {"type": "audio", "data": base64_audio}
    """
    await websocket.accept()
    session_id = f"session_{id(websocket)}"
    
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        # Get services
        stt_service = services['stt']
        tts_service = services['tts']
        memory_service = services['memory']
        orchestrator = services['agents'][AgentType.ORCHESTRATOR]
        
        # Create session
        await memory_service.get_or_create_session(session_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "status",
            "data": "Connected to Voice AI Platform",
            "session_id": session_id
        })
        
        while True:
            # Receive message from client
            message = await websocket.receive_json()
            message_type = message.get("type")
            
            if message_type == "audio":
                # Process audio input
                await handle_audio_input(
                    websocket,
                    session_id,
                    message.get("data"),
                    stt_service,
                    tts_service,
                    memory_service,
                    orchestrator
                )
            
            elif message_type == "text":
                # Process text input
                await handle_text_input(
                    websocket,
                    session_id,
                    message.get("data"),
                    tts_service,
                    memory_service,
                    orchestrator
                )
            
            elif message_type == "control":
                # Handle control messages
                control_action = message.get("action")
                if control_action == "end_session":
                    await memory_service.clear_session(session_id)
                    break
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": "An error occurred. Please try again."
        })
    finally:
        await memory_service.clear_session(session_id)


async def handle_audio_input(
    websocket: WebSocket,
    session_id: str,
    audio_data: str,
    stt_service: STTService,
    tts_service: TTSService,
    memory_service: MemoryService,
    orchestrator: OrchestratorAgent
):
    """Handle audio input from client"""
    try:
        # Decode base64 audio
        import base64
        audio_bytes = base64.b64decode(audio_data)
        
        # Transcribe
        await websocket.send_json({
            "type": "status",
            "data": "Transcribing..."
        })
        
        transcription = await stt_service.transcribe_audio(audio_bytes)
        user_text = transcription.text
        
        # Send transcript to client
        await websocket.send_json({
            "type": "transcript",
            "data": user_text
        })
        
        # Process with agent
        await process_user_message(
            websocket,
            session_id,
            user_text,
            tts_service,
            memory_service,
            orchestrator
        )
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": "Failed to process audio"
        })


async def handle_text_input(
    websocket: WebSocket,
    session_id: str,
    text: str,
    tts_service: TTSService,
    memory_service: MemoryService,
    orchestrator: OrchestratorAgent
):
    """Handle text input from client"""
    try:
        await process_user_message(
            websocket,
            session_id,
            text,
            tts_service,
            memory_service,
            orchestrator
        )
    except Exception as e:
        logger.error(f"Text processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": "Failed to process message"
        })


async def process_user_message(
    websocket: WebSocket,
    session_id: str,
    user_text: str,
    tts_service: TTSService,
    memory_service: MemoryService,
    orchestrator: OrchestratorAgent
):
    """Process user message through agent pipeline"""
    try:
        # Add user message to memory
        user_message = Message(
            role=MessageRole.USER,
            content=user_text
        )
        await memory_service.add_message(session_id, user_message)
        
        # Get conversation history
        history = await memory_service.get_conversation_history(session_id)
        context_summary = await memory_service.get_context_summary(session_id)
        
        # Route to appropriate agent
        await websocket.send_json({
            "type": "status",
            "data": "Thinking..."
        })
        
        routing_response = await orchestrator.process(
            user_text,
            history[:-1],  # Exclude current message
            {"summary": context_summary}
        )
        
        # Get selected agent
        selected_agent_name = routing_response.metadata.get("selected_agent", "general")
        agent_type = orchestrator.get_agent_type_from_name(selected_agent_name)
        selected_agent = services['agents'][agent_type]
        
        # Generate response
        agent_response = await selected_agent.process(
            user_text,
            history[:-1],
            {"enable_tools": False}  # Disable tools for POC simplicity
        )
        
        response_text = agent_response.content
        
        # Send text response
        emotion_value = agent_response.emotion.value if (agent_response.emotion and hasattr(agent_response.emotion, 'value')) else "neutral"
        await websocket.send_json({
            "type": "response",
            "data": response_text,
            "agent": selected_agent_name,
            "emotion": emotion_value
        })
        
        # Add assistant message to memory
        assistant_message = Message(
            role=MessageRole.ASSISTANT,
            content=response_text,
            agent_type=agent_type,
            emotion=agent_response.emotion
        )
        await memory_service.add_message(session_id, assistant_message)
        
        # Synthesize speech
        await websocket.send_json({
            "type": "status",
            "data": "Generating speech..."
        })
        
        audio_bytes = await tts_service.synthesize_speech(response_text)
        
        # Send audio response
        import base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        await websocket.send_json({
            "type": "audio",
            "data": audio_base64
        })
        
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        raise


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    try:
        memory_service = services['memory']
        history = await memory_service.get_conversation_history(session_id)
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "agent": msg.agent_type.value if msg.agent_type else None
                }
                for msg in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )



# ============================================================================
# PHONE CALL ENDPOINTS (Twilio Integration)
# ============================================================================

@app.post("/api/phone/voice")
async def handle_inbound_call(request: dict):
    """
    Handle inbound phone calls from Twilio
    
    Twilio sends POST request with call details and speech input
    """
    try:
        # Get speech input from Twilio
        speech_result = request.get('SpeechResult', '')
        call_sid = request.get('CallSid', '')
        from_number = request.get('From', '')
        
        logger.info(f"Inbound call from {from_number}: {speech_result}")
        
        if speech_result:
            # Process with AI (simplified for now)
            # TODO: Connect to orchestrator agent
            response_text = f"I heard you say: {speech_result}. How can I help you further?"
        else:
            response_text = "Hello! How can I help you today?"
        
        # Generate TwiML response
        twiml = services['phone'].create_inbound_response(speech_result)
        
        return JSONResponse(
            content=twiml,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Inbound call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route("/api/phone/outbound", methods=["GET", "POST"])
async def make_outbound_call(to_number: str, message: str):
    """
    Make an outbound call
    
    Args:
        to_number: Phone number to call (E.164 format, e.g., +1234567890)
        message: Message to speak
    """
    try:
        result = services['phone'].make_outbound_call(to_number, message)
        return result
    except Exception as e:
        logger.error(f"Outbound call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phone/status/{call_sid}")
async def get_call_status(call_sid: str):
    """Get status of a call"""
    try:
        status = services['phone'].get_call_status(call_sid)
        return status
    except Exception as e:
        logger.error(f"Call status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/phone/test")
async def test_phone_config():
    """Test phone configuration"""
    try:
        settings = get_settings()
        return {
            "phone_number": settings.twilio_phone_number,
            "account_configured": bool(settings.twilio_account_sid),
            "status": "ready"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard(days: int = 7):
    """Get analytics dashboard data"""
    try:
        stats = services['analytics'].get_dashboard_stats(days)
        return stats
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/export")
async def export_analytics(days: int = 30):
    """Export analytics report"""
    try:
        report = services['analytics'].export_report(days)
        return JSONResponse(
            content=report,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=analytics_report.json"}
        )
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
