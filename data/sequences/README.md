# Command Sequences (Macros)

Raven Assistant now supports **command sequences** - predefined macros that execute multiple commands automatically.

## How to Use

Simply say: **"Run [sequence-name]"** or **"Run sequence [sequence-name]"**

Examples:
- "Run gaming"
- "Run sequence morning"
- "Execute work"

## Creating Your Own Sequences

1. Create a new `.seq` file in the `data/sequences/` folder
2. Name it whatever you want (e.g., `gaming.seq`, `morning.seq`)
3. Add commands in this format:
   ```
   intent: payload
   ```

### Supported Intents

- `greeting:` - Say hello
- `time:` - Get current time
- `weather:` or `weather: City Name` - Get weather
- `open: website.com` - Open a website
- `play: song name` - Play music/video
- `search: query` - Search the web
- `stop:` - Stop current media
- `resume:` - Resume playback

### Example Sequence File

**gaming.seq**:
```
# This is a comment - lines starting with # are ignored
open: discord
play: gaming music mix
open: twitch.tv
```

### Tips

- Use `#` for comments in your sequence files
- Empty lines are ignored
- Sequence names should be lowercase with hyphens or underscores (e.g., `late-night.seq`)
- Commands execute in order from top to bottom
- If a command fails, the sequence continues with the next command

## Available Sequences

The project comes with these example sequences:
- **gaming** - Opens Discord, plays gaming music, opens Twitch
- **morning** - Shows time, weather, plays morning music, opens email
- **work** - Shows weather, plays focus music, opens GitHub and Stack Overflow

Create your own by copying these templates!
