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
    
    # Normalize to lowercase for matching
    text_lower = text.lower()
    
    # Weather commands
    m = re.search(r"\b(?:weather|forecast|temperature|rain|snow|wind)\b(?:.*(?:in|for)\s+(.+))?", text_lower)
    if m:
        loc = m.group(1).strip() if m.group(1) else None
        return {"intent": "weather", "payload": loc}

    # Time commands
    if re.search(r"\b(time|what(?:'s| is) the time|current time|tell me the time|what time)\b", text_lower):
        return {"intent": "time", "payload": None}

    # Stop/cancel commands
    if re.search(r"\b(stop|cancel|pause|quit|exit|never mind|don't)\b", text_lower):
        return {"intent": "stop", "payload": None}

    # Resume/continue commands (standalone, no song name)
    if re.search(r"\b(resume|continue|play|go on|keep going)\b\s*$", text_lower):
        return {"intent": "resume", "payload": None}

    # Play commands (improved patterns)
    # Matches: "play <song>", "play the <song>", "play me <song>", "start <song>", "listen to <song>", "put on <song>"
    m = re.search(r"\b(?:play|start|listen\s+to|put\s+on)\b\s+(?:(?:the|me|some)\s+)?(.+)", text_lower)
    if m:
        payload = m.group(1).strip()
        # Remove common filler words from payload
        payload = re.sub(r"\b(please|thanks?)\b\s*", "", payload).strip()
        return {"intent": "play", "payload": payload}

    # Open/visit commands
    m = re.search(r"\b(?:open|go to|show|visit|take me to|launch)\b\s+([^\n]+)", text_lower)
    if m:
        return {"intent": "open", "payload": m.group(1).strip()}

    # Search commands
    m = re.search(r"\b(?:search for|find|look up|lookup|google|look for|what is|what's)\b\s+(.+)", text_lower)
    if m:
        return {"intent": "search", "payload": m.group(1).strip()}

    # YouTube shorthand
    if re.search(r"\byoutube\b", text_lower):
        payload = re.sub(r"\b(play|open|youtube|on|please)\b", "", text_lower).strip()
        return {"intent": "play", "payload": payload}

    # Greeting commands
    if re.search(r"\b(hello|hi|hey|hiya|howdy|yo|good\s+(morning|afternoon|evening)|raven)\b", text_lower):
        return {"intent": "greeting", "payload": None}

    return {"intent": "unknown", "payload": text}
