import re
from typing import Dict, Optional

from .heuristic_processor import process_heuristic
from .ai_processor import process_ai
from .actions.basic import handle_greeting, handle_time, handle_stop
from .actions.playback import handle_resume
from .actions.weather import handle_weather
from .actions.web import handle_open, handle_search
from .actions.media import handle_play


def process_command(command: str, settings: dict):
    """
    Routes command processing to either heuristic or AI processor based on settings.
    
    Args:
        command: The user's command text
        settings: Settings dict with "ai_mode" key ("heuristics" or "ai")
    """
    if not command:
        return
    
    text = command.strip()
    ai_mode = settings.get("ai_mode", "heuristics")
    
    # Route to appropriate processor
    if ai_mode == "ai":
        result = process_ai(text)
    else:
        result = process_heuristic(text)

    intent = result.get("intent")
    payload = result.get("payload")

    print(f"[Assistant] {ai_mode} mode - intent: {intent!r}, payload: {payload!r}")

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
    if intent == "resume":
        return handle_resume()
    if intent == "search":
        return handle_search(payload or "")

    print(f"[Assistant] Unmatched command (raw): '{command}'")
