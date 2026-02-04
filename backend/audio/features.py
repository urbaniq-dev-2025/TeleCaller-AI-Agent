"""
Audio feature extraction.
Extracts volume, pace, and other features from audio chunks.
"""

import numpy as np
import audioop
from typing import Tuple, Optional
import math

from config import settings
from utils.logger import logger


def decode_mulaw(audio_chunk: bytes) -> np.ndarray:
    """
    Decode mu-law encoded audio to linear PCM.
    Twilio sends audio in mu-law format.
    
    Args:
        audio_chunk: Mu-law encoded audio bytes
        
    Returns:
        NumPy array of 16-bit PCM samples
    """
    try:
        # Convert mu-law to linear PCM (16-bit)
        linear_pcm = audioop.ulaw2lin(audio_chunk, 2)  # 2 = 16-bit
        # Convert to numpy array
        audio_array = np.frombuffer(linear_pcm, dtype=np.int16)
        return audio_array.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
    except Exception as e:
        logger.error(f"Error decoding mu-law audio: {e}")
        return np.array([], dtype=np.float32)


def calculate_rms_energy(audio_array: np.ndarray) -> float:
    """
    Calculate RMS (Root Mean Square) energy of audio.
    
    Args:
        audio_array: Normalized audio samples (-1 to 1)
        
    Returns:
        RMS energy value
    """
    if len(audio_array) == 0:
        return 0.0
    
    rms = np.sqrt(np.mean(audio_array ** 2))
    return rms


def calculate_volume_db(audio_array: np.ndarray, reference: float = 1.0) -> float:
    """
    Calculate volume in decibels.
    
    Args:
        audio_array: Normalized audio samples
        reference: Reference level (default 1.0 for normalized audio)
        
    Returns:
        Volume in dB
    """
    rms = calculate_rms_energy(audio_array)
    
    if rms == 0:
        return -60.0  # Silence threshold
    
    # Convert to dB
    db = 20 * math.log10(rms / reference)
    
    # Clamp to reasonable range
    return max(-60.0, min(0.0, db))


def estimate_speaking_rate(audio_buffer: list, sample_rate: int = 8000) -> float:
    """
    Estimate speaking rate (words per minute) from audio buffer.
    This is a simple approximation for PoC.
    
    Args:
        audio_buffer: List of audio chunks
        sample_rate: Audio sample rate
        
    Returns:
        Estimated words per minute
    """
    if not audio_buffer:
        return 0.0
    
    # Calculate total duration
    total_samples = sum(len(chunk) for chunk in audio_buffer)
    duration_seconds = total_samples / sample_rate
    
    if duration_seconds == 0:
        return 0.0
    
    # Simple heuristic: count energy peaks as "syllables"
    # This is a rough approximation
    peak_count = 0
    threshold = 0.1  # Energy threshold for peaks
    
    for chunk in audio_buffer:
        try:
            audio_array = decode_mulaw(chunk)
            if len(audio_array) > 0:
                energy = calculate_rms_energy(audio_array)
                if energy > threshold:
                    peak_count += 1
        except Exception:
            continue
    
    # Estimate: average word has ~2 syllables, so syllables/2 = words
    # Scale to per minute
    if duration_seconds > 0:
        words_estimate = (peak_count / 2) / (duration_seconds / 60)
        return min(300.0, max(0.0, words_estimate))  # Clamp to 0-300 WPM
    
    return 0.0


def calculate_silence_duration(
    audio_buffer: list,
    silence_threshold_db: float = -50.0,
    sample_rate: int = 8000
) -> float:
    """
    Calculate duration of silence in audio buffer.
    
    Args:
        audio_buffer: List of audio chunks
        silence_threshold_db: Volume threshold below which is considered silence
        sample_rate: Audio sample rate
        
    Returns:
        Silence duration in seconds
    """
    if not audio_buffer:
        return 0.0
    
    silence_samples = 0
    
    for chunk in audio_buffer:
        try:
            audio_array = decode_mulaw(chunk)
            if len(audio_array) > 0:
                volume_db = calculate_volume_db(audio_array)
                if volume_db < silence_threshold_db:
                    silence_samples += len(audio_array)
        except Exception:
            continue
    
    return silence_samples / sample_rate


def extract_audio_features(
    audio_chunk: bytes,
    audio_buffer: Optional[list] = None
) -> Tuple[float, float, bool]:
    """
    Extract key features from an audio chunk.
    
    Args:
        audio_chunk: Raw audio chunk (mu-law encoded)
        audio_buffer: Optional buffer for sliding window analysis
        
    Returns:
        Tuple of (volume_db, wpm_estimate, is_speaking)
    """
    try:
        # Decode audio
        audio_array = decode_mulaw(audio_chunk)
        
        if len(audio_array) == 0:
            return (-60.0, 0.0, False)
        
        # Calculate volume
        volume_db = calculate_volume_db(audio_array)
        
        # Estimate speaking rate (requires buffer)
        wpm = 0.0
        if audio_buffer:
            wpm = estimate_speaking_rate(audio_buffer + [audio_chunk])
        
        # Simple speaking detection (volume above threshold)
        is_speaking = volume_db > -40.0
        
        return (volume_db, wpm, is_speaking)
        
    except Exception as e:
        logger.error(f"Error extracting audio features: {e}")
        return (-60.0, 0.0, False)
