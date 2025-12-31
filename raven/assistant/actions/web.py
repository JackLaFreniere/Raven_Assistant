import re
import webbrowser
from urllib.parse import quote_plus
import json
from pathlib import Path
from ...settings import print

# Load host->tld mapping from repo `data/host_tlds.json`
HOST_TLDS = {}
try:
    mapping_path = Path(__file__).resolve().parents[3] / "data" / "host_tlds.json"
    if mapping_path.exists():
        with open(mapping_path, "r", encoding="utf-8") as fh:
            HOST_TLDS = json.load(fh)
except Exception:
    HOST_TLDS = {}


def handle_open(target: str):
    print(f"Opening: {target}")
    t = target.strip()

    if re.search(r"^https?://", t, re.IGNORECASE):
        url = t
    else:
        token = t.lower()
        mapped = HOST_TLDS.get(token)
        if mapped:
            url = "https://" + mapped if not re.search(r"^https?://", mapped) else mapped
        else:
            # If it has a space and isn't in the mapping, treat as search
            if ' ' in t:
                handle_search(t)
                return
            if '.' in token:
                url = "https://" + t
            else:
                url = f"https://{t}.com"

    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Could not open target: {e}")


def handle_search(query: str):
    print(f"Searching for: {query}")
    url = "https://www.google.com/search?q=" + quote_plus(query)
    try:
        webbrowser.open(url)
    except Exception:
        print("Failed to open web browser for search.")
