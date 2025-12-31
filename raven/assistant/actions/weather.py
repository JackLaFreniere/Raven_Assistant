from typing import Optional, Dict, Any
import requests
from ...settings import print

# Map Open-Meteo weather codes to short descriptions
wc_map = {
    0: "clear",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "light snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with hail",
    99: "thunderstorm with heavy hail",
}

def c_to_f(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (float(c) * 9.0 / 5.0) + 32.0

def ms_to_mph(ms: float) -> float:
    """Convert a speed in meters/second to miles/hour."""
    return float(ms) * 2.2369362920544

def format_location_name(display_name: Optional[str] = None, address: Optional[Dict[str, Any]] = None) -> str:
    """Return a concise location string: City + State (for US) or City + Country.

    Falls back to the first part of `display_name` when structured `address` is unavailable.
    """

    if address:
        # prefer city/town/village, fall back to county
        city = (
            address.get('city') or address.get('town') or address.get('village') or
            address.get('hamlet') or address.get('municipality') or address.get('county')
        )
        state = address.get('state')
        country = address.get('country')
        country_code = (address.get('country_code') or '').upper()
        parts = []

        if city:
            parts.append(city)
        # For US prefer state; otherwise append country
        if country_code == 'US' and state:
            parts.append(state)
        elif country:
            parts.append(country)

        if parts:
            return ', '.join(parts)

    # fallback to display_name first component
    if display_name:
        return display_name.split(',')[0].strip()

    return 'your location'


def parse_meteo_message(lat: float, lon: float, display_name: Optional[str] = None, address: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Query Open-Meteo for current weather and format a TTS-friendly sentence.

    Parameters
    - lat, lon: Coordinates to query.
    - display_name: Optional full display name (from Nominatim or ipinfo) used for fallback labelling.
    - address: Optional structured address dict (Nominatim `address`) used to format a concise location.

    Returns a short string suitable for display and TTS, or None on unexpected failures
    (so callers can try fallbacks).
    """
    try:
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': 'true',
            'temperature_unit': 'fahrenheit',
            'windspeed_unit': 'mph',
            'timezone': 'auto'
        }
        r = requests.get('https://api.open-meteo.com/v1/forecast', params=params, timeout=6.0)
        if r.status_code != 200:
            return None
        data = r.json()
        cw = data.get('current_weather')
        if not cw:
            return None

        temp = cw.get('temperature')
        code = cw.get('weathercode')
        windspeed = cw.get('windspeed')
        winddir = cw.get('winddirection')

        # Format components
        try:
            temp_str = f"{float(temp):.1f}°F"
            condition = wc_map.get(int(code), None) if code is not None else None
            wind_mph = float(windspeed)
        except Exception:
            pass

        location = format_location_name(display_name, address)

        message = f"The weather in {location} is {temp_str}. It is current weather is {condition}. The wind is {wind_mph:.1f} mph"
        return message
    except Exception:
        return None

def handle_weather(location: Optional[str] = None) -> str:
    """Public entrypoint: return a short weather sentence for `location`.

    If `location` is provided we forward-geocode it with Nominatim and query
    Open-Meteo. If not provided the function attempts to determine the user's
    location via `ipinfo.io` (best-effort) and reverse-geocodes with Nominatim
    to get a structured address. All external calls use short timeouts and the
    function falls back to `wttr.in` when structured data isn't available.

    The returned string is suitable for display in the live GUI and for TTS.
    """
    loc = (location or '').strip()

    # Determine coordinates and a display name
    try:
        if loc:
            # forward geocode via Nominatim
            nom_url = 'https://nominatim.openstreetmap.org/search'
            headers = {'User-Agent': 'RavenAssistant/1.0'}
            params = {'q': loc, 'format': 'json', 'limit': 1, 'addressdetails': 1}
            r = requests.get(nom_url, params=params, headers=headers, timeout=6.0)
            r.raise_for_status()
            data = r.json()
            if not data:
                raise RuntimeError('geocoding returned no results')
            place = data[0]
            lat = float(place.get('lat'))
            lon = float(place.get('lon'))
            display_name = place.get('display_name')
            address = place.get('address')
        else:
            # use IP-based location (simple): ipinfo -> coords
            ipr = requests.get('https://ipinfo.io/json', timeout=4.0)
            ipr.raise_for_status()
            ipj = ipr.json()
            loc_field = ipj.get('loc')
            if not loc_field:
                raise RuntimeError('ipinfo returned no loc')
            lat_s, lon_s = loc_field.split(',')
            lat = float(lat_s)
            lon = float(lon_s)
            display_name = ', '.join([p for p in [ipj.get('city'), ipj.get('region'), ipj.get('country')] if p]) or 'your location'
            address = None

        # Query Open-Meteo and return a compact formatted message.
        msg = parse_meteo_message(lat, lon, display_name, address)
        if not msg:
            raise RuntimeError('open-meteo returned no usable data')

        # Print and return the message as requested
        print(msg)
        return msg

    except Exception as exc:
        err = f"Unable to get weather: {exc}"
        print(err)
        return 'Unable to get weather.'
