"""
Configuration management for the Real-Time AI Call Coaching system.
Loads environment variables and provides typed configuration.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Twilio Configuration
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(..., env="TWILIO_PHONE_NUMBER")
    
    # Server Configuration
    backend_port: int = Field(default=8000, env="BACKEND_PORT")
    frontend_port: int = Field(default=3000, env="FRONTEND_PORT")
    tunnel_url: Optional[str] = Field(default=None, env="TUNNEL_URL")
    
    # Optional: OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Audio Processing Settings
    audio_sample_rate: int = Field(default=8000, env="AUDIO_SAMPLE_RATE")
    audio_chunk_size_ms: int = Field(default=50, env="AUDIO_CHUNK_SIZE_MS")
    sliding_window_seconds: int = Field(default=5, env="SLIDING_WINDOW_SECONDS")
    
    # Coaching Rules Thresholds
    agent_wpm_threshold_fast: int = Field(default=160, env="AGENT_WPM_THRESHOLD_FAST")
    agent_volume_threshold_loud: float = Field(default=-20.0, env="AGENT_VOLUME_THRESHOLD_LOUD")
    agent_volume_threshold_soft: float = Field(default=-50.0, env="AGENT_VOLUME_THRESHOLD_SOFT")
    silence_threshold_seconds: int = Field(default=3, env="SILENCE_THRESHOLD_SECONDS")
    interruption_cooldown_seconds: int = Field(default=15, env="INTERRUPTION_COOLDOWN_SECONDS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
