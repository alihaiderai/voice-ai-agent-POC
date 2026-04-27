"""
Text-to-Speech service using OpenAI TTS API
"""
from openai import AsyncOpenAI
import io
from typing import Optional
import logging
from config.settings import get_settings

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service with OpenAI TTS API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        logger.info("TTS Service initialized with OpenAI TTS API")
    
    async def synthesize_speech(
        self,
        text: str,
        speed: Optional[float] = None
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS API
        
        Args:
            text: Text to synthesize
            speed: Speech speed multiplier (0.25 to 4.0)
            
        Returns:
            Audio bytes in MP3 format
        """
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for TTS")
                return self._generate_silence()
            
            logger.info(f"Synthesizing: '{text[:50]}...'")
            
            # Generate speech using OpenAI TTS
            response = await self.client.audio.speech.create(
                model="tts-1",  # Use tts-1 for faster, tts-1-hd for higher quality
                voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
                input=text,
                speed=speed or self.settings.voice_speed
            )
            
            # Get audio bytes
            audio_bytes = response.content
            
            logger.info(f"Synthesized {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise
    
    async def synthesize_streaming(
        self,
        text: str,
        chunk_size: int = 512
    ) -> bytes:
        """
        Synthesize speech (streaming not supported by OpenAI TTS yet)
        
        For now, we'll generate the full audio and return it.
        """
        return await self.synthesize_speech(text)
    
    def _generate_silence(self, duration: float = 0.5) -> bytes:
        """Generate silent audio (empty MP3)"""
        # Return minimal valid MP3 data
        return b''
    
    def estimate_duration(self, text: str) -> float:
        """
        Estimate speech duration for text
        
        Rough estimate: ~150 words per minute
        """
        words = len(text.split())
        duration = (words / 150) * 60  # seconds
        return duration
