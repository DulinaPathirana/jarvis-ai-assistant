"""Voice Input Module - Speech-to-Text using Whisper"""

import whisper
import pyaudio
import wave
import tempfile
import os
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceInput:
    def __init__(self, model_size: str = "base"):
        """Initialize Whisper model for STT
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        logger.info(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        logger.info("Whisper model loaded successfully")
        
        # Audio recording parameters
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
    def record_audio(self, duration: int = 5, filename: Optional[str] = None) -> str:
        """Record audio from microphone
        
        Args:
            duration: Recording duration in seconds
            filename: Output filename (creates temp file if None)
            
        Returns:
            Path to recorded audio file
        """
        if filename is None:
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            filename = temp_file.name
            temp_file.close()
        
        logger.info(f"Recording for {duration} seconds...")
        
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        frames = []
        
        for _ in range(0, int(self.RATE / self.CHUNK * duration)):
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        logger.info("Recording finished")
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save recording
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return filename
    
    def transcribe(self, audio_path: str, language: str = "en") -> str:
        """Transcribe audio file to text using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Transcribed text
        """
        logger.info(f"Transcribing {audio_path}...")
        
        result = self.model.transcribe(audio_path, language=language)
        text = result["text"].strip()
        
        logger.info(f"Transcription: {text}")
        return text
    
    def listen_and_transcribe(self, duration: int = 5, language: str = "en") -> str:
        """Record audio and transcribe in one step
        
        Args:
            duration: Recording duration in seconds
            language: Language code
            
        Returns:
            Transcribed text
        """
        audio_path = self.record_audio(duration)
        
        try:
            text = self.transcribe(audio_path, language)
            return text
        finally:
            # Clean up temp file
            if os.path.exists(audio_path):
                os.remove(audio_path)
    
    def continuous_listen(self, callback, silence_threshold: float = 0.5):
        """Continuously listen for voice input (for future wake-word integration)
        
        Args:
            callback: Function to call with transcribed text
            silence_threshold: Threshold for detecting silence
        """
        # TODO: Implement VAD (Voice Activity Detection) and wake-word detection
        # This will be integrated with Porcupine for wake-word functionality
        pass
