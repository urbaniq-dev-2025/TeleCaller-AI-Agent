"""
Real-time processing loop that evaluates sessions and broadcasts suggestions.
Runs continuously while calls are active.
"""

import asyncio
import time
from typing import Dict

from sessions.session_manager import session_manager
from coaching.engine import coaching_engine
from api.websocket import manager
from utils.logger import logger

from config import settings


class ProcessingLoop:
    """Manages the real-time processing loop."""
    
    def __init__(self):
        self.is_running = False
        self.loop_task: asyncio.Task = None
        self.evaluation_interval = 0.5  # Evaluate every 500ms
    
    async def start(self):
        """Start the processing loop."""
        if self.is_running:
            logger.warning("Processing loop already running")
            return
        
        self.is_running = True
        self.loop_task = asyncio.create_task(self._run_loop())
        logger.info("Processing loop started")
    
    async def stop(self):
        """Stop the processing loop."""
        self.is_running = False
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
        logger.info("Processing loop stopped")
    
    async def _run_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                await self._evaluate_and_broadcast()
                await asyncio.sleep(self.evaluation_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(self.evaluation_interval)
    
    async def _evaluate_and_broadcast(self):
        """Evaluate all active sessions and broadcast suggestions."""
        active_sessions = session_manager.get_active_sessions()
        
        if not active_sessions:
            return  # No active calls
        
        # Log evaluation cycle (every 10 cycles = ~5 seconds)
        if not hasattr(self, '_eval_count'):
            self._eval_count = 0
        self._eval_count += 1
        
        if self._eval_count % 10 == 0:
            logger.debug(f"Processing loop: Evaluating {len(active_sessions)} active session(s)")
        
        for session_id, session in active_sessions.items():
            try:
                # Log session metrics periodically
                if self._eval_count % 10 == 0:
                    logger.debug(
                        f"Session {session_id} - Agent: vol={session.metrics.agent.volume_db:.1f}dB, "
                        f"wpm={session.metrics.agent.wpm:.1f}, speaking={session.metrics.agent.is_speaking}, "
                        f"Customer: speaking={session.metrics.customer.is_speaking}, "
                        f"Interruptions: {session.metrics.interruptions}"
                    )
                
                # Evaluate session
                suggestion = coaching_engine.evaluate_session(session)
                
                if suggestion:
                    # Broadcast to UI
                    await manager.send_to_ui(
                        session_id,
                        {
                            "type": "suggestion",
                            "data": suggestion
                        }
                    )
                    
                    logger.info(
                        f"Broadcasted suggestion {suggestion['type']} "
                        f"to session {session_id}"
                    )
            
            except Exception as e:
                logger.error(f"Error evaluating session {session_id}: {e}", exc_info=True)


# Global processing loop instance
processing_loop = ProcessingLoop()
