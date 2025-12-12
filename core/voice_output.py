"""Voice Output Module - Text-to-Speech"""

import pyttsx3
import logging
from typing import Optional
from openai import OpenAI
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceOutput:
    def __init__(self, engine_type: str = "pyttsx3", openai_api_key: Optional[str] = None):
        """Initialize TTS engine
        
        Args:
            engine_type: 'pyttsx3' for offline TTS or 'openai' for OpenAI TTS API
            openai_api_key: Required if using OpenAI TTS
        """
        self.engine_type = engine_type
        
        if engine_type == "pyttsx3":
            self.engine = pyttsx3.init()
            self._configure_pyttsx3()
        elif engine_type == "openai":
            if not openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI TTS")
            self.client = OpenAI(api_key=openai_api_key)
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
        
        logger.info(f"Voice output initialized with {engine_type}")
    
    def _configure_pyttsx3(self):
        """Configure pyttsx3 settings"""
        # Set properties
        self.engine.setProperty('rate', 175)    # Speed
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices and set a good one
        voices = self.engine.getProperty('voices')
        # Prefer female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text: str):
        """Speak text using configured TTS engine
        
        Args:
            text: Text to speak
        """
        if not text:
            return
        
        logger.info(f"Speaking: {text}")
        
        if self.engine_type == "pyttsx3":
            self.engine.say(text)
            self.engine.runAndWait()
        elif self.engine_type == "openai":
            self._speak_openai(text)
    
    def _speak_openai(self, text: str, voice: str = "alloy"):
        """Use OpenAI TTS API for high-quality voice output
        
        Args:
            text: Text to speak  
            voice: OpenAI voice (alloy, echo, fable, onyx, nova, shimmer)
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Play audio (simplified - would need proper audio player)
            response.stream_to_file("output.mp3")
            # TODO: Play MP3 file using pygame or similar
            logger.info("OpenAI TTS audio generated")
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        if self.engine_type == "pyttsx3":
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        if self.engine_type == "pyttsx3":
            self.engine.setProperty('volume', volume)
