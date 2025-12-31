from typing import Optional, Tuple
from ytmusicapi import YTMusic
import re
import webbrowser
import math
from ...settings import print

def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]+", " ", text.lower()).strip()


def _parse_title_artist(query: str) -> Tuple[str, Optional[str]]:
    """Split queries like 'hello by lionel richie' into (title, artist)."""
    m = re.search(r"(.+?)\s+by\s+(.+)", query, flags=re.IGNORECASE)
    if m:
        title = m.group(1).strip()
        artist = m.group(2).strip()
        return title, artist
    return query, None


def _token_set_similarity(a: str, b: str) -> float:
    ta = set(a.split())
    tb = set(b.split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def _parse_views_to_int(views_val) -> int:
    """Parse YouTube Music view/playCount values like '1.2M', '532K', '1,234,567' into an int.
    Returns 0 if unknown/missing.
    """
    if views_val is None:
        return 0
    if isinstance(views_val, (int, float)):
        v = int(views_val)
        return v if v >= 0 else 0

    s = str(views_val).strip().upper().replace(" ", "")
    # Match decimal + optional K/M/B suffix
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*([KMB])?$", s)
    if m:
        num = float(m.group(1))
        suf = m.group(2)
        if suf == 'K':
            num *= 1_000
        elif suf == 'M':
            num *= 1_000_000
        elif suf == 'B':
            num *= 1_000_000_000
        return int(num)
    # Fallback: strip non-digits (handles '1,234,567')
    digits = re.sub(r"[^0-9]", "", s)
    return int(digits) if digits else 0


def _score_song_result(result: dict, original_query: str, target_artist: Optional[str] = None) -> int:
    """Score a song result to prefer official/close-title matches over covers/remixes."""
    score = 0
    title_raw = result.get("title", "")
    title = title_raw.lower()
    artists = result.get("artists", [])
    artist_names = " ".join([a.get("name", "").lower() for a in artists])
    views_int = _parse_views_to_int(result.get('views') or result.get('playCount'))

    # Title closeness bonuses (kept modest so viewcount dominates minor differences)
    nq = _normalize(original_query)
    nt = _normalize(title_raw)
    if nt == nq:
        score += 35
    elif nt.startswith(nq):
        score += 20
    elif nq in nt:
        score += 12
    # Viewcount dominance: strong log10-based weight + tier bonuses
    if views_int > 0:
        log10v = math.log10(views_int)
        score += int(log10v * 32)  # e.g., 100k(~5) => +160, 10M(~7) => +224
        # Tier bonuses to strongly separate large uploads from small ones
        if views_int >= 100_000_000:
            score += 60
        elif views_int >= 20_000_000:
            score += 40
        elif views_int >= 5_000_000:
            score += 22
        elif views_int >= 1_000_000:
            score += 10
    else:
        # Missing/zero views: likely obscure or bad metadata
        score -= 35

    sim = _token_set_similarity(nt, nq)
    score += int(sim * 35)  # keep overlap helpful but secondary to views

    # Penalize very long titles that likely include extras
    if len(nt.split()) - len(nq.split()) >= 4:
        score -= 20

    # Negative penalties (bad versions)
    bad_keywords = [
        ("kids", -60), ("children", -60), ("cover", -45), ("remix", -35),
        ("instrumental", -30), ("karaoke", -45), ("tribute", -35),
        ("parody", -45), ("acoustic", -20), ("live", -12),
        ("slowed", -35), ("speed up", -35), ("loop", -25),
        ("10 hour", -60), ("1 hour", -55),
        ("marching band", -60), ("pep band", -60), ("marching", -35),
    ]
    for keyword, penalty in bad_keywords:
        if keyword in title:
            score += penalty

    # Positive bonuses (good versions)
    good_keywords = [
        ("official", 26), ("official audio", 34), ("official video", 30),
        ("official music video", 36), ("original", 20),
    ]
    for keyword, bonus in good_keywords:
        if keyword in title:
            score += bonus

    # Prefer results with matching artist names in the artist field
    query_words = original_query.lower().split()
    for word in query_words[:2]:  # Check first 2 words of query
        if word in artist_names and len(word) > 2:
            score += 12

    # Strong artist match bonuses when user specified an artist
    if target_artist:
        na = _normalize(target_artist)
        n_artists = _normalize(artist_names)
        if na and na == n_artists:
            score += 60
        elif na and na in n_artists:
            score += 35
        else:
            overlap = _token_set_similarity(na, n_artists)
            score += int(overlap * 30)

        # If we have a target artist and no overlap at all, lightly penalize
        if na and _token_set_similarity(na, n_artists) == 0:
            score -= 15

    return score


def _select_best_song(results: list, original_query: str, target_artist: Optional[str]) -> Optional[dict]:
    """From a list of search results, pick the best one.
    
    Filters out bad versions and returns the highest-scoring result.
    """
    if not results:
        return None
    
    # Score all results
    scored = []
    for result in results[:15]:  # Check first 15 results
        score = _score_song_result(result, original_query, target_artist)
        v = _parse_views_to_int(result.get('views') or result.get('playCount'))
        scored.append((score, v, result))
    
    # Sort by score descending
    # Sort by score, then views to break ties towards popular uploads
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    
    best_score, best_views, best_result = scored[0]
    
    # Only return if score is reasonable (not all penalties)
    if best_score > -30:
        return best_result
    
    return None


def handle_play(media: str):
    """Search YouTube Music for a song and play the best official version."""
    if not media:
        return
    
    media = media.strip()
    title_query, target_artist = _parse_title_artist(media)
    
    try:
        # Initialize YouTube Music (public search, no auth needed)
        ytmusic = YTMusic()

        # Search for the song (filter to songs only)
        search_results = ytmusic.search(title_query, filter="songs")

        if not search_results:
            return

        # Select the best result (prefer official versions)
        best_result = _select_best_song(search_results, title_query, target_artist)
        
        if not best_result:
            # Fallback to first result anyway
            best_result = search_results[0]

        video_id = best_result.get("videoId")
        if not video_id:
            return

        # Print final confirmation and open
        title = best_result.get("title", "Unknown")
        artist = best_result.get("artists", [{}])[0].get("name", "Unknown")
        print(f"Playing {title} by {artist}")
        
        song_url = f"https://music.youtube.com/watch?v={video_id}"
        webbrowser.open(song_url)

    except Exception:
        pass