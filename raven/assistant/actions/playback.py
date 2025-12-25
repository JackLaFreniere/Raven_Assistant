import keyboard


def handle_pause():
    """Pause the currently playing media."""
    print("Pausing music...")
    keyboard.press_and_release('play/pause media')


def handle_resume():
    """Resume playing paused media."""
    print("Resuming music...")
    keyboard.press_and_release('play/pause media')
