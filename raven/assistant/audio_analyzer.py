from time import sleep
from dotenv import load_dotenv
from threading import Thread
from collections import deque
from .processor import process_command
import sounddevice as sd
import numpy as np
import speech_recognition as sr
import pvporcupine
import os

# Load Picovoice API key from .env
load_dotenv()
ACCESS_KEY = os.getenv("RAVEN_PV_ACCESS_KEY")
if ACCESS_KEY is None:
    raise ValueError("RAVEN_PV_ACCESS_KEY not found in .env")

porcupine = None
audio_stream = None
agent_name = ""

def start_listener(settings: dict):
    """
    Starts the wake-word listener.
    Detects wake-word and triggers command recording.
    """

    global porcupine, audio_stream, agent_name

    # Wake-word model
    path = "porcupine/Hey-Raven_en_windows_v3_0_0.ppn"

    # Initialize Porcupine
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[path],
        sensitivities=[0.8]
    )

    # Get the agent name from the Wake-word model file name for debugging
    agent_name = path[path.index("-") + 1:path.index("_")]
    print(f"[{agent_name}] Listening for wake word...")

    frame_length = porcupine.frame_length
    sample_rate = porcupine.sample_rate
    recognizer = sr.Recognizer()

    def record_command():
        """
        Records audio after wake-word detection until silence is detected.
        Converts audio to text and processes the command if possible.
        """

        print(f"[{agent_name}] Listening for command...")

        chunk_size = 1024
        silence_threshold = 100
        max_silence_chunks = 15
        silence_chunks = 0
        audio_buffer = deque()

        def record_callback(indata, frames, time_info, status):
            """
            Appends sound data onto a deck unless silence is detected.
            """
            
            # Add audio to buffer and track silence
            nonlocal silence_chunks
            chunk = (indata[:, 0] * 32767).astype(np.int16)
            audio_buffer.append(chunk)
            volume = int(np.abs(chunk).mean())
            silence_chunks = 0 if volume > silence_threshold else silence_chunks + 1

        # Repeatedly run record_callback until there is silence
        with sd.InputStream(
            channels=1,
            samplerate=sample_rate,
            blocksize=chunk_size,
            callback=record_callback
        ):
            while silence_chunks < max_silence_chunks:
                sd.sleep(50)

        # Combine audio data and transcribe what was said
        # If a message was detected, pass on the command to be processed
        try:
            audio_data = np.concatenate(list(audio_buffer)).flatten().tobytes()
            audio = sr.AudioData(audio_data, sample_rate, 2)
            try:
                command_text = recognizer.recognize_google(audio)
                print(f"[{agent_name}] Command received: {command_text}")
                process_command(command_text, settings)
            except sr.UnknownValueError:
                print(f"[{agent_name}] Could not understand audio.")
            except sr.RequestError as e:
                print(f"[{agent_name}] Speech recognition error: {e}")
        except Exception as e:
            print(f"[{agent_name}] Error processing audio: {e}")
    
    def audio_callback(indata, frames, time_info, status):
        """
        Processes incoming audio for wake-word detection.
        Triggers command recording when detected.
        """

        # If this feature isn't enabled, don't run the code
        if not settings.get("assistant_enabled", False) or not settings.get("stt_enabled", False):
            return

        # Get the data from porcupine and process it for the wake word
        pcm = (indata[:, 0] * 32767).astype(np.int16)

        try:
            result = porcupine.process(pcm)
        except Exception as e:
            print(f"[{agent_name}] Porcupine error: {e}")
            return

        # If the wake word was detected and the settings are enabled, start recording the command
        if result >= 0 and settings.get("wake_word_enabled", False):
            print(f"[{agent_name}] WAKE WORD DETECTED!")
            Thread(target=record_command, daemon=True).start()

    audio_stream = sd.InputStream(
        channels=1,
        samplerate=sample_rate,
        blocksize=frame_length,
        callback=audio_callback
    )
    audio_stream.start()

    while True:
        sleep(0.1)
