import webbrowser
from urllib.parse import quote_plus
import re


def handle_play(media: str):
    if not media:
        print("[Raven] Play request received but no media specified.")
        return

    m = media.strip()
    print(f"[Raven] Play request received for: {m}")

    if re.search(r"^https?://", m, re.IGNORECASE):
        try:
            webbrowser.open(m)
            return
        except Exception as e:
            print(f"[Raven] Failed to open media URL: {e}")

    query = quote_plus(m)
    yt = f"https://www.youtube.com/results?search_query={query}"
    try:
        webbrowser.open(yt)
    except Exception as e:
        print(f"[Raven] Failed to open YouTube search: {e}")
