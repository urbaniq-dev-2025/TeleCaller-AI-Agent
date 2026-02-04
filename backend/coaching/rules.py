"""
Coaching rules definitions.
Each rule checks a condition and can trigger a suggestion.
"""

from typing import Optional, Dict, Any
import time

from config import settings
from sessions.models import CoachingSession
from utils.logger import logger


class CoachingRule:
    """Base class for coaching rules."""
    
    def __init__(self, name: str, cooldown_seconds: int = 20):
        self.name = name
        self.cooldown_seconds = cooldown_seconds
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """
        Evaluate if this rule should trigger.
        
        Args:
            session: Coaching session
            current_time: Current Unix timestamp
            
        Returns:
            True if rule should trigger
        """
        raise NotImplementedError
    
    def get_condition_description(self) -> str:
        """Get human-readable description of the rule condition."""
        raise NotImplementedError


class SpeakingTooFastRule(CoachingRule):
    """Rule: Agent speaking too fast (WPM > threshold)."""
    
    def __init__(self):
        super().__init__("SPEAKING_TOO_FAST", cooldown_seconds=30)
        self.wpm_threshold = settings.agent_wpm_threshold_fast
        self.duration_seconds = 5  # Must be fast for 5 seconds
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """Check if agent is speaking too fast."""
        if not session.metrics.agent.is_speaking:
            return False
        
        # Check if WPM exceeds threshold
        if session.metrics.agent.wpm > self.wpm_threshold:
            # Check duration (simplified - in real implementation, track start time)
            return True
        
        return False
    
    def get_condition_description(self) -> str:
        return f"Agent WPM > {self.wpm_threshold} for {self.duration_seconds} seconds"


class SpeakingTooLoudRule(CoachingRule):
    """Rule: Agent speaking too loud."""
    
    def __init__(self):
        super().__init__("SPEAKING_TOO_LOUD", cooldown_seconds=20)
        self.volume_threshold = settings.agent_volume_threshold_loud
        self.duration_seconds = 3
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """Check if agent is speaking too loud."""
        if not session.metrics.agent.is_speaking:
            return False
        
        return session.metrics.agent.volume_db > self.volume_threshold
    
    def get_condition_description(self) -> str:
        return f"Agent volume > {self.volume_threshold} dB for {self.duration_seconds} seconds"


class SpeakingTooSoftRule(CoachingRule):
    """Rule: Agent speaking too softly."""
    
    def __init__(self):
        super().__init__("SPEAKING_TOO_SOFT", cooldown_seconds=25)
        self.volume_threshold = settings.agent_volume_threshold_soft
        self.duration_seconds = 5
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """Check if agent is speaking too softly."""
        if not session.metrics.agent.is_speaking:
            return False
        
        return session.metrics.agent.volume_db < self.volume_threshold
    
    def get_condition_description(self) -> str:
        return f"Agent volume < {self.volume_threshold} dB for {self.duration_seconds} seconds"


class InterruptingCustomerRule(CoachingRule):
    """Rule: Agent interrupting customer."""
    
    def __init__(self):
        super().__init__("INTERRUPTING_CUSTOMER", cooldown_seconds=15)
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """Check if agent is interrupting customer."""
        # Both speaking = interruption
        if (session.metrics.agent.is_speaking and 
            session.metrics.customer.is_speaking):
            logger.debug(f"Interruption rule triggered: both speaking")
            return True
        
        return False
    
    def get_condition_description(self) -> str:
        return "Agent speaking while customer is speaking"


class TooMuchSilenceRule(CoachingRule):
    """Rule: Too much silence during agent's turn."""
    
    def __init__(self):
        super().__init__("TOO_MUCH_SILENCE", cooldown_seconds=10)
        self.silence_threshold = settings.silence_threshold_seconds
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """Check if there's too much silence."""
        # Check if agent should be speaking but isn't
        # Simplified: if customer was speaking and now there's silence
        if (not session.metrics.agent.is_speaking and 
            not session.metrics.customer.is_speaking):
            # Check silence duration
            silence_duration = current_time - session.metrics.last_update_time
            return silence_duration > self.silence_threshold
        
        return False
    
    def get_condition_description(self) -> str:
        return f"Silence > {self.silence_threshold} seconds during conversation"


class TestRule(CoachingRule):
    """Test rule: Triggers after 3 seconds of call to verify system is working."""
    
    def __init__(self):
        super().__init__("TEST_RULE", cooldown_seconds=60)  # Only trigger once per minute
        self.trigger_time = 3.0  # Trigger after 3 seconds
    
    def evaluate(self, session: CoachingSession, current_time: float) -> bool:
        """Trigger after call has been active for 3 seconds."""
        call_duration = current_time - session.created_at.timestamp()
        if call_duration >= self.trigger_time:
            # Only trigger once
            if "TEST_RULE" not in session.active_rules:
                logger.info(f"Test rule triggered after {call_duration:.1f} seconds")
                return True
        return False
    
    def get_condition_description(self) -> str:
        return f"Call active for {self.trigger_time} seconds (test rule)"


# All coaching rules
ALL_RULES = [
    TestRule(),  # Add test rule first - triggers easily
    SpeakingTooFastRule(),
    SpeakingTooLoudRule(),
    SpeakingTooSoftRule(),
    InterruptingCustomerRule(),
    TooMuchSilenceRule()
]
