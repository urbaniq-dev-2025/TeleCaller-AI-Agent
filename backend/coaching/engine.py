"""
Coaching engine that evaluates rules and generates suggestions.
"""

from typing import Optional, List
import time

from sessions.models import CoachingSession
from sessions.session_manager import session_manager
from coaching.rules import ALL_RULES
from coaching.messages import create_suggestion
from utils.throttling import throttler
from utils.logger import logger


class CoachingEngine:
    """Main coaching engine that evaluates rules and generates suggestions."""
    
    def __init__(self):
        self.rules = ALL_RULES
    
    def evaluate_session(self, session: CoachingSession) -> Optional[dict]:
        """
        Evaluate a session and return a suggestion if any rule triggers.
        
        Args:
            session: Coaching session to evaluate
            
        Returns:
            Suggestion dictionary if rule triggers, None otherwise
        """
        if not session.is_active:
            return None
        
        current_time = time.time()
        
        # Evaluate each rule
        for rule in self.rules:
            try:
                # Check if rule condition is met
                if rule.evaluate(session, current_time):
                    # Check cooldown
                    last_trigger_time = session.active_rules.get(rule.name, 0.0)
                    
                    if throttler.can_trigger(rule.name, last_trigger_time, current_time):
                        # Generate suggestion
                        suggestion = create_suggestion(rule.name, current_time)
                        
                        # Update session state
                        session.last_suggestion_time = current_time
                        session.last_suggestion_type = rule.name
                        session.active_rules[rule.name] = current_time
                        
                        logger.info(
                            f"Rule triggered: {rule.name} for session {session.call_session_id}"
                        )
                        
                        return suggestion
                    else:
                        cooldown_remaining = throttler.get_cooldown_remaining(
                            rule.name, last_trigger_time, current_time
                        )
                        logger.debug(
                            f"Rule {rule.name} in cooldown: {cooldown_remaining:.1f}s remaining"
                        )
            
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                continue
        
        return None
    
    def evaluate_all_active_sessions(self) -> List[dict]:
        """
        Evaluate all active sessions and return suggestions.
        
        Returns:
            List of suggestions (one per session that triggered)
        """
        suggestions = []
        active_sessions = session_manager.get_active_sessions()
        
        for session_id, session in active_sessions.items():
            suggestion = self.evaluate_session(session)
            if suggestion:
                suggestions.append({
                    "session_id": session_id,
                    "suggestion": suggestion
                })
        
        return suggestions


# Global coaching engine instance
coaching_engine = CoachingEngine()
