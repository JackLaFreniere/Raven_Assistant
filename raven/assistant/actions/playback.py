import keyboard
import asyncio
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioSessionControl2

def get_media_status():
    """Returns 1 if media is playing, 0 if paused/stopped, None if no media found"""
    sessions = AudioUtilities.GetAllSessions()
    
    for session in sessions:
        if session.Process:
            try:
                process_name = session.Process.name()
                volume = session.SimpleAudioVolume
                state = session.State
                
                # Debug output
                print(f"{process_name}: State={state}, Volume={volume.GetMasterVolume():.2f}")
                
                # Check if media is actively playing
                if volume.GetMute() == 0 and volume.GetMasterVolume() > 0:
                    # State: 0=Inactive, 1=Active, 2=Expired
                    if state == 1:
                        return 1  # Playing
                    else:
                        return 0  # Paused/Stopped
            except Exception as e:
                # Skip sessions that can't be accessed
                continue
    
    return None  # No media sessions found

def handle_pause():
    if get_media_status():
        """Pause the currently playing media."""
        print("Pausing music...")
        keyboard.press_and_release('play/pause media')
    else:
        print("Music is already paused.")


def handle_resume():
    if not get_media_status():
        """Resume playing paused media."""
        print("Resuming music...")
        keyboard.press_and_release('play/pause media')
    else:
        print("Music is already playing.")
