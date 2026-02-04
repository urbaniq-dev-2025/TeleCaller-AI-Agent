"""
Voice Activity Detection (VAD) - Simple energy-based VAD.
Detects when someone is speaking vs silence.
"""

import numpy as np
from typing import Optional

from config import settings
from utils.logger import logger
from audio.features import decode_mulaw, calculate_volume_db


class VoiceActivityDetector:
    """Voice Activity Detection using energy-based method."""
    
    def __init__(self, sample_rate: int = 8000, threshold_db: float = -40.0):
        """
        Initialize VAD.
        
        Args:
            sample_rate: Audio sample rate (8000 Hz for Twilio)
            threshold_db: Volume threshold in dB (below this is considered silence)
        """
        self.sample_rate = sample_rate
        self.threshold_db = threshold_db
    
    def is_speech(self, audio_chunk: bytes) -> bool:
        """
        Detect if audio chunk contains speech.
        
        Args:
            audio_chunk: Raw audio bytes (mu-law encoded from Twilio)
            
        Returns:
            True if speech detected, False otherwise
        """
        try:
            # Decode mu-law to numpy array
            audio_array = decode_mulaw(audio_chunk)
            
            if len(audio_array) == 0:
                return False
            
            # Calculate volume
            volume_db = calculate_volume_db(audio_array)
            
            # Simple threshold-based VAD
            return volume_db > self.threshold_db
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return False
    
    def detect_speech_in_buffer(self, audio_buffer: list, threshold: float = 0.3) -> bool:
        """
        Detect speech in a buffer of audio chunks.
        
        Args:
            audio_buffer: List of audio chunks
            threshold: Fraction of chunks that must be speech (0.0 to 1.0)
            
        Returns:
            True if speech detected
        """
        if not audio_buffer:
            return False
        
        speech_count = 0
        total_chunks = 0
        
        for chunk in audio_buffer:
            if chunk:
                total_chunks += 1
                if self.is_speech(chunk):
                    speech_count += 1
        
        if total_chunks == 0:
            return False
        
        speech_ratio = speech_count / total_chunks
        return speech_ratio >= threshold


# Global VAD instance
vad_detector = VoiceActivityDetector(sample_rate=settings.audio_sample_rate)
