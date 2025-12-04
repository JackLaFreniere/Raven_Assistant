from raven.settings import load_settings
from raven.gui import create_gui
from raven.assistant.listener import start_listener
from raven.assistant.processor import process_command
import threading
import time
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

    if debug_mode:
        while program_enabled:
            command = input("Enter a command >> ")
            process_command(command, settings)
    else:
        if settings["start_visible"]:
            open_gui(settings)
    
        keyboard.add_hotkey("tab+`", lambda: open_gui(settings))

        # Start assistant thread
        threading.Thread(target=start_listener, args=(settings,), daemon=True).start()

        # Mainloop to keep the program running
        while program_enabled:
            time.sleep(0.1)

def open_gui(settings):
    """
    Attempts to open the GUI with a reference to the current settings and a callback to properly update main.py when it closes.
    """

    global gui_open
    if not gui_open:
        gui_open = True
        create_gui(settings, close_gui, shutdown_program)

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
