"""
Advanced configuration for Voice AI Agent Platform
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"  # Using gpt-4o-mini (faster and cheaper)
    openai_temperature: float = 0.7
    
    # Twilio Configuration
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # Application
    app_name: str = "Voice AI Agent Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Audio
    sample_rate: int = 16000
    chunk_size: int = 1024
    audio_format: str = "wav"
    
    # Agent
    max_conversation_history: int = 20
    agent_response_timeout: int = 30
    enable_streaming: bool = True
    
    # Memory & RAG
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_rag_results: int = 5
    
    # TTS
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    tts_vocoder: str = "vocoder_models/en/ljspeech/hifigan_v2"
    voice_speed: float = 1.0
    
    # Whisper
    whisper_model: str = "base"
    whisper_language: str = "en"
    whisper_device: str = "cpu"
    
    # Feature Flags
    enable_emotion_detection: bool = True
    enable_rag: bool = True
    enable_tool_use: bool = True
    enable_analytics: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Agent Personalities and System Prompts
AGENT_CONFIGS = {
    "orchestrator": {
        "name": "Orchestrator",
        "role": "Main coordinator that routes conversations to specialized agents",
        "personality": "intelligent, decisive, efficient"
    },
    "support": {
        "name": "Support Agent",
        "role": "Customer support specialist",
        "personality": "empathetic, patient, solution-oriented",
        "expertise": ["troubleshooting", "product knowledge", "issue resolution"]
    },
    "booking": {
        "name": "Booking Agent",
        "role": "Appointment and scheduling specialist",
        "personality": "organized, friendly, detail-oriented",
        "expertise": ["calendar management", "scheduling", "confirmations"]
    },
    "general": {
        "name": "General Agent",
        "role": "Conversational AI for general inquiries",
        "personality": "friendly, knowledgeable, engaging",
        "expertise": ["general knowledge", "casual conversation", "information"]
    },
    "analytics": {
        "name": "Analytics Agent",
        "role": "Conversation analysis and insights",
        "personality": "analytical, precise, data-driven",
        "expertise": ["metrics", "sentiment", "performance tracking"]
    }
}

# Audio Processing Configuration
AUDIO_CONFIG = {
    "vad_aggressiveness": 3,  # Voice Activity Detection (0-3)
    "silence_threshold": 500,  # ms of silence to detect end of speech
    "max_recording_duration": 30,  # seconds
    "noise_reduction": True,
    "auto_gain_control": True
}

# Streaming Configuration
STREAMING_CONFIG = {
    "chunk_size": 512,  # tokens per chunk
    "buffer_size": 3,  # number of chunks to buffer
    "timeout": 0.1  # seconds between chunks
}
