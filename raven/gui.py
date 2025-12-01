import dearpygui.dearpygui as dpg
from .settings import DEFAULT_SETTINGS, save_settings

close_callback = None
shutdown_callback = None

toggles = {
            "assistant_enabled": "Assistant Enabled",
            "stt_enabled": "STT Enabled",
            "wake_word_enabled": "Wake Word Enabled",
            "tts_enabled": "TTS Enabled"
        }

# When programmatically changing widget values we suppress callbacks
suppress_callbacks = False

def exit():
    """
    Handles closing the GUI window and stopping DearPyGUI.
    """

    close_callback()
    dpg.stop_dearpygui()

def create_gui(settings: dict, c_cb: callable, s_cb: callable):
    """
    Creates and runs the Raven Control Panel GUI.

    Parameters
    ----------
    settings : dict
        The settings dictionary being edited.
    c_cb : callable
        Callback executed when the window closes.
    s_cb : callable
        Callback executed when shutting down the entire program.
    """

    global close_callback, shutdown_callback, toggles
    close_callback = c_cb
    shutdown_callback = s_cb

    def checkbox_enabled_callback(sender, app_data, user_data):
        """
        Updates a boolean setting when a checkbox is toggled.

        Behavior:
        - If a checkbox is selected, select all toggles that come before it (by
          the order in `toggles`).
        - If a checkbox is deselected, deselect all toggles that come after it.
        """

        global suppress_callbacks

        # If callbacks are being suppressed (we're programmatically changing
        # values), ignore this event to avoid recursion.
        if suppress_callbacks:
            return

        settings[user_data] = bool(app_data)

        keys = list(toggles.keys())
        try:
            idx = keys.index(user_data)
        except ValueError:
            idx = -1

        # Programmatically change other checkboxes while suppressing their callbacks
        if app_data:
            # Selected: ensure all previous toggles are selected
            suppress_callbacks = True
            try:
                for key in keys[:idx]:
                    if not settings.get(key, DEFAULT_SETTINGS.get(key, False)):
                        settings[key] = True
                        try:
                            dpg.set_value(key, True)
                        except Exception:
                            pass
            finally:
                suppress_callbacks = False
        else:
            # Deselected: clear all toggles that come after it
            suppress_callbacks = True
            try:
                for key in keys[idx + 1:]:
                    if settings.get(key, DEFAULT_SETTINGS.get(key, False)):
                        settings[key] = False
                        try:
                            dpg.set_value(key, False)
                        except Exception:
                            pass
            finally:
                suppress_callbacks = False

        save_settings(settings)

    def value_callback(sender, app_data, user_data):
        """
        Generic callback for non-boolean widgets (sliders, input text, combos).
        """

        settings[user_data] = app_data
        save_settings(settings)

    dpg.create_context()
    dpg.create_viewport(
        title="Raven Control Panel",
        width=600,
        height=475,
        always_on_top=True
    )

    with dpg.window(label="Raven Control Panel", tag="main_win"):
        with dpg.menu_bar():
            dpg.add_menu_item(label="Close Window", callback=exit)
            dpg.add_menu_item(label="                                               ")  # Spacer
            dpg.add_menu_item(label="Shutdown Program", callback=shutdown_callback)

        dpg.add_text("Configure settings below:")
        dpg.add_separator()
        dpg.add_spacer(height=1)

        for key, label in toggles.items():
            dpg.add_checkbox(
                label=label,
                tag=key,
                default_value=settings.get(key, DEFAULT_SETTINGS.get(key, False)),
                callback=checkbox_enabled_callback,
                user_data=key
            )

        dpg.add_separator()
        dpg.add_checkbox(
            label="Start Visible",
            tag="start_visible",
            default_value=settings.get("start_visible", DEFAULT_SETTINGS.get("start_visible", True)),
            callback=value_callback,
            user_data="start_visible"
        )

        dpg.add_separator()
        dpg.add_text("AI Mode")
        dpg.add_combo(
            label="Mode",
            tag="ai_mode",
            items=["ai", "heuristics"],
            default_value=settings.get("ai_mode", DEFAULT_SETTINGS.get("ai_mode", "ai")),
            callback=value_callback,
            user_data="ai_mode"
        )

        # --- Additional settings ---
        dpg.add_separator()
        dpg.add_text("Audio")
        dpg.add_slider_float(
            label="Volume",
            tag="volume",
            default_value=settings.get("volume", DEFAULT_SETTINGS.get("volume", 50.0)),
            min_value=0.0,
            max_value=100.0,
            callback=value_callback,
            user_data="volume"
        )
        dpg.add_slider_float(
            label="Microphone Sensitivity",
            tag="mic_sensitivity",
            default_value=settings.get("mic_sensitivity", DEFAULT_SETTINGS.get("mic_sensitivity", 50.0)),
            min_value=0.0,
            max_value=100.0,
            callback=value_callback,
            user_data="mic_sensitivity"
        )

        dpg.add_separator()
        dpg.add_text("Hotkey")
        dpg.add_checkbox(
            label="Enable Hotkey",
            tag="hotkey_enabled",
            default_value=settings.get("hotkey_enabled", DEFAULT_SETTINGS.get("hotkey_enabled", False)),
            callback=value_callback,
            user_data="hotkey_enabled"
        )
        dpg.add_input_text(
            label="Hotkey",
            tag="hotkey",
            default_value=settings.get("hotkey", DEFAULT_SETTINGS.get("hotkey", "")),
            callback=value_callback,
            user_data="hotkey"
        )

        dpg.add_separator()
        dpg.add_text("TTS")
        voices = settings.get("available_voices", DEFAULT_SETTINGS.get("available_voices", ["Default"]))
        dpg.add_combo(
            label="TTS Voice",
            tag="tts_voice",
            items=voices,
            default_value=settings.get("tts_voice", DEFAULT_SETTINGS.get("tts_voice", voices[0] if voices else "Default")),
            callback=value_callback,
            user_data="tts_voice"
        )

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_win", True)
    dpg.set_exit_callback(exit)
    dpg.start_dearpygui()
    dpg.destroy_context()
