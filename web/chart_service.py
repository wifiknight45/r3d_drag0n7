"""
Chart computation service — prefers the canonical r3d_dragon package.
Falls back to archived single-file modules only if the package is unavailable.
"""
from __future__ import annotations

import csv
import importlib
import math
import os
import sys
import traceback
from datetime import date, datetime, time as dtime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "data"
US_ZIP_CSV = DATA_DIR / "US_zipcodes.csv"

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

# Approximate mean orbital elements for builtin fallback (degrees / day rates at J2000-ish)
# lon0 at JD 2451545.0, daily motion — good enough for UI demos when no ephemeris installed
_MEAN_ELEMENTS = {
    "Sun": (280.460, 0.9856474),
    "Moon": (218.316, 13.176396),
    "Mercury": (252.250, 4.092317),
    "Venus": (181.979, 1.602136),
    "Mars": (355.433, 0.524033),
    "Jupiter": (34.351, 0.083085),
    "Saturn": (50.077, 0.033444),
    "Uranus": (314.055, 0.011725),
    "Neptune": (304.348, 0.005995),
    "Pluto": (238.929, 0.003975),
}

_sistema = None
_sistema_name: Optional[str] = None
_sistema_error: Optional[str] = None


def _try_load_sistema():
    global _sistema, _sistema_name, _sistema_error
    if _sistema is not None or _sistema_error is not None:
        return _sistema
    # Prefer package, then thin sistema wrapper, then archived legacy modules.
    candidates = (
        "r3d_dragon",
        "sistema",
        "archive.sistema_enhanced",
        "archive.sistema_completa",
    )
    errors = []
    for mod_name in candidates:
        try:
            _sistema = importlib.import_module(mod_name)
            _sistema_name = mod_name
            _sistema_error = None
            return _sistema
        except Exception as exc:
            errors.append(f"{mod_name}: {exc}")
            continue
    _sistema_error = "; ".join(errors) if errors else "no module"
    return None


def sistema_status() -> Dict[str, Any]:
    mod = _try_load_sistema()
    info: Dict[str, Any] = {
        "module": _sistema_name,
        "loaded": mod is not None,
        "error": _sistema_error if mod is None else None,
    }
    if mod is not None:
        has_swe = getattr(mod, "HAS_PYSWISSEPH", None)
        has_sf = getattr(mod, "HAS_SKYFIELD", None)
        if has_swe is None and _sistema_name == "r3d_dragon":
            try:
                from r3d_dragon import deps as _deps
                has_swe = _deps.HAS_PYSWISSEPH
                has_sf = _deps.HAS_SKYFIELD
            except Exception:
                has_swe, has_sf = False, False
        info["has_swisseph"] = bool(has_swe)
        info["has_skyfield"] = bool(has_sf)
        info["version"] = getattr(mod, "__version__", None)
    return info


def sign_from_degree(deg: float) -> Tuple[str, float]:
    d = deg % 360.0
    idx = int(d // 30)
    return SIGNS[idx], d % 30.0


def jd_from_datetime(dt_utc: datetime) -> float:
    """Julian Day (UT) from aware UTC datetime."""
    y, m, d = dt_utc.year, dt_utc.month, dt_utc.day
    hh = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + B - 1524.5
    return jd + hh / 24.0


def normalize_date(raw: str) -> str:
    """Accept ISO YYYY-MM-DD or slash dates; return slash form for sistema or ISO parseable."""
    s = raw.strip()
    if "-" in s and "/" not in s:
        parts = s.split("-")
        if len(parts) == 3 and len(parts[0]) == 4:
            # Prefer MDY-style for US forms: MM/DD/YYYY; sistema also accepts ISO if parts[0] len 4 with /
            return f"{parts[0]}/{parts[1]}/{parts[2]}"  # YYYY/MM/DD → sistema ISO branch uses /
    return s


def parse_date_local(raw: str, preferred: Optional[str] = "MDY") -> date:
    s = raw.strip()
    if "-" in s and len(s.split("-")[0]) == 4:
        return datetime.fromisoformat(s[:10]).date()
    if "/" in s:
        parts = s.split("/")
        if len(parts) == 3 and len(parts[0]) == 4:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
        ambiguous = a <= 12 and b <= 12
        if not ambiguous:
            if a > 12:
                return date(c, b, a)  # DD/MM
            return date(c, a, b)  # MM/DD
        if preferred == "DMY":
            return date(c, b, a)
        return date(c, a, b)  # MDY default for web forms
    raise ValueError(f"Unrecognized date: {raw}")


def parse_time_local(raw: str) -> dtime:
    s = raw.strip()
    # strip am/pm
    upper = s.upper()
    ampm = None
    for tag in ("AM", "PM"):
        if tag in upper:
            ampm = tag
            s = upper.replace(tag, "").strip()
            break
    # drop trailing tz tokens
    tokens = s.split()
    time_part = tokens[0]
    hh_s, mm_s = time_part.split(":")[:2]
    hh, mm = int(hh_s), int(mm_s)
    if ampm == "PM" and hh < 12:
        hh += 12
    if ampm == "AM" and hh == 12:
        hh = 0
    return dtime(hh, mm)


def resolve_timezone(tz_input: Optional[str], lat: Optional[float] = None, lon: Optional[float] = None):
    if tz_input:
        s = tz_input.strip()
        abbrev = {
            "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
            "EST": "America/New_York", "EDT": "America/New_York",
            "CST": "America/Chicago", "CDT": "America/Chicago",
            "MST": "America/Denver", "MDT": "America/Denver",
            "UTC": "UTC", "GMT": "UTC",
        }
        if s.upper() in abbrev:
            return ZoneInfo(abbrev[s.upper()])
        try:
            return ZoneInfo(s)
        except Exception:
            pass
    if lat is not None and lon is not None:
        try:
            from timezonefinder import TimezoneFinder
            name = TimezoneFinder().timezone_at(lng=lon, lat=lat)
            if name:
                return ZoneInfo(name)
        except Exception:
            pass
    return timezone.utc


def lookup_us_zip(zipcode: str) -> Optional[Tuple[float, float, str]]:
    if not US_ZIP_CSV.exists():
        return None
    z = zipcode.strip()
    with open(US_ZIP_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            code = (row.get("code") or row.get("zipcode") or "").strip()
            if code == z or code.lstrip("0") == z.lstrip("0"):
                lat = float(row["lat"])
                lon = float(row["lon"])
                city = row.get("city", "")
                state = row.get("state", "")
                return lat, lon, f"{city}, {state}, USA"
    return None


def geocode_place(place: str, prefer_online: bool = True) -> Tuple[float, float, str, Optional[str]]:
    """Returns lat, lon, display, tzname. Uses sistema if available, else zip/Nominatim."""
    s = place.strip()
    # direct "lat,lon"
    if "," in s:
        bits = [b.strip() for b in s.split(",")]
        try:
            lat_f, lon_f = float(bits[0]), float(bits[1])
            if -90 <= lat_f <= 90 and -180 <= lon_f <= 180:
                return lat_f, lon_f, f"Coords {lat_f},{lon_f}", None
        except ValueError:
            pass
    if s.isdigit() and len(s) in (5, 9):
        hit = lookup_us_zip(s[:5])
        if hit:
            return hit[0], hit[1], hit[2], None

    mod = _try_load_sistema()
    if mod is not None and hasattr(mod, "geocode_location"):
        try:
            return mod.geocode_location(s, prefer_online=prefer_online)
        except Exception:
            pass

    if prefer_online:
        try:
            import requests
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": s, "format": "json", "limit": 1},
                headers={"User-Agent": "r3d_drag0n7-web/1.0"},
                timeout=10,
            )
            if r.status_code == 200 and r.json():
                data = r.json()[0]
                return float(data["lat"]), float(data["lon"]), data.get("display_name", s), None
        except Exception:
            pass
    raise ValueError(
        f"Could not geocode '{place}'. Provide lat/lon, a US zip, or install geopy/requests for city lookup."
    )


def equal_house_cusps(asc: float) -> List[float]:
    return [(asc + i * 30.0) % 360.0 for i in range(12)]


def whole_sign_cusps(asc: float) -> List[float]:
    start = int(asc // 30) * 30.0
    return [(start + i * 30.0) % 360.0 for i in range(12)]


def porphyry_cusps(asc: float, mc: float) -> List[float]:
    # simplified: equal-ish with MC at 10
    cusps = equal_house_cusps(asc)
    cusps[9] = mc % 360.0
    return cusps


def approximate_asc_mc(jd_ut: float, lat: float, lon: float) -> Tuple[float, float]:
    """Rough local sidereal → ASC/MC approximation for fallback."""
    T = (jd_ut - 2451545.0) / 36525.0
    gmst = 280.46061837 + 360.98564736629 * (jd_ut - 2451545.0) + 0.000387933 * T * T
    lst = (gmst + lon) % 360.0
    eps = 23.439291 - 0.0130042 * T
    # ASC approximation
    lat_r = math.radians(lat)
    eps_r = math.radians(eps)
    lst_r = math.radians(lst)
    y = -math.cos(lst_r)
    x = math.sin(lst_r) * math.cos(eps_r) + math.tan(lat_r) * math.sin(eps_r)
    asc = math.degrees(math.atan2(y, x)) % 360.0
    mc = lst % 360.0
    return asc, mc


def builtin_planets(jd_ut: float) -> Dict[str, Dict[str, float]]:
    planets = {}
    d = jd_ut - 2451545.0
    for name, (lon0, rate) in _MEAN_ELEMENTS.items():
        lon = (lon0 + rate * d) % 360.0
        planets[name] = {"ecl_lon": lon, "ecl_lat": 0.0, "distance_au": None}
    return planets


def compute_with_sistema(
    mode: str,
    dt_utc: datetime,
    lat: float,
    lon: float,
) -> Tuple[Dict[str, Any], str]:
    """Returns (astro_dict, backend_label)."""
    mod = _try_load_sistema()
    if mod is None:
        jd = jd_from_datetime(dt_utc)
        return {"planets": builtin_planets(jd), "houses": {}, "note": "builtin mean longitudes"}, "builtin"

    jd = jd_from_datetime(dt_utc) if not hasattr(mod, "jd_from_datetime") else mod.jd_from_datetime(dt_utc)
    backend = "builtin"
    astro: Dict[str, Any] = {}

    prefer_swiss = mode.lower() == "nostradamus" and getattr(mod, "HAS_PYSWISSEPH", False)
    prefer_sky = getattr(mod, "HAS_SKYFIELD", False) and mode.lower() != "paranoid"

    if prefer_swiss:
        try:
            astro = mod.compute_planet_positions_swisseph(jd, lat, lon, eph_path=str(DATA_DIR))
            backend = "swisseph"
        except Exception as exc:
            astro = {"error": f"swisseph failed: {exc}"}
    if (not astro.get("planets")) and prefer_sky and mode.lower() != "paranoid":
        try:
            try:
                astro = mod.compute_planet_positions_skyfield(dt_utc, lat, lon, allow_download=True)
            except TypeError:
                astro = mod.compute_planet_positions_skyfield(dt_utc, lat, lon)
            backend = "skyfield"
        except Exception as exc:
            if not astro:
                astro = {"error": f"skyfield failed: {exc}"}
    if not astro.get("planets"):
        # Paranoid / offline: only local ephemeris (no Skyfield download)
        try:
            if hasattr(mod, "compute_planet_positions_skyfield") and getattr(mod, "HAS_SKYFIELD", False):
                try:
                    astro = mod.compute_planet_positions_skyfield(
                        dt_utc, lat, lon, allow_download=(mode.lower() != "paranoid")
                    )
                except TypeError:
                    if mode.lower() == "paranoid":
                        raise
                    astro = mod.compute_planet_positions_skyfield(dt_utc, lat, lon)
                backend = "skyfield"
        except Exception:
            pass
    if not astro.get("planets"):
        astro = {"planets": builtin_planets(jd), "houses": {}, "note": "builtin mean longitudes (no ephemeris)"}
        backend = "builtin"
    return astro, backend


def build_houses(astro: Dict[str, Any], house_system: str, lat: float, lon: float, jd: float, mod=None) -> Dict[str, Any]:
    hs = house_system or "Placidus"
    # map aliases
    aliases = {
        "whole": "Whole", "whole sign": "Whole", "wholesign": "Whole",
        "placidus": "Placidus", "equal": "Equal", "porphyry": "Porphyry", "campanus": "Campanus",
    }
    key = aliases.get(hs.lower(), hs)

    if "houses" in astro and isinstance(astro["houses"], dict):
        # swisseph style: may have Placidus etc.
        for cand in (key, "Placidus", "Equal"):
            block = astro["houses"].get(cand) or astro["houses"].get(cand.replace(" ", ""))
            if block and "cusps" in block:
                raw_cusps = list(block["cusps"])
                if len(raw_cusps) == 13:
                    raw_cusps = raw_cusps[1:13]
                cusps = raw_cusps[:12]
                if len(cusps) >= 12:
                    asc_v = block.get("asc", block.get("ascendant", cusps[0]))
                    mc_v = block.get("mc", block.get("MC", cusps[9] if len(cusps) > 9 else 0))
                    return {
                        "system": cand,
                        "cusps": [float(c) for c in cusps],
                        "ascendant": float(asc_v),
                        "mc": float(mc_v),
                    }

    asc, mc = approximate_asc_mc(jd, lat, lon)
    if key == "Equal":
        cusps = equal_house_cusps(asc)
    elif key == "Whole":
        cusps = whole_sign_cusps(asc)
    elif key == "Porphyry":
        if mod and hasattr(mod, "porphyry_cusps"):
            cusps = list(mod.porphyry_cusps(asc, mc))
        else:
            cusps = porphyry_cusps(asc, mc)
    elif key == "Campanus" and mod and hasattr(mod, "campanus_cusps"):
        try:
            cusps = list(mod.campanus_cusps(asc, lat, lon, jd))
        except Exception:
            cusps = equal_house_cusps(asc)
    else:
        cusps = equal_house_cusps(asc)  # Placidus approx when no swiss
        key = key if key != "Placidus" else "Placidus (approx)"
    return {"system": key, "cusps": cusps, "ascendant": asc, "mc": mc}


def format_planets(astro: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for name in PLANETS:
        pdata = astro.get("planets", {}).get(name)
        if not isinstance(pdata, dict) or "ecl_lon" not in pdata:
            continue
        lon = float(pdata["ecl_lon"])
        sign, deg_in = sign_from_degree(lon)
        out.append({
            "name": name,
            "longitude": round(lon, 4),
            "sign": sign,
            "degree_in_sign": round(deg_in, 2),
            "ruler": RULERS.get(sign),
            "latitude": pdata.get("ecl_lat"),
            "distance_au": pdata.get("distance_au") or pdata.get("distance_km"),
        })
    return out


def short_summary(name: Optional[str], planets: List[Dict[str, Any]], houses: Dict[str, Any], mode: str, backend: str) -> str:
    who = name or "Native"
    lines = [f"Chart for {who} — mode {mode}, backend {backend}."]
    sun = next((p for p in planets if p["name"] == "Sun"), None)
    moon = next((p for p in planets if p["name"] == "Moon"), None)
    if sun:
        lines.append(f"Sun in {sun['sign']} {sun['degree_in_sign']:.1f}° — core vitality and direction.")
    if moon:
        lines.append(f"Moon in {moon['sign']} {moon['degree_in_sign']:.1f}° — emotional weather and instincts.")
    asc = houses.get("ascendant")
    if asc is not None:
        sign, deg = sign_from_degree(asc)
        lines.append(f"Ascendant {sign} {deg:.1f}° — the mask and rising tide.")
    # elemental hint
    elem_map = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
    }
    counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for p in planets:
        counts[elem_map.get(p["sign"], "Fire")] += 1
    dom = max(counts, key=counts.get)
    lines.append(f"Elemental balance leans {dom} ({', '.join(f'{k} {v}' for k, v in counts.items())}).")
    if backend == "builtin":
        lines.append("Note: approximate mean longitudes (install skyfield or pyswisseph for research-grade positions).")
    return "\n".join(lines)


def svg_wheel(planets: List[Dict[str, Any]], houses: Dict[str, Any], size: int = 360) -> str:
    cx = cy = size / 2
    r_outer = size * 0.42
    r_inner = size * 0.28
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" class="chart-wheel" aria-label="Natal chart wheel">',
        f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#f0c674" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="rgba(20,4,8,0.85)" stroke="#ff3b4a" stroke-width="1.5"/>',
    ]
    # sign wedges
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x2 = cx + r_outer * math.cos(ang)
        y2 = cy + r_outer * math.sin(ang)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="rgba(255,255,255,0.12)" />')
        mid = math.radians(i * 30 + 15 - 90)
        tx = cx + (r_outer - 18) * math.cos(mid)
        ty = cy + (r_outer - 18) * math.sin(mid)
        parts.append(
            f'<text x="{tx:.1f}" y="{ty:.1f}" fill="#c9a0a8" font-size="9" text-anchor="middle" dominant-baseline="middle">{SIGNS[i][:2]}</text>'
        )
    # house cusps
    for i, cusp in enumerate(houses.get("cusps", [])[:12]):
        ang = math.radians(float(cusp) - 90)
        x2 = cx + r_inner * math.cos(ang)
        y2 = cy + r_inner * math.sin(ang)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#ff8a5c" stroke-width="0.8" opacity="0.7"/>')
    glyphs = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    }
    for p in planets:
        ang = math.radians(p["longitude"] - 90)
        rr = (r_inner + r_outer) / 2
        x = cx + rr * math.cos(ang)
        y = cy + rr * math.sin(ang)
        g = glyphs.get(p["name"], p["name"][0])
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="#ffe8e8" font-size="14" text-anchor="middle" dominant-baseline="middle">{g}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def run_chart(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry: accepts name?, date, time, place OR lat/lon, timezone?, house_system?, mode?
    """
    try:
        name = payload.get("name")
        date_raw = payload.get("date")
        time_raw = payload.get("time") or "12:00"
        place = payload.get("place")
        lat = payload.get("lat")
        lon = payload.get("lon")
        tz_in = payload.get("timezone")
        house_system = payload.get("house_system") or "Placidus"
        mode = payload.get("mode") or "Ptolemy"
        if mode not in ("Nostradamus", "Ptolemy", "Paranoid"):
            # normalize case
            m = str(mode).strip().capitalize()
            mapping = {"nostradamus": "Nostradamus", "ptolemy": "Ptolemy", "paranoid": "Paranoid"}
            mode = mapping.get(str(mode).lower(), m if m in ("Nostradamus", "Ptolemy", "Paranoid") else "Ptolemy")

        if not date_raw:
            return {"ok": False, "error": "date is required (YYYY-MM-DD or DD/MM/YYYY or MM/DD/YYYY)"}

        dt_date = parse_date_local(str(date_raw), preferred="MDY")
        ttime = parse_time_local(str(time_raw))

        display = None
        tzname = None
        if lat is not None and lon is not None:
            lat_f, lon_f = float(lat), float(lon)
            display = f"Coords {lat_f},{lon_f}"
        elif place:
            lat_f, lon_f, display, tzname = geocode_place(
                str(place), prefer_online=(mode != "Paranoid")
            )
        else:
            return {"ok": False, "error": "Provide place or lat/lon"}

        tzinfo = resolve_timezone(tz_in or tzname, lat_f, lon_f)
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
        dt_utc = local_dt.astimezone(timezone.utc)
        jd = jd_from_datetime(dt_utc)

        astro, backend = compute_with_sistema(mode, dt_utc, lat_f, lon_f)
        mod = _try_load_sistema()
        houses = build_houses(astro, house_system, lat_f, lon_f, jd, mod=mod)
        planets = format_planets(astro)

        interpretation = None
        if mod is not None and hasattr(mod, "ChartInterpreter") and planets:
            try:
                interpreter = mod.ChartInterpreter()
                planets_interp = interpreter.interpret_planets_and_aspects(astro)
                patterns_interp = interpreter.interpret_chart_patterns(astro)
                # houses_interp may need cusps dict keyed by system
                cusps_map = {
                    houses["system"]: {
                        "cusps": houses["cusps"],
                        "asc": houses.get("ascendant"),
                        "mc": houses.get("mc"),
                    }
                }
                houses_interp = ""
                if hasattr(interpreter, "interpret_houses"):
                    try:
                        houses_interp = interpreter.interpret_houses(astro, cusps_map)
                    except Exception:
                        houses_interp = ""
                synthesis = ""
                if hasattr(interpreter, "generate_synthesis"):
                    try:
                        synthesis = interpreter.generate_synthesis(astro, cusps_map)
                    except Exception:
                        pass
                interpretation = "\n\n".join(x for x in [planets_interp, patterns_interp, houses_interp, synthesis] if x)
            except Exception as exc:
                interpretation = f"(Interpreter unavailable: {exc})"

        summary = short_summary(name, planets, houses, mode, backend)
        wheel = svg_wheel(planets, houses)

        return {
            "ok": True,
            "input": {
                "name": name,
                "date": dt_date.isoformat(),
                "local_time": local_dt.isoformat(),
                "utc": dt_utc.isoformat(),
                "location": {"lat": lat_f, "lon": lon_f, "display": display},
                "timezone": str(getattr(tzinfo, "key", tzinfo)),
                "house_system": house_system,
                "mode": mode,
            },
            "backend": backend,
            "sistema": sistema_status(),
            "planets": planets,
            "houses": houses,
            "summary": summary,
            "interpretation": interpretation,
            "wheel_svg": wheel,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
            "detail": traceback.format_exc(limit=4),
            "sistema": sistema_status(),
        }


def heuristic_ai_reading(chart: Dict[str, Any], question: Optional[str] = None) -> Dict[str, Any]:
    """Templated enrichment when no API key is present."""
    if not chart.get("ok"):
        return {"ok": False, "error": "Need a successful chart payload under 'chart'"}
    planets = chart.get("planets") or []
    name = (chart.get("input") or {}).get("name") or "Seeker"
    sun = next((p for p in planets if p["name"] == "Sun"), None)
    moon = next((p for p in planets if p["name"] == "Moon"), None)
    houses = chart.get("houses") or {}
    asc_sign = None
    if houses.get("ascendant") is not None:
        asc_sign, _ = sign_from_degree(houses["ascendant"])

    tone = {
        "Aries": "bold and initiatory", "Taurus": "steady and sensual",
        "Gemini": "curious and quicksilver", "Cancer": "protective and lunar",
        "Leo": "radiant and proud", "Virgo": "precise and devoted",
        "Libra": "harmonizing and relational", "Scorpio": "intense and transformative",
        "Sagittarius": "questing and philosophical", "Capricorn": "ambitious and structural",
        "Aquarius": "inventive and future-minded", "Pisces": "dreaming and empathic",
    }
    bits = [f"AI reading (heuristic) for {name}."]
    if sun:
        bits.append(f"Your Sun in {sun['sign']} colors the chart {tone.get(sun['sign'], 'unique')} — own that flame without apology.")
    if moon:
        bits.append(f"The Moon in {moon['sign']} asks you to tend {tone.get(moon['sign'], 'your inner tides')} in private rituals.")
    if asc_sign:
        bits.append(f"Rising {asc_sign} is how the room meets you first: {tone.get(asc_sign, 'memorable')}.")
    if question:
        bits.append(f"On your question — «{question}» — weigh the Sun’s aim against the Moon’s need; the answer lives in their dialogue, not in either alone.")
    else:
        bits.append("Ask a grounded question next time for a tighter reading. For now: move like the dragon — coil before you strike.")
    bits.append("Set OPENAI_API_KEY or PERPLEXITY_API_KEY to enable live model enrichment.")
    return {
        "ok": True,
        "provider": "heuristic",
        "reading": "\n\n".join(bits),
    }


async def live_ai_reading(chart: Dict[str, Any], question: Optional[str] = None) -> Dict[str, Any]:
    """Optional live call if API keys present; otherwise heuristic."""
    openai_key = os.environ.get("OPENAI_API_KEY")
    pplx_key = os.environ.get("PERPLEXITY_API_KEY")
    if not openai_key and not pplx_key:
        return heuristic_ai_reading(chart, question)

    summary = chart.get("summary") or ""
    planets = chart.get("planets") or []
    placement_blob = "; ".join(
        f"{p['name']} {p['sign']} {p['degree_in_sign']}°" for p in planets[:10]
    )
    prompt = (
        "You are an astrologer with a celestial Chinese-dragon voice: vivid, respectful, concise.\n"
        f"Chart summary:\n{summary}\nPlacements: {placement_blob}\n"
        f"Question: {question or 'Give a short natal overview (under 250 words).'}"
    )
    try:
        import json
        import urllib.request

        if pplx_key:
            body = json.dumps({
                "model": "sonar",
                "messages": [
                    {"role": "system", "content": "Astrologer, concise poetic prose."},
                    {"role": "user", "content": prompt},
                ],
            }).encode()
            req = urllib.request.Request(
                "https://api.perplexity.ai/chat/completions",
                data=body,
                headers={"Authorization": f"Bearer {pplx_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode())
            text = data["choices"][0]["message"]["content"]
            return {"ok": True, "provider": "perplexity", "reading": text}

        body = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Astrologer, concise poetic prose."},
                {"role": "user", "content": prompt},
            ],
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())
        text = data["choices"][0]["message"]["content"]
        return {"ok": True, "provider": "openai", "reading": text}
    except Exception as exc:
        fallback = heuristic_ai_reading(chart, question)
        fallback["warning"] = f"Live AI failed ({exc}); returned heuristic."
        return fallback
