import datetime
from .playback import handle_pause
from ...settings import print

def handle_greeting():
    print("Hello there!")


def handle_time():
    now = datetime.datetime.now()
    time_str = now.strftime('%I:%M %p').lstrip('0')
    msg = f"The time is {time_str}"
    print(msg)
    return msg


def handle_stop():
    """Pause music by pressing the media play/pause key."""
    return handle_pause()
