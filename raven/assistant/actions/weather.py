import requests
from urllib.parse import quote_plus

def handle_weather(location: str):
    loc = (location or "").strip()

    def _print_wttr(query: str):
        try:
            url = f"https://wttr.in/{quote_plus(query)}?format=3&u"
            resp = requests.get(url, timeout=6.0)
            if resp.status_code == 200:
                print(f"[Raven] Weather: {resp.text.strip()}")
            else:
                print(f"[Raven] wttr.in returned {resp.status_code}")
        except Exception as e:
            print(f"[Raven] wttr.in request failed: {e}")

    def c_to_f(c):
        return (float(c) * 9.0 / 5.0) + 32.0

    def kmh_to_mph(kmh):
        return float(kmh) * 0.621371

    def _deg_to_compass(deg):
        try:
            d = float(deg) % 360
        except Exception:
            return None
        dirs = [
            'N','NNE','NE','ENE','E','ESE','SE','SSE',
            'S','SSW','SW','WSW','W','WNW','NW','NNW'
        ]
        ix = int((d / 22.5) + 0.5) % 16
        return dirs[ix]

    wc_map = {0: "Clear",1: "Mainly clear",2: "Partly cloudy",3: "Overcast",45: "Fog",48: "Depositing rime fog",51: "Light drizzle",53: "Moderate drizzle",55: "Dense drizzle",56: "Light freezing drizzle",57: "Dense freezing drizzle",61: "Slight rain",63: "Moderate rain",65: "Heavy rain",66: "Light freezing rain",67: "Heavy freezing rain",71: "Slight snow",73: "Moderate snow",75: "Heavy snow",77: "Snow grains",80: "Slight rain showers",81: "Moderate rain showers",82: "Violent rain showers",85: "Slight snow showers",86: "Heavy snow showers",95: "Thunderstorm",96: "Thunderstorm with slight hail",99: "Thunderstorm with heavy hail"}

    emoji_map = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",45: "🌫️",48: "🌫️",51: "🌦️",53: "🌧️",55: "🌧️",61: "🌦️",63: "🌧️",65: "🌧️",71: "🌨️",73: "🌨️",75: "❄️",80: "🌦️",81: "🌧️",82: "⛈️",85: "🌨️",86: "❄️",95: "⛈️",96: "⛈️",99: "⛈️"}

    def _print_open_meteo(lat, lon, display_name=None):
        try:
            meteo_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                "&current_weather=true&timezone=auto"
            )
            mr = requests.get(meteo_url, timeout=6.0)
            if mr.status_code != 200:
                return False
            data = mr.json()
            cw = data.get("current_weather") or {}
            temp_c = cw.get("temperature")
            wind_kmh = cw.get("windspeed")
            code = cw.get("weathercode")
            wdir = cw.get("winddirection")

            parts = []
            if display_name:
                parts.append(display_name.split(',')[0])

            if temp_c is not None:
                try:
                    tf = c_to_f(temp_c)
                    parts.append(f"{tf:.1f}°F ({float(temp_c):.1f}°C)")
                except Exception:
                    parts.append(str(temp_c))

            desc = ""
            try:
                if code is not None:
                    desc = wc_map.get(int(code), "")
            except Exception:
                desc = ""
            if desc:
                parts.append(desc)

            if wind_kmh is not None:
                try:
                    wf = kmh_to_mph(wind_kmh)
                    compass = _deg_to_compass(wdir)
                    if compass:
                        parts.append(f"wind {wf:.1f} mph {compass}")
                    else:
                        parts.append(f"wind {wf:.1f} mph")
                except Exception:
                    parts.append(str(wind_kmh))

            emoji = ""
            try:
                if code is not None:
                    emoji = emoji_map.get(int(code), "")
            except Exception:
                emoji = ""

            summary = ", ".join(parts)
            if emoji:
                print(f"[Raven] Weather for {display_name or 'location'}: {summary} — {emoji}")
            else:
                print(f"[Raven] Weather for {display_name or 'location'}: {summary}")
            return True
        except Exception:
            return False

    if not loc:
        try:
            ipinfo_url = "https://ipinfo.io/json"
            resp = requests.get(ipinfo_url, timeout=5.0)
            if resp.status_code == 200:
                ipj = resp.json()
                loc_city = ipj.get("city")
                loc_region = ipj.get("region")
                loc_country = ipj.get("country")
                loc_display = ", ".join([p for p in [loc_city, loc_region, loc_country] if p])
                loc_loc = ipj.get("loc")
                if loc_loc:
                    lat_s, lon_s = loc_loc.split(",")
                    try:
                        lat = float(lat_s)
                        lon = float(lon_s)
                    except Exception:
                        _print_wttr("")
                        return
                    display_name = loc_display or "your location"
                    if _print_open_meteo(lat, lon, display_name):
                        return
        except Exception:
            pass

        _print_wttr("")
        return

    try:
        nom_url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "RavenAssistant/1.0 (harveyporter8@outlook.com)"}
        params = {"q": loc, "format": "json", "limit": 1}
        r = requests.get(nom_url, params=params, headers=headers, timeout=6.0)
        if r.status_code == 200 and r.json():
            place = r.json()[0]
            lat = float(place.get("lat"))
            lon = float(place.get("lon"))
            display_name = place.get("display_name")
            if _print_open_meteo(lat, lon, display_name):
                return
            else:
                print(f"[Raven] Open-Meteo returned unexpected data, falling back to wttr.in")
                _print_wttr(loc)
                return
        else:
            _print_wttr(loc)
            return
    except Exception as exc:
        print(f"[Raven] Geocoding/Open-Meteo error: {exc}. Falling back to wttr.in")
        _print_wttr(loc)
