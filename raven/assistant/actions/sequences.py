"""
Handles execution of command sequences (macros).
Sequences are stored in data/sequences/ folder as .seq files.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from ...settings import print


def get_sequences_dir() -> Path:
    """Returns the path to the sequences directory."""
    # Get project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent
    return project_root / "data" / "sequences"


def list_available_sequences() -> List[str]:
    """
    Returns a list of available sequence names (without .seq extension).
    """
    sequences_dir = get_sequences_dir()
    if not sequences_dir.exists():
        return []
    
    sequences = []
    for file in sequences_dir.glob("*.seq"):
        sequences.append(file.stem)
    
    return sorted(sequences)


def load_sequence(sequence_name: str) -> Optional[List[Dict[str, str]]]:
    """
    Loads a sequence file and parses it into a list of commands.
    
    File format (each line):
        intent: payload
    
    Examples:
        play: lofi hip hop
        open: youtube
        weather: New York
    
    Args:
        sequence_name: Name of the sequence (without .seq extension)
    
    Returns:
        List of dicts with "intent" and "payload" keys, or None if file not found
    """
    sequences_dir = get_sequences_dir()
    sequence_file = sequences_dir / f"{sequence_name}.seq"
    
    if not sequence_file.exists():
        print(f"Sequence '{sequence_name}' not found at {sequence_file}")
        return None
    
    commands = []
    try:
        with open(sequence_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse "intent: payload" format
                if ':' not in line:
                    print(f"Warning: Line {line_num} in '{sequence_name}.seq' missing colon, skipping: {line}")
                    continue
                
                intent, payload = line.split(':', 1)
                intent = intent.strip().lower()
                payload = payload.strip()
                
                # Empty payload is allowed (e.g., "time:" or "resume:")
                if not payload:
                    payload = None
                
                commands.append({
                    "intent": intent,
                    "payload": payload
                })
        
        return commands
    
    except Exception as e:
        print(f"Error loading sequence '{sequence_name}': {e}")
        return None


def handle_run_sequence(sequence_name: str):
    """
    Executes a sequence of commands.
    
    Args:
        sequence_name: Name of the sequence to run
    """
    if not sequence_name:
        available = list_available_sequences()
        if available:
            msg = f"Available sequences: {', '.join(available)}"
            print(msg)
            return msg
        else:
            msg = "No sequences available. Create .seq files in data/sequences/"
            print(msg)
            return msg
    
    # Normalize sequence name
    sequence_name = sequence_name.lower().strip()
    
    # Load the sequence
    commands = load_sequence(sequence_name)
    if not commands:
        msg = f"Sequence '{sequence_name}' not found"
        print(msg)
        return msg
        
    # Import handlers here to avoid circular imports
    from .basic import handle_greeting, handle_time, handle_stop
    from .playback import handle_resume
    from .weather import handle_weather
    from .web import handle_open, handle_search
    from .media import handle_play
    
    # Execute each command in sequence
    for idx, cmd in enumerate(commands, 1):
        intent = cmd["intent"]
        payload = cmd["payload"]
        
        print(f"[{idx}/{len(commands)}] Executing: {intent} -> {payload or '(no payload)'}")
        
        try:
            if intent == "greeting":
                handle_greeting()
            elif intent == "time":
                handle_time()
            elif intent == "weather":
                handle_weather(payload or "")
            elif intent == "open":
                handle_open(payload or "")
            elif intent == "play":
                handle_play(payload or "")
            elif intent == "stop":
                handle_stop()
            elif intent == "resume":
                handle_resume()
            elif intent == "search":
                handle_search(payload or "")
            else:
                print(f"Unknown intent in sequence: '{intent}'")
        
        except Exception as e:
            print(f"Error executing command {idx}: {e}")
            # Continue with next command even if one fails
    
    msg = f"Sequence '{sequence_name}' completed"
    print(msg)
    return msg
