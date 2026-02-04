"""
WebSocket endpoints for real-time communication.
Handles both UI WebSocket connections and Twilio media streams.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

from utils.logger import logger


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # UI WebSocket connections (session_id -> WebSocket)
        self.ui_connections: Dict[str, WebSocket] = {}
        # Twilio media stream connections (stream_sid -> WebSocket)
        self.media_connections: Dict[str, WebSocket] = {}
        # Active sessions
        self.active_sessions: Set[str] = set()
    
    async def connect_ui(self, session_id: str, websocket: WebSocket):
        """Connect a UI WebSocket client."""
        await websocket.accept()
        self.ui_connections[session_id] = websocket
        self.active_sessions.add(session_id)
        logger.info(f"UI WebSocket connected for session: {session_id}")
    
    async def disconnect_ui(self, session_id: str):
        """Disconnect a UI WebSocket client."""
        if session_id in self.ui_connections:
            try:
                await self.ui_connections[session_id].close()
            except Exception as e:
                logger.error(f"Error closing UI WebSocket for {session_id}: {e}")
            del self.ui_connections[session_id]
            self.active_sessions.discard(session_id)
            logger.info(f"UI WebSocket disconnected for session: {session_id}")
    
    async def connect_media(self, stream_sid: str, websocket: WebSocket):
        """Connect a Twilio media stream WebSocket."""
        await websocket.accept()
        self.media_connections[stream_sid] = websocket
        logger.info(f"Media stream WebSocket connected: {stream_sid}")
    
    async def disconnect_media(self, stream_sid: str):
        """Disconnect a Twilio media stream WebSocket."""
        if stream_sid in self.media_connections:
            try:
                await self.media_connections[stream_sid].close()
            except Exception as e:
                logger.error(f"Error closing media WebSocket for {stream_sid}: {e}")
            del self.media_connections[stream_sid]
            logger.info(f"Media stream WebSocket disconnected: {stream_sid}")
    
    async def send_to_ui(self, session_id: str, message: dict):
        """Send message to UI WebSocket client."""
        if session_id in self.ui_connections:
            try:
                await self.ui_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to UI for {session_id}: {e}")
                await self.disconnect_ui(session_id)
    
    async def broadcast_to_ui(self, message: dict):
        """Broadcast message to all UI connections."""
        disconnected = []
        for session_id, websocket in self.ui_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                disconnected.append(session_id)
        
        # Clean up disconnected clients
        for session_id in disconnected:
            await self.disconnect_ui(session_id)


# Global connection manager instance
manager = ConnectionManager()


from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()


@router.get("/twilio/media/{stream_sid}")
async def websocket_info(stream_sid: str):
    """
    Info endpoint - WebSocket connections should use ws:// or wss:// protocol.
    This endpoint is only for testing. Twilio will connect via WebSocket upgrade.
    """
    return {
        "info": "This is a WebSocket endpoint",
        "message": "Twilio should connect via WebSocket (wss://), not HTTP GET",
        "endpoint": f"/ws/twilio/media/{stream_sid}",
        "stream_sid": stream_sid,
        "note": "If you see this, the HTTP endpoint is working. WebSocket connections will be handled by the @router.websocket decorator above."
    }


@router.websocket("/ui/{session_id}")
async def websocket_ui(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for UI clients to receive coaching suggestions.
    
    Args:
        websocket: WebSocket connection
        session_id: Call session ID
    """
    await manager.connect_ui(session_id, websocket)
    
    try:
        while True:
            # Wait for messages from client (optional - for ping/pong)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        logger.info(f"UI WebSocket disconnected: {session_id}")
        await manager.disconnect_ui(session_id)
    except Exception as e:
        logger.error(f"Error in UI WebSocket for {session_id}: {e}")
        await manager.disconnect_ui(session_id)


@router.websocket("/twilio/media/{stream_sid}")
async def websocket_twilio_media(websocket: WebSocket, stream_sid: str):
    """
    WebSocket endpoint for Twilio media streams.
    Receives audio chunks from Twilio.
    
    Args:
        websocket: WebSocket connection from Twilio
        stream_sid: Twilio Media Stream SID (can be call_sid initially)
    """
    logger.info(f"WebSocket connection attempt received for stream: {stream_sid}")
    logger.info(f"WebSocket headers: {dict(websocket.headers)}")
    logger.info(f"WebSocket subprotocols: {websocket.subprotocols}")
    
    try:
        await manager.connect_media(stream_sid, websocket)
        logger.info(f"Media stream WebSocket accepted: {stream_sid}")
    except Exception as e:
        logger.error(f"Error accepting media stream WebSocket: {e}", exc_info=True)
        raise
    
    try:
        while True:
            # Receive message from Twilio
            data = await websocket.receive_text()
            
            try:
                event_data = json.loads(data)
                event_type = event_data.get("event")
                
                # Log first few events to verify connection
                if not hasattr(websocket_twilio_media, '_event_count'):
                    websocket_twilio_media._event_count = 0
                websocket_twilio_media._event_count += 1
                
                if websocket_twilio_media._event_count <= 5:
                    logger.info(f"Received Twilio event #{websocket_twilio_media._event_count}: {event_type} for stream {stream_sid}")
                
                # Handle media events
                from audio.stream_handler import audio_stream_handler
                await audio_stream_handler.handle_media_event(event_data, stream_sid)
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from Twilio: {e}")
            except Exception as e:
                logger.error(f"Error processing Twilio media event: {e}", exc_info=True)
    
    except WebSocketDisconnect:
        logger.info(f"Twilio media WebSocket disconnected: {stream_sid}")
        await manager.disconnect_media(stream_sid)
        
        # End session
        from sessions.session_manager import session_manager
        session = session_manager.get_session_by_stream_sid(stream_sid)
        if session:
            session_manager.end_session(session.call_sid)
    
    except Exception as e:
        logger.error(f"Error in Twilio media WebSocket for {stream_sid}: {e}")
        await manager.disconnect_media(stream_sid)
