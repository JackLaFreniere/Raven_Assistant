"""
Heuristic-based intent detection using regex patterns.
Fast, lightweight, no external dependencies.
"""

import re
from typing import Dict, Optional


def process_heuristic(text: str) -> Dict[str, Optional[str]]:
    """
    Detects intent and extracts payload using regex patterns.
    
    Args:
        text: The user command text
    
    Returns:
        Dict with "intent" and "payload" keys
    """
    
    # Weather commands
    m = re.search(r"\b(?:weather|forecast|temperature|rain|snow|wind)\b(?:.*(?:in|for)\s+(.+))?", text)
    if m:
        loc = m.group(1).strip() if m.group(1) else None
        return {"intent": "weather", "payload": loc}

    # Greeting commands
    if re.search(r"\b(hello|hi|hey|hiya|howdy|yo|good\s+(morning|afternoon|evening)|raven)\b", text):
        return {"intent": "greeting", "payload": None}

    # Time commands
    if re.search(r"\b(time|what(?:'s| is) the time|current time|tell me the time|what time)\b", text):
        return {"intent": "time", "payload": None}

    # Stop/cancel commands
    if re.search(r"\b(stop|cancel|pause|quit|exit|never mind|don't)\b", text):
        return {"intent": "stop", "payload": None}

    # Play commands
    m = re.search(r"\b(?:play|start|listen to|put on)\b\s+(.+)", text)
    if m:
        return {"intent": "play", "payload": m.group(1).strip()}

    # Open/visit commands
    m = re.search(r"\b(?:open|go to|show|visit|take me to|launch)\b\s+([^\n]+)", text)
    if m:
        return {"intent": "open", "payload": m.group(1).strip()}

    # Search commands
    m = re.search(r"\b(?:search for|find|look up|lookup|google|look for|what is|what's)\b\s+(.+)", text)
    if m:
        return {"intent": "search", "payload": m.group(1).strip()}

    # YouTube shorthand
    if re.search(r"\byoutube\b", text):
        payload = re.sub(r"\b(play|open|youtube|on|please)\b", "", text).strip()
        return {"intent": "play", "payload": payload}

    return {"intent": "unknown", "payload": text}
