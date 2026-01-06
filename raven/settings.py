import json
from pathlib import Path
import builtins

# Store reference to built-in print
_builtin_print = builtins.print

# Primary directory containing the entire project
BASE_DIR = Path(__file__).resolve().parent.parent

# Settings file is stored in: RAVEN_ASSISTANT/data/settings.json
SETTINGS_PATH = BASE_DIR / "data" / "settings.json"

# Default settings (used on first run or when keys are missing)
# CHANGE THESE SETTINGS AS THEY WILL AUTOMATICALLY UPDATE THE JSON FILE
DEFAULT_SETTINGS = {
  "assistant_enabled": True,
  "assistant_name": "Raven",
  "wake_word_enabled": True,
  "stt_enabled": True,
  "tts_enabled": True,
  "start_visible": True,
  "ai_mode": "heuristics",
  "volume": 50,
  "mic_sensitivity": 50,
  "hotkey_enabled": True,
  "hotkey": "",
  "tts_voice": "Default"
}

def load_settings() -> dict:
    """
    Loads the settings.json file.
    - If the file does not exist, create it with DEFAULT_SETTINGS.
    - If the file exists but is missing keys, they are filled in and saved back.
    - If loading fails, DEFAULT_SETTINGS is returned.

    Returns:
        dict: The merged settings dictionary.
    """

    if not SETTINGS_PATH.exists():
        print("settings.json not found — creating a new one.")
        save_settings(DEFAULT_SETTINGS.copy())
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_PATH.open("r", encoding="utf-8") as fh:
            file_data = json.load(fh)

        # Merge file data with defaults (defaults fill in missing keys)
        merged = DEFAULT_SETTINGS.copy()
        for key, default_value in DEFAULT_SETTINGS.items():
            merged[key] = file_data.get(key, default_value)

        # If any keys were missing, save the merged version back to file
        if merged != file_data:
            save_settings(merged)

        return merged

    except Exception as e:
        print(f"Failed to load settings.json — using defaults. Error: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    """
    Safely saves the settings to settings.json.
    Uses a temporary file to avoid corruption on crash or interruption.
    """

    tmp_path = SETTINGS_PATH.with_suffix(".tmp")

    try:
        # Write settings to temp file first
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2)

        # Atomically replace the real settings file
        tmp_path.replace(SETTINGS_PATH)

    except Exception as e:
        print(f"Failed to save settings.json: {e}")

def print(message: str = "", *args, **kwargs):
    """
    Custom print function that automatically adds the assistant name prefix.
    """
    
    prefix = load_settings().get("assistant_name")
    _builtin_print(f"[{prefix}] {message}", *args, **kwargs)

builtins.print = print