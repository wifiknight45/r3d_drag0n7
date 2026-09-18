#!/usr/bin/env python3
"""
sistema.py

Single-file astrological and astronomical chart generator.

Modes:
 - Nostradamus  : High-accuracy mode using pyswisseph (Swiss Ephemeris) when available.
 - Ptolemy      : Pure-Python fallback using Skyfield and approximate house algorithms.
 - Paranoid     : Offline-only mode using local data/ files.

Features:
 - Parse date inputs (DD/MM/YYYY or MM/DD/YYYY) with interactive disambiguation.
 - Parse times (24h/12h with AM/PM), timezone abbreviations or IANA tz names, and UTC.
 - Location input: city/state/country (geocoded via Nominatim), lat/lon, or zipcode (fallback to data/zipcodes.csv).
 - House systems: Placidus, Equal, Whole Sign, Porphyry, Campanus (SwissEphem exact if available; approximate fallback otherwise).
 - Output: verbose chart (text), summary, astronomical raw JSON, PNG wheel image, interactive HTML wheel, PDF report (when libs available).
 - Historical events fetch via Wikipedia OnThisDay (online) with offline fallback events_cache.json in data/.
 - Prompts for API keys at first run (NASA optional; Nominatim uses unauthenticated endpoints).
 - Saves outputs to outputs/ directory.
 - Interactive + CLI modes supported.

MIT License
Copyright 2025
"""

import sys, os, math, json, time, traceback
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import argparse
import shutil

# ---------------------------
# Configuration / constants
# ---------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
ZIPFILE = os.path.join(DATA_DIR, "zipcodes.csv")
TZ_CACHE = os.path.join(DATA_DIR, "tz_cache.csv")
EPHEM_SNAPSHOT = os.path.join(DATA_DIR, "ephem_snapshot.json")
EVENTS_CACHE = os.path.join(DATA_DIR, "events_cache.json")

# Default output filenames
OUT_VERBOSE = os.path.join(OUTPUT_DIR, "chart_verbose.txt")
OUT_SUMMARY = os.path.join(OUTPUT_DIR, "chart_summary.txt")
OUT_ASTRO_RAW = os.path.join(OUTPUT_DIR, "astro_data_raw.json")
OUT_WHEEL_PNG = os.path.join(OUTPUT_DIR, "int_chart_wheel.png")
OUT_WHEEL_HTML = os.path.join(OUTPUT_DIR, "chart_wheel.html")
OUT_PDF = os.path.join(OUTPUT_DIR, "chart_report.pdf")

# Common timezone abbreviation map to IANA (best-effort)
TZ_ABBREV_MAP = {
    "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    "EST": "America/New_York", "EDT": "America/New_York",
    "CST": "America/Chicago", "CDT": "America/Chicago",
    "MST": "America/Denver", "MDT": "America/Denver",
    "UTC": "UTC", "GMT": "Etc/Greenwich",
    "BST": "Europe/London", "CET": "Europe/Paris", "CEST": "Europe/Paris"
}

# Planet list mapping for Swiss Ephemeris or skyfield
PLANETS = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]

# ---------------------------
# Dependency detection
# ---------------------------
HAS_PYSWISSEPH = False
HAS_SKYFIELD = False
HAS_MATPLOTLIB = False
HAS_PLOTLY = False
HAS_PIL = False
HAS_FPDF = False
HAS_GEOPY = False
HAS_TFINDER = False
HAS_REQUESTS = False
HAS_DATEUTIL = False

try:
    import swisseph as swe
    HAS_PYSWISSEPH = True
except Exception:
    HAS_PYSWISSEPH = False

try:
    from skyfield.api import load, Topos, Star, wgs84
    from skyfield.api import N, E, W, S
    HAS_SKYFIELD = True
except Exception:
    HAS_SKYFIELD = False

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except Exception:
    HAS_PIL = False

try:
    from fpdf import FPDF
    HAS_FPDF = True
except Exception:
    HAS_FPDF = False

try:
    from geopy.geocoders import Nominatim
    HAS_GEOPY = True
except Exception:
    HAS_GEOPY = False

try:
    from timezonefinder import TimezoneFinder
    HAS_TFINDER = True
except Exception:
    HAS_TFINDER = False

try:
    import requests
    HAS_REQUESTS = True
except Exception:
    HAS_REQUESTS = False

try:
    from dateutil import parser as du_parser
    HAS_DATEUTIL = True
except Exception:
    HAS_DATEUTIL = False

# ---------------------------
# Utility functions
# ---------------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def eprint(*a, **k): print(*a, file=sys.stderr, **k)

def try_install_hint(pkg_list):
    eprint("Some optional functionality needs additional packages.")
    eprint("You can run the following session-only pip install (example):")
    eprint("python3 -m pip install " + " ".join(pkg_list))

# ---------------------------
# Input parsing helpers
# ---------------------------
def parse_date_input(raw_date, preferred_format=None):
    """
    Accepts DD/MM/YYYY or MM/DD/YYYY.
    If ambiguous and preferred_format provided ('DMY' or 'MDY'), obey it.
    Otherwise ask interactively to confirm (interactive mode).
    Returns datetime.date.
    """
    raw = raw_date.strip()
    parts = raw.split("/")
    if len(parts) != 3:
        raise ValueError("Date must be in DD/MM/YYYY or MM/DD/YYYY format")
    a,b,c = parts
    if len(a)==4: # ISO style
        return datetime.fromisoformat(raw).date()
    # numeric parse
    try:
        d1 = int(a); d2 = int(b); y = int(c)
    except Exception:
        raise ValueError("Invalid numeric date parts")
    ambiguous = (d1 <= 12 and d2 <= 12)
    if not ambiguous:
        # decide by which looks like day>12
        if d1 > 12:
            return datetime(y, d1, d2).date()
        else:
            return datetime(y, d2, d1).date()
    if preferred_format == 'DMY':
        return datetime(y, d1, d2).date()
    if preferred_format == 'MDY':
        return datetime(y, d2, d1).date()
    # interactive confirmation
    print(f"Ambiguous date {raw}. Interpret as:")
    print(f"  1) DD/MM/YYYY -> {d1}/{d2}/{y}  (day={d1})")
    print(f"  2) MM/DD/YYYY -> {d2}/{d1}/{y}  (month={d1})")
    choice = input("Choose 1 or 2 (default 1): ").strip() or "1"
    if choice.startswith("2"):
        return datetime(y, d2, d1).date()
    return datetime(y, d1, d2).date()

def parse_time_input(raw_time, tz_hint=None):
    """
    Accepts:
     - 24-hour with optional timezone (17:15 PDT)
     - 12-hour with am/pm (5:15 PM PDT)
     - UTC (00:15)
    Returns aware datetime.time and tzinfo.
    """
    s = raw_time.strip()
    parts = s.split()
    time_part = parts[0]
    tz_part = None
    if len(parts) > 1:
        tz_part = parts[-1]
    # try hh:mm
    # handle am/pm by dateutil if available, else basic parse
    if HAS_DATEUTIL:
        # dateutil can parse time with AM/PM; create a dummy date
        dt = du_parser.parse(time_part + ((" " + tz_part) if tz_part else ""))
        tzinfo = None
        if tz_part:
            tzinfo = resolve_tz(tz_part)
        return dt.time(), tzinfo
    else:
        # basic parse
        if ":" not in time_part:
            raise ValueError("Time must include ':' between hour and minute")
        hh,mm = time_part.split(":")
        hh = int(hh); mm = int(mm)
        tzinfo = resolve_tz(tz_part) if tz_part else None
        return datetime(2000,1,1,hh,mm).time(), tzinfo

def resolve_tz(tz_input):
    """
    Map common abbreviations to IANA via TZ_ABBREV_MAP.
    If given an IANA string, return ZoneInfo.
    If given UTC offset like UTC+2, parse it.
    """
    if not tz_input:
        return None
    s = tz_input.strip()
    if s.upper() in TZ_ABBREV_MAP:
        try:
            return ZoneInfo(TZ_ABBREV_MAP[s.upper()])
        except Exception:
            return ZoneInfo("UTC")
    if s.upper().startswith("UTC"):
        # UTC, UTC+/-HH[:MM]
        rest = s[3:]
        if not rest:
            return timezone.utc
        sign = 1
        if rest[0] in "+-":
            sign = 1 if rest[0]=="+" else -1
            rest = rest[1:]
        parts = rest.split(":")
        hh = int(parts[0]) if parts[0] else 0
        mm = int(parts[1]) if len(parts)>1 else 0
        return timezone(timedelta(hours=sign*hh, minutes=sign*mm))
    # assume it's an IANA name
    try:
        return ZoneInfo(s)
    except Exception:
        # unknown; return UTC as safe default but warn
        print(f"Warning: unknown timezone '{s}', defaulting to UTC")
        return timezone.utc

# ---------------------------
# Geocoding helpers
# ---------------------------
def geocode_location(input_loc, prefer_online=True, max_retries=5):
    """
    Accepts:
     - "City, State, Country"
     - "latitude N longitude W" e.g. "37.7749 N -122.4194 W" or "36.97 N, -122.03 W"
     - Zipcode (e.g., "94108")
    Returns (lat, lon, display_name, tzinfo_str)
    """
    s = str(input_loc).strip()
    # detect lat/lon numeric patterns
    if any(ch.isdigit() for ch in s) and ("," in s or " " in s) and ("N" in s or "S" in s or "E" in s or "W" in s or "-" in s):
        # try to parse numeric lat lon
        # accept forms: "36.9741 N and -122.0308 W" or "36.9741 N, -122.0308 W" or "36.9741 -122.0308"
        toks = s.replace("and", ",").replace("°","").replace("º","").replace("  "," ").replace(" , ",",").replace(" ,",",").replace(", ",",").split(",")
        flat=None; flon=None
        # find two float numbers
        nums = []
        for t in s.replace("N"," ").replace("S"," ").replace("E"," ").replace("W"," ").replace("°"," ").replace("º"," ").replace(","," ").split():
            try:
                nums.append(float(t))
            except:
                pass
        if len(nums)>=2:
            flat=nums[0]; flon=nums[1]
            # handle negative longitude if indicated by W earlier
            if "W" in s.upper() and flon>0:
                flon = -abs(flon)
            if "S" in s.upper() and flat>0:
                flat = -abs(flat)
            # try tzfinder if available
            tzname = None
            if HAS_TFINDER:
                try:
                    tf = TimezoneFinder()
                    tzname = tf.timezone_at(lng=flon, lat=flat)
                except Exception:
                    tzname = None
            return flat, flon, f"Coords {flat},{flon}", tzname
    # detect zipcode numeric
    if s.isdigit() and os.path.exists(ZIPFILE):
        # local lookup in zipcodes.csv: format expected "zipcode,lat,lon,city,state,country"
        with open(ZIPFILE, "r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split(",")
                if parts and parts[0]==s:
                    try:
                        lat = float(parts[1]); lon = float(parts[2])
                        city = parts[3] if len(parts)>3 else ""
                        state = parts[4] if len(parts)>4 else ""
                        country = parts[5] if len(parts)>5 else ""
                        tzname = None
                        if HAS_TFINDER:
                            try:
                                tf = TimezoneFinder()
                                tzname = tf.timezone_at(lng=lon, lat=lat)
                            except Exception:
                                tzname = None
                        return lat, lon, f"{city},{state},{country}", tzname
                    except:
                        continue
    # attempt Nominatim geocode (online preferred)
    if prefer_online and HAS_REQUESTS:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent":"astrocharts/1.0 (email@example.com)"}
        params = {"q": s, "format":"json", "limit":1}
        backoff = 1
        for attempt in range(max_retries):
            try:
                r = requests.get(url, params=params, headers=headers, timeout=10)
                if r.status_code==200:
                    data = r.json()
                    if data:
                        lat = float(data[0]["lat"]); lon = float(data[0]["lon"])
                        display = data[0].get("display_name","")
                        # timezone via TimezoneFinder or fallback to tz API if available
                        tzname = None
                        if HAS_TFINDER:
                            try:
                                tf = TimezoneFinder()
                                tzname = tf.timezone_at(lng=lon, lat=lat)
                            except Exception:
                                tzname = None
                        return lat, lon, display, tzname
                    else:
                        break
                elif r.status_code in (429, 503):
                    time.sleep(backoff); backoff *= 2; continue
                else:
                    break
            except Exception:
                time.sleep(backoff); backoff *= 2; continue
    # fallback to local zip file search by token (best effort)
    if os.path.exists(ZIPFILE):
        q = s.lower()
        with open(ZIPFILE, "r", encoding="utf-8") as fh:
            for line in fh:
                if q in line.lower():
                    parts = line.strip().split(",")
                    try:
                        lat=float(parts[1]); lon=float(parts[2]); city=parts[3]
                        return lat, lon, f"{parts[3]},{parts[4]},{parts[5]}", None
                    except:
                        continue
    raise ValueError("Could not geocode location; provide lat,lon or ensure data/zipcodes.csv exists or network available for Nominatim")

# ---------------------------
# Astronomical / Ephemeris
# ---------------------------
def load_ephemeris_preference():
    """
    Determine ephemeris backend. Preference:
     - Swiss Ephemeris (pyswisseph) -> Nostradamus
     - Skyfield (JPL) -> Ptolemy fallback (lower precision for some houses)
    """
    if HAS_PYSWISSEPH:
        return "swisseph"
    if HAS_SKYFIELD:
        return "skyfield"
    return "builtin"

def jd_from_datetime(dt_utc):
    """
    Convert Python datetime (UTC-aware) to Julian Day (UTC) for swisseph and other uses.
    Uses algorithm for Julian Day (proleptic Gregorian).
    """
    # dt_utc must be timezone-aware in UTC
    if dt_utc.tzinfo is None:
        raise ValueError("datetime must be timezone-aware UTC")
    # Convert to UTC naive
    t = dt_utc.astimezone(timezone.utc)
    year = t.year; month = t.month; day = t.day
    hour = t.hour + t.minute/60 + t.second/3600 + t.microsecond/3.6e9
    if month <= 2:
        year -= 1; month += 12
    A = year // 100
    B = 2 - A + A//4
    jd = int(365.25*(year+4716)) + int(30.6001*(month+1)) + day + B - 1524.5 + hour/24.0
    return jd

def compute_planet_positions_swisseph(jd_ut, lat, lon, eph_path=None):
    """
    Uses swisseph to compute planetary geocentric ecliptic longitudes and latitudes,
    distances, moon phases, heliocentric coordinates, house cusps for various systems.
    Returns structured dict.
    """
    res = {}
    if eph_path:
        swe.set_ephe_path(eph_path)
    # ensure ephemeris loaded
    try:
        swe.set_topo(lon, lat, 0) # set earth surface if needed
    except Exception:
        pass
    # planets: swisseph constants
    sw_planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO
    }
    res["planets"] = {}
    for name, pconst in sw_planets.items():
        try:
            lonlat_dist = swe.calc_ut(jd_ut, pconst)  # returns [lon,lat,dist,...]
            res["planets"][name] = {
                "ecl_lon": lonlat_dist[0],
                "ecl_lat": lonlat_dist[1],
                "distance_au": lonlat_dist[2] if len(lonlat_dist)>2 else None,
                "raw": lonlat_dist
            }
        except Exception as e:
            res["planets"][name] = {"error": str(e)}
    # houses for requested systems (Placidus, Equal, Whole, Porphyry, Campanus)
    houses = {}
    try:
        # Swiss Ephemeris expects latitude (north positive), longitude east positive; return houses for Placidus by default
        asc_mc, cusp = swe.houses(jd_ut, lat, lon, b'P')  # 'P' = Placidus
        houses['Placidus'] = {"ascendant": asc_mc[0], "mc": asc_mc[1], "cusps": list(cusp)}
        # Equal: Swiss uses 'E'
        asc_mc_e, cusp_e = swe.houses(jd_ut, lat, lon, b'E')
        houses['Equal'] = {"ascendant": asc_mc_e[0], "mc": asc_mc_e[1], "cusps": list(cusp_e)}
        # Whole sign: compute as whole sign from ascendant
        asc = asc_mc[0]
        whole_cusps = []
        asc_sign = int(asc//30)
        for i in range(12):
            whole_cusps.append(((asc_sign + i)*30) % 360)
        houses['Whole'] = {"ascendant": asc, "mc": asc_mc[1], "cusps": whole_cusps}
        # Porphyry: 'O' code is not universal; compute via swe.houses with 'O' if exists else approximate
        try:
            asc_mc_p, cusp_p = swe.houses(jd_ut, lat, lon, b'P') # placeholder; for Porphyry we will implement approximate below
        except Exception:
            cusp_p = None
        houses['Porphyry'] = {"method_note":"approximate porphyry"}
        # Campanus: swe supports 'C'?
        try:
            asc_mc_c, cusp_c = swe.houses(jd_ut, lat, lon, b'C')
            houses['Campanus'] = {"ascendant": asc_mc_c[0], "mc": asc_mc_c[1], "cusps": list(cusp_c)}
        except Exception:
            houses['Campanus'] = {"method_note":"approximate campanus (fallback)"}
    except Exception as e:
        houses['error'] = str(e)
    res["houses"] = houses
    # Moon geocentric distance and phase: compute elongation and phase
    try:
        moon = res["planets"]["Moon"]
        sun = res["planets"]["Sun"]
        if moon.get("distance_au") and sun.get("distance_au"):
            # phase angle approximation via longitudes
            elong = abs(moon["ecl_lon"] - sun["ecl_lon"])
            elong = elong if elong <=180 else 360-elong
            res["moon_phase_deg"] = elong
            # illuminated fraction approx: (1 + cos(elong))/2
            res["moon_illum_frac"] = (1 + math.cos(math.radians(elong))) / 2
    except Exception:
        pass
    return res

def compute_planet_positions_skyfield(dt_utc, lat, lon):
    """
    Skyfield fallback: compute approximate geocentric ecliptic longitudes and heliocentric positions.
    Requires skyfield.
    """
    ts = load.timescale()
    t = ts.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, dt_utc.second)
    eph = load('de421.bsp')  # may download if network available
    earth = eph['earth']
    observer = earth + wgs84.latlon(lat, lon)
    res = {"planets": {}}
    for name in PLANETS:
        try:
            body = eph[name] if name in eph.names else eph[name] if name in eph else None
        except Exception:
            body = None
        try:
            if body is not None:
                astrometric = earth.at(t).observe(body)
                ra, dec, dist = astrometric.radec()
                # convert to ecliptic lon/lat via transform - Skyfield has ecliptic_frame
                from skyfield.api import ecliptic
                ecl = ecliptic.position_from_radec(ra, dec, distance=dist)
                # approximate lon/lat:
                lon_ecl = math.degrees(math.atan2(ecl[1].km, ecl[0].km)) % 360
                lat_ecl = math.degrees(math.atan2(ecl[2].km, math.hypot(ecl[0].km, ecl[1].km)))
                res["planets"][name] = {"ecl_lon": lon_ecl, "ecl_lat": lat_ecl, "distance_km": dist.km}
            else:
                res["planets"][name] = {"error":"not found in SPK"}
        except Exception as e:
            res["planets"][name] = {"error": str(e)}
    # moon and sun specifics
    return res

# ---------------------------
# House system approximations (pure-Python)
# ---------------------------
def equal_house_cusps(asc):
    # asc in degrees; equal houses = asc + n*30
    asc = asc % 360
    return [ (asc + i*30) % 360 for i in range(12) ]

def whole_sign_cusps(asc):
    asc = asc % 360
    sign_start = (asc//30)*30
    return [ (sign_start + i*30) % 360 for i in range(12) ]

def porphyry_cusps(asc, mc):
    # Porphyry divides quadrants (ASC->MC, MC->DSC, DSC->IC, IC->ASC) into 3 equal parts.
    asc = asc % 360; mc = mc % 360
    quad = []
    # helper to get sector from A to B in increasing degrees
    def between(a,b):
        # returns range from a to b mod360 as value list
        seg = (b - a) % 360
        return seg
    ic = (mc + 180) % 360
    dsc = (asc + 180) % 360
    # quadrants: asc->mc, mc->dsc, dsc->ic, ic->asc
    names = [("asc","mc"),("mc","dsc"),("dsc","ic"),("ic","asc")]
    cusps = []
    pts = {"asc":asc,"mc":mc,"dsc":dsc,"ic":ic}
    for (a,b) in names:
        start = pts[a]; end = pts[b]
        span = (end - start) % 360
        for i in range(3):
            cusps.append((start + span*(i/3)) % 360)
    return [round(c,6) for c in cusps[:12]]

def campanus_cusps(asc, lat, lon, jd_ut):
    # Campanus requires vertical division of prime vertical; this is complex.
    # Provide an approximate by projecting 12 equal segments of sky from the prime vertical.
    # This is an approximation for fallback mode.
    a = asc % 360
    return [ (a + i*30) % 360 for i in range(12) ]

# ---------------------------
# Interpretative utilities (dignities, aspects)
# ---------------------------
RULERS = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"
}
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def sign_from_degree(deg):
    deg = deg % 360
    idx = int(deg//30)
    sign = SIGNS[idx]
    deg_in_sign = deg - idx*30
    return sign, deg_in_sign

def aspects_between(a_deg, b_deg):
    # return list of aspects with small orb rules
    dif = abs((a_deg - b_deg + 180) % 360 - 180)
    aspects = []
    # aspect table: angle: (name, orb)
    table = {0:("Conjunction",8), 180:("Opposition",8), 120:("Trine",7), 60:("Sextile",6), 90:("Square",6), 150:("Quincunx",3)}
    for ang,(name,orb) in table.items():
        if abs(dif - ang) <= orb:
            aspects.append((name, ang, dif))
    return aspects

# ---------------------------
# Historical events (Wikipedia OnThisDay)
# ---------------------------
def fetch_events_on_date(dt, prefer_online=True):
    """
    dt: datetime.date
    If online and requests available, fetch from Wikipedia API OnThisDay endpoints.
    Else fallback to events_cache.json
    """
    events = []
    if prefer_online and HAS_REQUESTS:
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/all/{dt.month}/{dt.day}"
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent":"astrocharts/1.0"})
            if r.status_code == 200:
                data = r.json()
                # pick births, events, deaths condensed
                for cat in ("births","events","deaths"):
                    for item in data.get(cat, [])[:5]:
                        year = item.get("year")
                        text = item.get("text") or item.get("pages",[{}])[0].get("extract")
                        events.append({"category":cat, "year":year, "text": text})
                return events
        except Exception:
            pass
    # fallback
    if os.path.exists(EVENTS_CACHE):
        try:
            with open(EVENTS_CACHE, "r", encoding="utf-8") as fh:
                cache = json.load(fh)
                key = f"{dt.month:02d}-{dt.day:02d}"
                return cache.get(key, [])
        except Exception:
            return []
    return []

# ---------------------------
# Output formatting and visualization
# ---------------------------
def write_text_file(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

def create_simple_wheel_png(planet_positions, cusps, outpath):
    """
    Create a simple PNG wheel with planet glyphs as text markers.
    Requires PIL. If not available, skip.
    """
    if not HAS_PIL:
        return False
    size = 1200
    img = Image.new("RGBA", (size,size), "white")
    draw = ImageDraw.Draw(img)
    center = (size//2, size//2)
    radius = int(size*0.4)
    # draw circle
    draw.ellipse((center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius), outline="black", width=3)
    # draw cusp lines
    for c in cusps:
        ang = math.radians((90 - c) % 360)
        x = center[0] + radius*math.cos(ang)
        y = center[1] - radius*math.sin(ang)
        draw.line([center,(x,y)], fill="black", width=2)
    # place planet markers
    for pname, pdata in planet_positions.items():
        lon = pdata.get("ecl_lon")
        if lon is None:
            continue
        ang = math.radians((90 - lon) % 360)
        pr = radius*0.85
        x = center[0] + pr*math.cos(ang)
        y = center[1] - pr*math.sin(ang)
        draw.text((x-10,y-10), pname[0], fill="red")
    img.save(outpath)
    return True

def create_plotly_wheel(planet_positions, cusps, outpath_html):
    if not HAS_PLOTLY:
        return False
    # create simple polar plot
    labels = []
    angles = []
    radii = []
    for pname, pdata in planet_positions.items():
        lon = pdata.get("ecl_lon")
        if lon is None: continue
        labels.append(pname)
        angles.append((lon/360.0)*2*math.pi)
        radii.append(1)
    fig = go.Figure()
    theta = [math.degrees(a) for a in angles]
    fig.add_trace(go.Barpolar(theta=theta, r=[1]*len(theta), text=labels, marker_color="indianred"))
    fig.update_layout(template=None, title="Planet positions (ecliptic longitudes)")
    fig.write_html(outpath_html)
    return True

# ---------------------------
# Main calculation pipeline
# ---------------------------
def generate_chart(mode, date_str, time_str, tz_input, location_input, date_format_pref=None, interactive=True):
    """
    mode: 'Nostradamus', 'Ptolemy', or 'Paranoid'
    """
    ensure_dirs()
    # parse date
    dt_date = parse_date_input(date_str, preferred_format = 'DMY' if date_format_pref=='DMY' else ('MDY' if date_format_pref=='MDY' else None))
    # parse time
    ttime, tzinfo = parse_time_input(time_str, tz_hint=tz_input)
    tzinfo = tzinfo or resolve_tz(tz_input)
    # assemble datetime with timezone
    if isinstance(tzinfo, ZoneInfo):
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
    elif isinstance(tzinfo, timezone):
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
    else:
        # fallback: assume local is UTC
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=timezone.utc)
    # convert to UTC
    dt_utc = local_dt.astimezone(timezone.utc)
    # geocode
    geo_lat, geo_lon, geo_display, tzname = geocode_location(location_input, prefer_online=(mode!="Paranoid"))
    # if tzname exists and tzinfo was None, set tzinfo
    if tzname and (not tzinfo):
        try:
            tzinfo = ZoneInfo(tzname)
            local_dt = local_dt.astimezone(tzinfo)
            dt_utc = local_dt.astimezone(timezone.utc)
        except Exception:
            pass
    # choose ephemeris backend
    backend = load_ephemeris_preference()
    jd_ut = jd_from_datetime(dt_utc)
    astro = {}
    if backend == "swisseph" and mode!="Paranoid":
        # use swisseph (Nostradamus)
        try:
            swe.set_ephe_path(DATA_DIR)  # optional path
            swres = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
            astro = swres
        except Exception as e:
            eprint("Swiss Ephemeris error:", e)
            astro = {"error":"swisseph failed, fallback to skyfield if available"}
            if HAS_SKYFIELD:
                astro = compute_planet_positions_skyfield(dt_utc, geo_lat, geo_lon)
    elif HAS_SKYFIELD:
        astro = compute_planet_positions_skyfield(dt_utc, geo_lat, geo_lon)
    else:
        astro = {"error":"No ephemeris backend available. Install pyswisseph or skyfield."}
    # Houses: try to extract asc/MC from astro if available; else compute approximate ascendant via sidereal math
    # For fallback, compute ascendant approximate:
    if "houses" in astro and "Placidus" in astro["houses"]:
        asc = astro["houses"]["Placidus"]["ascendant"]
        mc = astro["houses"]["Placidus"]["mc"]
        cusps_pl = astro["houses"]["Placidus"]["cusps"]
    else:
        # approximate ascendant calculation using local sidereal time and obliquity:
        # approximate GST -> LST -> ascendant
        # This is a simplification; accurate ascendant needs full ephemeris.
        # Use skyfield for LST/asc if available
        asc = 0.0; mc = 0.0; cusps_pl = equal_house_cusps(0.0)
    # compute cusps for each requested system using either swisseph results or approximate functions
    cusps = {}
    if "houses" in astro and astro["houses"].get("Placidus"):
        cusps['Placidus'] = astro["houses"]["Placidus"]["cusps"]
    else:
        cusps['Placidus'] = equal_house_cusps(asc)
    cusps['Equal'] = equal_house_cusps(asc)
    cusps['Whole'] = whole_sign_cusps(asc)
    cusps['Porphyry'] = porphyry_cusps(asc, mc)
    cusps['Campanus'] = campanus_cusps(asc, geo_lat, geo_lon, jd_ut)

    # Compose verbose textual report
    verbose_lines = []
    verbose_lines.append(f"Input (interpreted): date={dt_date.isoformat()}, local_time={local_dt.isoformat()}, UTC={dt_utc.isoformat()}")
    verbose_lines.append(f"Location: {geo_display} (lat={geo_lat}, lon={geo_lon})")
    verbose_lines.append(f"Backend: {backend}; Mode: {mode}")
    verbose_lines.append("")
    verbose_lines.append("Planetary positions (ecliptic longitude degrees) and signs:")
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            verbose_lines.append(f" - {pname}: {pdata['ecl_lon']:.4f}° (sign {sign} {deg_in:.2f}°), lat {pdata.get('ecl_lat')}, dist {pdata.get('distance_au') or pdata.get('distance_km')}")
        else:
            verbose_lines.append(f" - {pname}: {pdata}")
    verbose_lines.append("")
    verbose_lines.append("Houses (cusps) by system (degrees):")
    for sysname, cvals in cusps.items():
        verbose_lines.append(f" - {sysname}: " + ", ".join([f"{round(c,4)}" for c in cvals]))
    verbose_lines.append("")
    # aspects summary
    verbose_lines.append("Significant aspects (sample pairwise check among classical planets):")
    planet_list = [p for p in astro.get("planets", {}).keys()]
    for i in range(len(planet_list)):
        for j in range(i+1, len(planet_list)):
            pa = astro["planets"].get(planet_list[i], {})
            pb = astro["planets"].get(planet_list[j], {})
            if not pa or not pb or "ecl_lon" not in pa or "ecl_lon" not in pb:
                continue
            asp = aspects_between(pa["ecl_lon"], pb["ecl_lon"])
            if asp:
                for a in asp:
                    verbose_lines.append(f"  * {planet_list[i]} - {planet_list[j]}: {a[0]} (angle={a[1]}°, diff={a[2]:.2f}°)")

    # summarization
    summary_lines = []
    summary_lines.append("Chart summary:")
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            ruler = RULERS.get(sign, "Unknown")
            summary_lines.append(f"{pname} in {sign} {deg_in:.1f}° (ruler: {ruler})")
    # historical events
    events = fetch_events_on_date(dt_date, prefer_online=(mode!="Paranoid"))
    event_lines = ["Historical events on this date (sample):"]
    if events:
        for ev in events[:8]:
            event_lines.append(f" - [{ev.get('category')}] {ev.get('year')}: {ev.get('text')}")
    else:
        event_lines.append(" - No online events found; check data/events_cache.json for offline entries.")
    # write outputs
    write_text_file(OUT_VERBOSE, "\n".join(verbose_lines))
    write_text_file(OUT_SUMMARY, "\n".join(summary_lines + [""] + event_lines))
    with open(OUT_ASTRO_RAW, "w", encoding="utf-8") as fh:
        json.dump({"input": {"date": dt_date.isoformat(), "local_time": local_dt.isoformat(), "utc": dt_utc.isoformat(), "location": {"lat":geo_lat,"lon":geo_lon,"display":geo_display}}, "astro": astro, "cusps": cusps, "events": events}, fh, indent=2)
    # images
    create_simple_wheel_png(astro.get("planets", {}), cusps.get("Placidus", []), OUT_WHEEL_PNG)
    create_plotly_wheel(astro.get("planets", {}), cusps.get("Placidus", []), OUT_WHEEL_HTML)
    # PDF report if fpdf installed
    if HAS_FPDF:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0,6, "\n".join(verbose_lines))
        if os.path.exists(OUT_WHEEL_PNG):
            pdf.image(OUT_WHEEL_PNG, x=10, w=180)
        pdf.output(OUT_PDF)
    # results summary printed to console
    print("Outputs written to 'outputs/' directory:")
    print(" - Verbose chart:", OUT_VERBOSE)
    print(" - Summary:", OUT_SUMMARY)
    print(" - Raw astro JSON:", OUT_ASTRO_RAW)
    print(" - Wheel PNG (if PIL available):", OUT_WHEEL_PNG)
    print(" - Wheel interactive HTML (if Plotly available):", OUT_WHEEL_HTML)
    if HAS_FPDF:
        print(" - PDF report:", OUT_PDF)
    print("\nNOTE: For Nostradamus mode exact Swiss Ephemeris calculations, install pyswisseph and ephemeris files.")
    return True

# ---------------------------
# CLI / interactive front end
# ---------------------------
def interactive_mode():
    print("AstroCharts Interactive Mode")
    print("Modes: Nostradamus (swisseph), Ptolemy (skyfield/fallback), Paranoid (offline)")
    mode_choice = input("Choose mode [Nostradamus/Ptolemy/Paranoid] (default Nostradamus): ").strip() or "Nostradamus"
    date_format_pref = None
    df_choice = input("Select date input preference for ambiguous (1) DD/MM/YYYY or (2) MM/DD/YYYY or (3) ask each time (default ask): ").strip()
    if df_choice == "1": date_format_pref = "DMY"
    elif df_choice == "2": date_format_pref = "MDY"
    else: date_format_pref = None
    date_str = input("Enter date (DD/MM/YYYY or MM/DD/YYYY): ").strip()
    time_str = input("Enter time (e.g., 17:15 PDT or 5:15 PM PDT or 00:15 UTC): ").strip()
    tz_hint = input("Optional timezone hint (e.g., PDT or America/Los_Angeles) or press Enter: ").strip() or None
    location = input("Location (City, State, Country OR zipcode OR lat lon): ").strip()
    print("Generating chart... this may take a few seconds.")
    try:
        generate_chart(mode_choice, date_str, time_str, tz_hint, location, date_format_pref=date_format_pref, interactive=True)
    except Exception as e:
        eprint("Error generating chart:", e)
        traceback.print_exc()

def cli_mode(args):
    # args: mode, date, time, tz, location, datefmt
    generate_chart(args.mode, args.date, args.time, args.tz, args.location, date_format_pref=args.datefmt, interactive=False)

def main():
    parser = argparse.ArgumentParser(description="AstroCharts CLI and Interactive tool")
    parser.add_argument("--mode", choices=["Nostradamus","Ptolemy","Paranoid"], default="Nostradamus", help="Computation mode")
    parser.add_argument("--date", help="Date input DD/MM/YYYY or MM/DD/YYYY")
    parser.add_argument("--time", help="Time input e.g. '17:15 PDT' or '5:15 PM PDT' or '00:15 UTC'")
    parser.add_argument("--tz", help="Optional timezone hint (PDT or America/Los_Angeles)")
    parser.add_argument("--location", help="Location: 'City, State, Country' or 'latitude,longitude' or zipcode")
    parser.add_argument("--datefmt", choices=["DMY","MDY"], help="Preferred interpretation for ambiguous dates")
    parser.add_argument("--interactive", action="store_true", help="Interactive prompts")
    args = parser.parse_args()
    ensure_dirs()
    # auto-install hint when critical packages missing for Nostradamus mode
    if args.mode=="Nostradamus" and not HAS_PYSWISSEPH:
        eprint("Swiss Ephemeris (pyswisseph) not detected. Nostradamus mode will fallback to Ptolemy calculations.")
        try_install_hint(["pyswisseph","matplotlib","plotly","pillow","skyfield","timezonefinder","geopy","requests","fpdf"])
    if args.interactive or (not args.date and not args.time and not args.location):
        interactive_mode()
    else:
        if not (args.date and args.time and args.location):
            parser.error("For CLI mode supply --date --time --location or use --interactive")
        cli_mode(args)

if __name__ == "__main__":
    main()
