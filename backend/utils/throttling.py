"""
Throttling utilities to prevent suggestion spam.
Ensures suggestions don't fire too frequently.
"""

from typing import Dict, Optional
import time

from config import settings
from utils.logger import logger


class SuggestionThrottler:
    """Manages cooldown periods for coaching suggestions."""
    
    def __init__(self):
        # Rule cooldowns: rule_name -> cooldown_seconds
        self.rule_cooldowns: Dict[str, int] = {
            "SPEAKING_TOO_FAST": 30,
            "SPEAKING_TOO_LOUD": 20,
            "SPEAKING_TOO_SOFT": 25,
            "INTERRUPTING_CUSTOMER": 15,
            "TOO_MUCH_SILENCE": 10
        }
    
    def can_trigger(
        self,
        rule_name: str,
        last_trigger_time: float,
        current_time: Optional[float] = None
    ) -> bool:
        """
        Check if a rule can be triggered (cooldown passed).
        
        Args:
            rule_name: Name of the rule
            last_trigger_time: When the rule was last triggered (Unix timestamp)
            current_time: Current time (defaults to time.time())
            
        Returns:
            True if rule can trigger, False if still in cooldown
        """
        if current_time is None:
            current_time = time.time()
        
        if last_trigger_time == 0:
            return True  # Never triggered before
        
        cooldown = self.rule_cooldowns.get(rule_name, 20)  # Default 20 seconds
        time_since_last = current_time - last_trigger_time
        
        return time_since_last >= cooldown
    
    def get_cooldown_remaining(
        self,
        rule_name: str,
        last_trigger_time: float,
        current_time: Optional[float] = None
    ) -> float:
        """
        Get remaining cooldown time for a rule.
        
        Args:
            rule_name: Name of the rule
            last_trigger_time: When the rule was last triggered
            current_time: Current time
            
        Returns:
            Remaining cooldown in seconds (0 if can trigger)
        """
        if current_time is None:
            current_time = time.time()
        
        if last_trigger_time == 0:
            return 0.0
        
        cooldown = self.rule_cooldowns.get(rule_name, 20)
        time_since_last = current_time - last_trigger_time
        remaining = max(0.0, cooldown - time_since_last)
        
        return remaining


# Global throttler instance
throttler = SuggestionThrottler()
