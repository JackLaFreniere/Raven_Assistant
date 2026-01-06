# RAVEN - Voice Assistant

A Python-based voice assistant with wake word detection and command execution.

## Installation

### Prerequisites
- Python 3.9+
- Windows

### Dependencies

```bash
pip install pvporcupine dearpygui python-dotenv SpeechRecognition requests keyboard sounddevice numpy ytmusicapi AppOpener thefuzz winsdk
```

### Setup

1. Create a `.env` file in the project root with your Picovoice access key:
   ```
   RAVEN_PV_ACCESS_KEY=your_key_here
   ```

2. Edit `data/settings.json` to configure preferences

## Usage

```bash
python main.py
```

- **Voice Mode**: Say "Hey Raven" to activate
- **Debug Mode**: Set `debug_mode = True` in `main.py` to test via CLI
- **Settings**: Press **Tab+`** to open the settings panel
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
