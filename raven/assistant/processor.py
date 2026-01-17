import re
from typing import Dict, Optional

from .heuristic_processor import process_heuristic
from .ai_processor import process_ai
from .tts import speak
from .actions.basic import handle_greeting, handle_time, handle_stop
from .actions.playback import handle_resume
from .actions.weather import handle_weather
from .actions.web import handle_open, handle_search
from .actions.media import handle_play
from .actions.sequences import handle_run_sequence
from ..settings import print


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

    print(f"{ai_mode} mode - intent: {intent!r}, payload: {payload!r}")

    response = None
    
    if intent == "greeting":
        response = handle_greeting()
    elif intent == "time":
        response = handle_time()
    elif intent == "weather":
        response = handle_weather(payload or "")
    elif intent == "open":
        response = handle_open(payload or "")
    elif intent == "play":
        response = handle_play(payload or "")
    elif intent == "stop":
        response = handle_stop()
    elif intent == "resume":
        response = handle_resume()
    elif intent == "search":
        response = handle_search(payload or "")
    elif intent == "sequence":
        response = handle_run_sequence(payload or "")
    else:
        print(f"Unmatched command (raw): '{command}'")
        return
    
    # If TTS is enabled and we have a response, speak it
    if response and settings.get("tts_enabled", False):
        tts_voice = settings.get("tts_voice", "Default")
        tts_volume = settings.get("volume", 50)
        speak(response, voice_name=tts_voice, volume=tts_volume)
    
    return response
