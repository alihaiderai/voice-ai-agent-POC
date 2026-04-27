"""
Speech-to-Text service using OpenAI Whisper API
"""
from openai import AsyncOpenAI
import io
import wave
from typing import Optional
from models.conversation import TranscriptionResult
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service with OpenAI Whisper API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        logger.info("STT Service initialized with OpenAI Whisper API")
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio bytes to text using OpenAI Whisper API
        
        Args:
            audio_data: Raw audio bytes (WAV format)
            language: Optional language code
            
        Returns:
            TranscriptionResult with text and metadata
        """
        try:
            # Save audio to temporary file for API
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            try:
                # Transcribe with OpenAI Whisper API
                with open(tmp_path, "rb") as audio_file:
                    result = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language or self.settings.whisper_language
                    )
                
                text = result.text.strip()
                
                # Estimate duration from audio data (rough estimate)
                duration = len(audio_data) / (self.settings.sample_rate * 2)  # 16-bit audio
                
                logger.info(f"Transcribed: '{text}'")
                
                return TranscriptionResult(
                    text=text,
                    confidence=0.95,  # API doesn't provide confidence
                    language=language or "en",
                    duration=duration
                )
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    async def transcribe_stream(
        self,
        audio_stream: bytes,
        language: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe streaming audio
        
        For now, uses the same method as batch transcription.
        """
        return await self.transcribe_audio(audio_stream, language)
    
    def is_speech_detected(self, audio_data: bytes, threshold: float = 0.5) -> bool:
        """
        Detect if audio contains speech
        
        Simple length-based detection for POC.
        """
        try:
            # If audio is longer than 0.5 seconds, assume it contains speech
            min_length = int(self.settings.sample_rate * 0.5 * 2)  # 16-bit audio
            return len(audio_data) > min_length
        except Exception as e:
            logger.error(f"Speech detection error: {e}")
            return False
