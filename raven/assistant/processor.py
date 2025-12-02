import re
from typing import Dict, Optional

from .actions.basic import handle_greeting, handle_time, handle_stop
from .actions.weather import handle_weather
from .actions.web import handle_open, handle_search
from .actions.media import handle_play

def detect_heuristic(text: str) -> Dict[str, Optional[str]]:
    m = re.search(r"\b(?:weather|forecast|temperature|rain|snow|wind)\b(?:.*(?:in|for)\s+(.+))?", text)
    if m:
        loc = m.group(1).strip() if m.group(1) else None
        return {"intent": "weather", "payload": loc}

    if re.search(r"\b(hello|hi|hey|hiya|howdy|yo|good\s+(morning|afternoon|evening)|raven)\b", text):
        return {"intent": "greeting", "payload": None}

    if re.search(r"\b(time|what(?:'s| is) the time|current time|tell me the time|what time)\b", text):
        return {"intent": "time", "payload": None}

    if re.search(r"\b(stop|cancel|pause|quit|exit|never mind|don't)\b", text):
        return {"intent": "stop", "payload": None}

    m = re.search(r"\b(?:play|start|listen to|put on)\b\s+(.+)", text)
    if m:
        return {"intent": "play", "payload": m.group(1).strip()}

    m = re.search(r"\b(?:open|go to|show|visit|take me to|launch)\b\s+([^\n]+)", text)
    if m:
        return {"intent": "open", "payload": m.group(1).strip()}

    m = re.search(r"\b(?:search for|find|look up|lookup|google|look for|what is|what's)\b\s+(.+)", text)
    if m:
        return {"intent": "search", "payload": m.group(1).strip()}

    if re.search(r"\byoutube\b", text):
        payload = re.sub(r"\b(play|open|youtube|on|please)\b", "", text).strip()
        return {"intent": "play", "payload": payload}

    return {"intent": "unknown", "payload": text}

def detect_ai(text: str) -> Dict[str, Optional[str]]:
    return {"intent": "unknown", "payload": text}

def process_command(command: str, settings: dict):
    if not command:
        return
    
    text = command.strip()
    if settings["ai_mode"] == "heuristics":
        result = detect_heuristic(text)
    else:
        result = detect_ai(text)

    intent = result.get("intent")
    payload = result.get("payload")

    print(f"[Raven] {settings["ai_mode"]} intent: {intent!r}, payload: {payload!r}")

    if intent == "greeting":
        return handle_greeting()
    if intent == "time":
        return handle_time()
    if intent == "weather":
        return handle_weather(payload or "")
    if intent == "open":
        return handle_open(payload or "")
    if intent == "play":
        return handle_play(payload or "")
    if intent == "stop":
        return handle_stop()
    if intent == "search":
        return handle_search(payload or "")

    print(f"[Raven] Unmatched command (raw): '{command}'")
