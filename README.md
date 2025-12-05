# RAVEN - Real-time Automatic Voice Execution Network

A voice assistant built in Python that processes commands through voice input or CLI testing.

**RAVEN** = **Real-time Automatic Voice Execution Network**

## Features

- **Dual Intent Detection**: Heuristic (fast regex) and AI-based modes
- **Voice & CLI Input**: Wake word detection with Porcupine or CLI for testing
- **Action System**: Weather, web browsing, media playback, time queries
- **GUI Settings Panel**: Configure mode, model, and audio settings
- **Modular Design**: Easy to extend with new commands and processors

## Project Structure

```
Raven_Assistant/
├── main.py                    # Entry point
├── data/
│   ├── settings.json         # Configuration
│   └── host_tlds.json        # TLD reference
├── porcupine/
│   └── Hey-Raven_...ppn      # Wake word model
└── raven/
    ├── settings.py
    ├── gui.py
    └── assistant/
        ├── processor.py              # Intent router
        ├── heuristic_processor.py    # Regex-based detection
        ├── ai_processor.py           # AI detection (extensible)
        └── actions/
            ├── basic.py
            ├── weather.py
            ├── web.py
            └── media.py
```

## Installation

### Requirements

- Python 3.9+
- Windows

### Dependencies

Install required packages:

```bash
pip install pvporcupine dearpygui SpeechRecognition requests keyboard
```

These packages provide wake word detection, GUI, speech-to-text, HTTP requests, and hotkey support.

### Setup

1. Create a `.env` file in the project root with your Picovoice access key:
   ```
   RAVEN_PV_ACCESS_KEY=your_key_here
   ```

2. Edit `data/settings.json` to configure your preferences

## Usage

### Running RAVEN

```bash
python main.py
```

### Debug Mode (CLI)

Set `debug_mode = True` in `main.py` to test commands via terminal:

```
Enter a command >> play lofi music
Enter a command >> what's the weather in seattle
Enter a command >> search for python
```

### Voice Mode

Set `debug_mode = False` to use Porcupine wake word detection. Say "Hey Raven" to activate.

### Settings

Press **Tab+`** to open the settings panel and adjust:
- AI mode (heuristics or ai)
- AI model
- Audio settings

## Intent Types

| Intent | Example |
|--------|---------|
| `greeting` | "hello", "hi", "hey" |
| `time` | "what time is it" |
| `weather` | "weather in boston" |
| `open` | "open youtube" |
| `play` | "play lofi music" |
| `stop` | "stop", "pause" |
| `search` | "search for python" |

## Configuration

### `data/settings.json`

```json
{
  "ai_mode": "heuristics",
  "ai_model": "gemma:2b",
  "volume": 50,
  "mic_sensitivity": 50
}
```

See the file for all available options.

## Extending RAVEN

### Add Custom Actions

Create a function in `raven/assistant/actions/` and add handling in `processor.py`.

### Add AI Detection

Edit `raven/assistant/ai_processor.py` to implement your own intent detection logic.

## Troubleshooting

- **Porcupine Error**: Verify `RAVEN_PV_ACCESS_KEY` is set in `.env`
- **No Audio**: Check microphone settings or test with CLI mode
- **GUI Issues**: Ensure DearPyGUI is installed with `pip install dearpygui`



## License

Open source and available for modification.
