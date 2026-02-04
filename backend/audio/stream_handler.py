"""
Audio stream handler for processing Twilio media streams.
Handles incoming audio chunks and routes them for processing.
"""

import json
import base64
from typing import Optional, Dict, Any

from utils.logger import logger
from audio.features import extract_audio_features, decode_mulaw, calculate_volume_db
from audio.vad import vad_detector
from sessions.session_manager import session_manager


class AudioStreamHandler:
    """Handles audio stream processing from Twilio."""
    
    def __init__(self):
        self.active_streams: Dict[str, bool] = {}  # stream_sid -> is_active
    
    async def handle_media_event(self, event_data: dict, stream_sid: str):
        """
        Handle a media event from Twilio WebSocket.
        
        Args:
            event_data: Parsed JSON event data
            stream_sid: Twilio Media Stream SID
        """
        try:
            event_type = event_data.get("event")
            
            if event_type == "media":
                await self._process_audio_chunk(event_data, stream_sid)
            elif event_type == "start":
                await self._handle_stream_start(event_data, stream_sid)
            elif event_type == "stop":
                await self._handle_stream_stop(stream_sid)
            else:
                logger.debug(f"Unhandled event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling media event: {e}")
    
    async def _handle_stream_start(self, event_data: dict, stream_sid: str):
        """Handle stream start event."""
        logger.info(f"Media stream started: {stream_sid}")
        self.active_streams[stream_sid] = True
        
        # Get or create session
        session = session_manager.get_session_by_stream_sid(stream_sid)
        if not session:
            call_sid = event_data.get("start", {}).get("callSid")
            if call_sid:
                session = session_manager.get_session_by_call_sid(call_sid)
                if session:
                    session_manager.update_session_stream(call_sid, stream_sid)
    
    async def _handle_stream_stop(self, stream_sid: str):
        """Handle stream stop event."""
        logger.info(f"Media stream stopped: {stream_sid}")
        self.active_streams[stream_sid] = False
        
        # End session
        session = session_manager.get_session_by_stream_sid(stream_sid)
        if session:
            session_manager.end_session(session.call_sid)
    
    async def _process_audio_chunk(self, event_data: dict, stream_sid: str):
        """
        Process an audio chunk from Twilio.
        
        Args:
            event_data: Media event data
            stream_sid: Stream SID
        """
        try:
            media = event_data.get("media", {})
            payload = media.get("payload")
            track = media.get("track")  # "inbound" (customer) or "outbound" (agent)
            
            if not payload:
                return
            
            # Decode base64 payload
            audio_chunk = base64.b64decode(payload)
            
            # Get session
            session = session_manager.get_session_by_stream_sid(stream_sid)
            if not session:
                logger.warning(f"No session found for stream_sid: {stream_sid}")
                return
            if not session.is_active:
                logger.warning(f"Session {session.call_session_id} is not active")
                return
            
            # Log first few chunks to verify audio is being received
            chunk_count = len(session.agent_audio_buffer) + len(session.customer_audio_buffer)
            if chunk_count < 5:
                logger.info(f"Processing audio chunk #{chunk_count} for track: {track}, stream: {stream_sid}")
            
            # Route to appropriate buffer
            if track == "inbound":
                # Customer audio
                session.customer_audio_buffer.append(audio_chunk)
                # Keep buffer size manageable (last 5 seconds)
                max_chunks = (settings.sliding_window_seconds * 1000) // settings.audio_chunk_size_ms
                if len(session.customer_audio_buffer) > max_chunks:
                    session.customer_audio_buffer.pop(0)
                
                # Extract features
                volume_db, wpm, is_speaking = extract_audio_features(
                    audio_chunk,
                    session.customer_audio_buffer
                )
                
                # Update metrics
                session.metrics.customer.volume_db = volume_db
                session.metrics.customer.wpm = wpm
                session.metrics.customer.is_speaking = is_speaking
                
            elif track == "outbound":
                # Agent audio
                session.agent_audio_buffer.append(audio_chunk)
                # Keep buffer size manageable
                max_chunks = (settings.sliding_window_seconds * 1000) // settings.audio_chunk_size_ms
                if len(session.agent_audio_buffer) > max_chunks:
                    session.agent_audio_buffer.pop(0)
                
                # Extract features
                volume_db, wpm, is_speaking = extract_audio_features(
                    audio_chunk,
                    session.agent_audio_buffer
                )
                
                # Update metrics
                session.metrics.agent.volume_db = volume_db
                session.metrics.agent.wpm = wpm
                session.metrics.agent.is_speaking = is_speaking
                
                # Log metrics periodically (every 20 chunks = ~1 second)
                if len(session.agent_audio_buffer) % 20 == 0:
                    logger.debug(
                        f"Agent metrics - Volume: {volume_db:.1f}dB, WPM: {wpm:.1f}, "
                        f"Speaking: {is_speaking}"
                    )
                
                # Check for interruptions (both speaking)
                if session.metrics.agent.is_speaking and session.metrics.customer.is_speaking:
                    session.metrics.interruptions += 1
                    logger.info(f"Interruption detected! Total: {session.metrics.interruptions}")
            
            # Update last update time
            import time
            session.metrics.last_update_time = time.time()
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")


# Global stream handler instance
audio_stream_handler = AudioStreamHandler()
