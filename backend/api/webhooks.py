"""
Twilio webhook handlers for call events and media streams.
"""

from fastapi import APIRouter, Request, Form, Response
from twilio.twiml.voice_response import VoiceResponse, Start, Stream, Pause
from typing import Optional

from config import settings
from sessions.session_manager import session_manager
from utils.logger import logger

router = APIRouter()


@router.post("/twilio/voice/status")
async def handle_voice_status(request: Request):
    """
    Handle Twilio voice status webhook.
    Called when call status changes (ringing, in-progress, completed, etc.)
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        
        logger.info(f"Call status update: {call_sid} - {call_status}")
        
        if call_status == "in-progress":
            # Call connected - create session (if not already created)
            session = session_manager.get_session_by_call_sid(call_sid)
            if not session:
                session = session_manager.create_session(call_sid)
                logger.info(f"Created session for call: {call_sid}")
        
        elif call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
            # Call ended - end session
            session_manager.end_session(call_sid)
            logger.info(f"Ended session for call: {call_sid}")
        
        return Response(content="OK", status_code=200, media_type="text/plain")
    
    except Exception as e:
        logger.error(f"Error handling voice status webhook: {e}", exc_info=True)
        return Response(content="OK", status_code=200, media_type="text/plain")  # Return OK to avoid Twilio retries


@router.post("/twilio/voice/incoming")
async def handle_incoming_call(request: Request):
    """
    Handle incoming call webhook.
    Returns TwiML to start media stream.
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        
        if not call_sid:
            logger.error("No CallSid in incoming call webhook")
            response = VoiceResponse()
            response.say("Error processing call.")
            return Response(content=str(response), media_type="application/xml")
        
        logger.info(f"Incoming call: {call_sid}")
        
        # Create session
        session = session_manager.create_session(call_sid)
        
        # Get tunnel URL for media stream
        # Use tunnel_url from settings, or construct from request if not set
        if settings.tunnel_url:
            base_url = settings.tunnel_url.replace('https://', 'wss://').replace('http://', 'ws://')
        else:
            # Try to get from request headers (when behind ngrok/proxy)
            host = request.headers.get('host', 'localhost:8000')
            # Remove port 80/443 if present (not needed for WebSocket)
            if host.endswith(':80'):
                host = host[:-3]
            elif host.endswith(':443'):
                host = host[:-4]
            
            # If host contains ngrok or cloudflare, use wss
            if 'ngrok' in host.lower() or 'cloudflare' in host.lower() or 'trycloudflare' in host.lower():
                scheme = 'wss'
            else:
                # Check if request came via HTTPS
                forwarded_proto = request.headers.get('x-forwarded-proto', '')
                referer = request.headers.get('referer', '')
                if forwarded_proto == 'https' or 'https://' in referer or 'https' in str(request.url):
                    scheme = 'wss'
                else:
                    scheme = 'ws'
            base_url = f"{scheme}://{host}"
        
        # IMPORTANT: Twilio uses the call_sid initially, but will send stream_sid in events
        # The WebSocket endpoint accepts call_sid and will map it to stream_sid when received
        media_stream_url = f"{base_url}/ws/twilio/media/{call_sid}"
        
        logger.info(f"Media stream URL: {media_stream_url}")
        logger.info(f"Expected WebSocket protocol: wss:// (secure WebSocket)")
        logger.info(f"Make sure ngrok/cloudflared supports WebSocket upgrades")
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Start media stream
        start = Start()
        stream = Stream(
            url=media_stream_url,
            name="media_stream"
        )
        start.stream(stream)
        response.append(start)
        
        # Add a simple greeting
        response.say("Call connected. Coaching is active.", voice="alice")
        
        # Keep call alive - add a long pause to keep the call active
        # This prevents the call from ending immediately
        pause = Pause(length=300)  # 5 minutes max (300 seconds)
        response.append(pause)
        
        # Alternative: If you want to dial a number, uncomment:
        # dial = response.dial()
        # dial.number("+1234567890")  # Replace with actual number
        
        twiml = str(response)
        
        logger.info(f"Returning TwiML for call: {call_sid}")
        logger.debug(f"TwiML: {twiml}")
        
        return Response(content=twiml, media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Error handling incoming call webhook: {e}", exc_info=True)
        # Return error TwiML instead of 500
        try:
            response = VoiceResponse()
            response.say("An error occurred. Please try again.")
            return Response(content=str(response), media_type="application/xml")
        except:
            return Response(content="<Response><Say>Error</Say></Response>", media_type="application/xml")


@router.post("/twilio/media/start")
async def handle_media_start(request: Request):
    """
    Handle media stream start event.
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        stream_sid = form_data.get("StreamSid")
        
        logger.info(f"Media stream started: {stream_sid} for call: {call_sid}")
        
        # Update session with stream SID
        session = session_manager.get_session_by_call_sid(call_sid)
        if session:
            logger.info(f"Found existing session {session.call_session_id}, updating with stream")
            session_manager.update_session_stream(call_sid, stream_sid)
        else:
            # Create session if it doesn't exist
            logger.info(f"No existing session found, creating new session for call {call_sid}")
            session = session_manager.create_session(call_sid, stream_sid)
            logger.info(f"Created session {session.call_session_id} with stream {stream_sid}")
        
        return Response(content="OK", status_code=200)
    
    except Exception as e:
        logger.error(f"Error handling media start webhook: {e}")
        return Response(content="Error", status_code=500)


@router.post("/twilio/media/stop")
async def handle_media_stop(request: Request):
    """
    Handle media stream stop event.
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        stream_sid = form_data.get("StreamSid")
        
        logger.info(f"Media stream stopped: {stream_sid} for call: {call_sid}")
        
        # End session
        session_manager.end_session(call_sid)
        
        return Response(content="OK", status_code=200)
    
    except Exception as e:
        logger.error(f"Error handling media stop webhook: {e}")
        return Response(content="Error", status_code=500)
