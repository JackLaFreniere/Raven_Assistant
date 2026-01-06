import re
import webbrowser
import builtins
from urllib.parse import quote_plus
import json
from pathlib import Path
from ...settings import print
from AppOpener import open as open_app, give_appnames
from thefuzz import process

# Load host->tld mapping from repo `data/host_tlds.json`
HOST_TLDS = {}
try:
    mapping_path = Path(__file__).resolve().parents[3] / "data" / "host_tlds.json"
    if mapping_path.exists():
        # Use builtins.open because AppOpener overrides the name "open"
        with builtins.open(mapping_path, "r", encoding="utf-8") as fh:
            HOST_TLDS = json.load(fh)
except Exception:
    HOST_TLDS = {}

def handle_open(target: str):
    if not app_open(target):
        web_open(target)

def app_open(target: str):
    apps = list(give_appnames(upper=False))
    best_match = process.extractOne(target, apps)

    if not best_match:
        return False
    
    key, score = best_match
    key = str(key)
    print(f"Key: {key} Score {score}")
    
    # Check if all words from target are present in the matched key
    # This prevents "github" from matching "github desktop"
    target_words = set(target.lower().split())
    key_words = set(key.lower().split())
    
    # All target words must be in the matched app name
    if not target_words.issubset(key_words):
        print(f"Rejected: not all search terms found in '{key}'")
        return False
    
    # Accept if score is high enough (allows for case/spacing differences)
    if score >= 80:
        open_app(key, match_closest=False)
        print(f"Opening {key}")
        return True
    
    return False

def web_open(target: str):
    print(f"Opening: {target}")
    t = target.strip()

    if re.search(r"^https?://", t, re.IGNORECASE):
        url = t
    else:
        token = t.lower()
        # Check mapping first (handles multi-word entries like "youtube music")
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
