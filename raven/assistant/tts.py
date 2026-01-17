"""
Text-to-Speech module for Raven Assistant.
Handles voice synthesis and speech output.
"""

import pyttsx3
import threading
from typing import List, Optional
from ..settings import print

# Initialize TTS engine (lazy initialization)
_engine = None

def _initialize_engine():
    """Initialize the pyttsx3 engine."""
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            _engine.setProperty('rate', 150)  # Words per minute
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
    return _engine


def get_available_voices() -> List[str]:
    """
    Get list of available voices on the system.
    
    Returns:
        List of voice names
    """
    try:
        engine = _initialize_engine()
        if engine is None:
            return ["Default"]
        
        voices = engine.getProperty('voices')
        return [voice.name for voice in voices] if voices else ["Default"]
    except Exception as e:
        print(f"Failed to get available voices: {e}")
        return ["Default"]


def set_voice(voice_name: str):
    """
    Set the active voice by name.
    
    Args:
        voice_name: Name of the voice to use
    """
    try:
        engine = _initialize_engine()
        if engine is None:
            return
        
        voices = engine.getProperty('voices')
        for voice in voices:
            if voice.name == voice_name:
                engine.setProperty('voice', voice.id)
                return
        
        # If voice not found, use first available
        if voices:
            engine.setProperty('voice', voices[0].id)
    except Exception as e:
        print(f"Failed to set voice: {e}")


def set_volume(volume: float):
    """
    Set the volume level for TTS output.
    
    Args:
        volume: Volume level from 0.0 to 100.0
    """
    try:
        engine = _initialize_engine()
        if engine is None:
            return
        
        # Normalize volume to 0.0-1.0 range
        normalized_volume = max(0.0, min(1.0, volume / 100.0))
        engine.setProperty('volume', normalized_volume)
    except Exception as e:
        print(f"Failed to set volume: {e}")


def speak(text: str, voice_name: Optional[str] = None, volume: Optional[float] = None):
    """
    Speak the given text using TTS.
    
    Args:
        text: The text to speak
        voice_name: Optional voice name to use
        volume: Optional volume level (0-100)
    """
    if not text or not text.strip():
        return
    
    def _speak_in_thread():
        # Create a fresh engine for each call to avoid state issues
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            
            if voice_name:
                voices = engine.getProperty('voices')
                for voice in voices:
                    if voice.name == voice_name:
                        engine.setProperty('voice', voice.id)
                        break
            
            if volume is not None:
                normalized_volume = max(0.0, min(1.0, volume / 100.0))
                engine.setProperty('volume', normalized_volume)
            
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            # Clean up the engine
            if engine is not None:
                try:
                    engine.stop()
                except:
                    pass
    
    # Run in a background thread to avoid blocking
    thread = threading.Thread(target=_speak_in_thread, daemon=True)
    thread.start()
