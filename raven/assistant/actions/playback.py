import keyboard
import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager, GlobalSystemMediaTransportControlsSessionPlaybackStatus
from ...settings import print

async def _is_playing():
    manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = manager.get_current_session()
    if not session:
        return False

    info = session.get_playback_info()
    return info.playback_status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING

def is_playing():
    return asyncio.run(_is_playing())

def handle_pause():
    if is_playing():
        keyboard.press_and_release("play/pause media")
    else:
        print("Already paused")

def handle_resume():
    if not is_playing():
        keyboard.press_and_release("play/pause media")
    else:
        print("Already playing")
