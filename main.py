from raven.settings import load_settings
from raven.gui import create_gui
from raven.assistant.audio_analyzer import start_listener
from raven.assistant.cli_analyzer import start_cli
from time import sleep
import threading
import keyboard

debug_mode = True
gui_open = False
program_enabled = True

def main():
    """
    Executes the main functionality and the heart of the program.
    """

    global program_enabled
    settings = load_settings()

    if settings["start_visible"]:
        open_gui(settings)

    keyboard.add_hotkey("tab+`", lambda: open_gui(settings))

    threading.Thread(target=start_cli if debug_mode else start_listener, args=(settings,), daemon=True).start()

    # Mainloop to keep the program running
    while program_enabled:
        sleep(0.1)

def open_gui(settings):
    """
    Attempts to open the GUI with a reference to the current settings and a callback to properly update main.py when it closes.
    """

    global gui_open
    if not gui_open:
        gui_open = True
        threading.Thread(target=create_gui, args=(settings, close_gui, shutdown_program), daemon=False).start()

def close_gui():
    """
    The callback for the GUI to call to tell main.py that the GUI was closed.
    """
    
    global gui_open
    gui_open = False

def shutdown_program():
    """
    The callback from the GUI to shutdown the entire program.
    """

    global program_enabled
    program_enabled = False

if __name__ == "__main__":
    main()
