"""
Hardcoded suggestion messages for coaching.
These are used instead of AI-generated messages for the PoC.
"""

from typing import Dict

# Suggestion messages mapped by rule type
SUGGESTION_MESSAGES: Dict[str, Dict[str, str]] = {
    "TEST_RULE": {
        "message": "✅ System is working! Coaching is active and monitoring your call.",
        "severity": "low"
    },
    "SPEAKING_TOO_FAST": {
        "message": "Slow down your pace slightly to sound more professional and clear.",
        "severity": "medium"
    },
    "SPEAKING_TOO_LOUD": {
        "message": "Lower your tone slightly to sound calmer and more approachable.",
        "severity": "medium"
    },
    "SPEAKING_TOO_SOFT": {
        "message": "Speak a bit louder to ensure the customer can hear you clearly.",
        "severity": "low"
    },
    "INTERRUPTING_CUSTOMER": {
        "message": "Let the customer finish speaking before responding.",
        "severity": "high"
    },
    "TOO_MUCH_SILENCE": {
        "message": "Acknowledge the customer or ask a follow-up question to keep the conversation flowing.",
        "severity": "medium"
    }
}


def get_suggestion_message(rule_type: str) -> Dict[str, str]:
    """
    Get suggestion message for a rule type.
    
    Args:
        rule_type: Type of coaching rule
        
    Returns:
        Dictionary with message and severity
    """
    return SUGGESTION_MESSAGES.get(
        rule_type,
        {
            "message": "Consider adjusting your communication style.",
            "severity": "low"
        }
    )


def create_suggestion(rule_type: str, timestamp: float) -> Dict:
    """
    Create a suggestion object.
    
    Args:
        rule_type: Type of coaching rule
        timestamp: Unix timestamp
        
    Returns:
        Suggestion dictionary
    """
    message_data = get_suggestion_message(rule_type)
    
    return {
        "type": rule_type,
        "message": message_data["message"],
        "severity": message_data["severity"],
        "timestamp": timestamp
    }
