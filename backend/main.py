"""
Main FastAPI application entry point for Real-Time AI Call Coaching system.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time AI Call Coaching API",
    description="Backend API for real-time call coaching system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "*"  # Allow all for PoC (restrict in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        logger.info("Starting Real-Time AI Call Coaching API")
        logger.info(f"Backend running on port {settings.backend_port}")
        logger.info(f"Log level: {settings.log_level}")
        
        # Start processing loop
        try:
            from processing_loop import processing_loop
            await processing_loop.start()
            logger.info("Processing loop started successfully")
        except Exception as e:
            logger.error(f"Failed to start processing loop: {e}", exc_info=True)
            # Continue anyway - webhooks should still work
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Real-Time AI Call Coaching API")
    
    # Stop processing loop
    from processing_loop import processing_loop
    await processing_loop.stop()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real-Time AI Call Coaching API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/")
async def root_post(request: Request):
    """Fallback POST endpoint for misconfigured webhooks."""
    logger.warning(f"Received POST to root endpoint from {request.client.host}")
    logger.warning(f"Request URL: {request.url}")
    logger.warning(f"Headers: {dict(request.headers)}")
    
    # Try to parse form data to see what Twilio is sending
    try:
        form_data = await request.form()
        logger.warning(f"Form data: {dict(form_data)}")
        
        # Check if it looks like a Twilio webhook
        if "CallSid" in form_data:
            logger.error(f"Twilio webhook misconfigured! CallSid: {form_data.get('CallSid')}")
            logger.error("Please update Twilio webhook to: /webhooks/twilio/voice/incoming")
    except Exception:
        pass
    
    return {
        "error": "Webhook endpoint not found",
        "message": "Please configure Twilio webhooks to use /webhooks/twilio/voice/incoming",
        "correct_url": f"{request.base_url}webhooks/twilio/voice/incoming"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "telecaller-coaching-api",
            "version": "1.0.0"
        }
    )


# Import routers
from api import webhooks, websocket
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Listen on all interfaces (required for ngrok)
        port=settings.backend_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
