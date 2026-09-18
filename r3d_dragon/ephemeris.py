"""Ephemeris backends: Swiss Ephemeris and Skyfield (ecliptic_latlon)."""
from __future__ import annotations

import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from . import deps
from .houses import (
    equal_house_cusps,
    make_system_entry,
    porphyry_cusps,
    whole_sign_cusps,
)
from .swiss import (
    asc_from_ascmc,
    house_system_code,
    mc_from_ascmc,
    slice_cusps_12,
    try_porphyry_code,
    unpack_calc_ut,
    unpack_houses,
)


class EphemerisDownloadError(RuntimeError):
    """Raised when Paranoid mode would need a Skyfield network download."""


def jd_from_datetime(dt_utc: datetime) -> float:
    if dt_utc.tzinfo is None:
        raise ValueError("datetime must be timezone-aware UTC")
    t = dt_utc.astimezone(timezone.utc)
    year, month, day = t.year, t.month, t.day
    hour = t.hour + t.minute / 60 + t.second / 3600 + t.microsecond / 3.6e9
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5 + hour / 24.0


def load_ephemeris_preference() -> str:
    if deps.HAS_PYSWISSEPH:
        return "swisseph"
    if deps.HAS_SKYFIELD:
        return "skyfield"
    return "builtin"


def _call_houses(swe, jd_ut: float, lat: float, lon: float, code: bytes):
    # Prefer houses(); houses_ex accepts hsys as int/bytes depending on binding
    if hasattr(swe, "houses"):
        try:
            return unpack_houses(swe.houses(jd_ut, lat, lon, code))
        except Exception:
            pass
    if hasattr(swe, "houses_ex"):
        # Some bindings want ord(code), some want bytes
        try:
            return unpack_houses(swe.houses_ex(jd_ut, lat, lon, code))
        except Exception:
            return unpack_houses(swe.houses_ex(jd_ut, lat, lon, ord(code)))
    raise RuntimeError("No swe.houses / swe.houses_ex available")


def compute_planet_positions_swisseph(
    jd_ut: float,
    lat: float,
    lon: float,
    eph_path: Optional[str] = None,
) -> Dict[str, Any]:
    if not deps.HAS_PYSWISSEPH or deps.swe is None:
        raise RuntimeError("pyswisseph not available")
    swe = deps.swe
    if eph_path:
        swe.set_ephe_path(eph_path)
    try:
        swe.set_topo(lon, lat, 0)
    except Exception:
        pass

    planet_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
    }
    res: Dict[str, Any] = {"planets": {}, "houses": {}}
    for pname, pid in planet_map.items():
        xx_flag = swe.calc_ut(jd_ut, pid)
        lon_, lat_, dist, flag = unpack_calc_ut(xx_flag)
        res["planets"][pname] = {
            "ecl_lon": lon_,
            "ecl_lat": lat_,
            "distance_au": dist,
            "flag": flag,
        }

    systems = [
        ("Placidus", b"P"),
        ("Equal", b"E"),
        ("Whole", b"W"),
        ("Campanus", b"C"),
    ]
    # Porphyry: prefer b'O'
    porphyry_code = try_porphyry_code(swe)
    for hname, hcode in systems:
        try:
            cusps_raw, ascmc = _call_houses(swe, jd_ut, lat, lon, hcode)
            cusps12 = slice_cusps_12(cusps_raw)
            asc = asc_from_ascmc(ascmc)
            mc = mc_from_ascmc(ascmc)
            res["houses"][hname] = make_system_entry(cusps12, asc, mc)
        except Exception as exc:
            res["houses"][hname] = {"error": str(exc)}

    # Porphyry via Swiss or geometric fallback
    plac = res["houses"].get("Placidus") or {}
    asc = plac.get("asc", 0.0)
    mc = plac.get("mc", 0.0)
    if porphyry_code:
        try:
            cusps_raw, ascmc = _call_houses(swe, jd_ut, lat, lon, porphyry_code)
            cusps12 = slice_cusps_12(cusps_raw)
            res["houses"]["Porphyry"] = make_system_entry(
                cusps12, asc_from_ascmc(ascmc), mc_from_ascmc(ascmc)
            )
            res["houses"]["Porphyry"]["method"] = "swiss:O"
        except Exception:
            res["houses"]["Porphyry"] = make_system_entry(porphyry_cusps(asc, mc), asc, mc)
            res["houses"]["Porphyry"]["method"] = "geometric_fallback"
            res["houses"]["Porphyry"]["note"] = (
                "Swiss Porphyry (b'O') unavailable; used geometric trisection fallback."
            )
    else:
        res["houses"]["Porphyry"] = make_system_entry(porphyry_cusps(asc, mc), asc, mc)
        res["houses"]["Porphyry"]["method"] = "geometric_fallback"

    return res


def _skyfield_loader(*, allow_download: bool):
    if not deps.HAS_SKYFIELD or deps.load is None:
        raise RuntimeError("skyfield not available")
    # Prefer local de421.bsp next to data/ or CWD
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "de421.bsp"),
        os.path.join(os.getcwd(), "de421.bsp"),
        "de421.bsp",
    ]
    local = next((p for p in candidates if os.path.exists(p)), None)
    if local:
        return deps.load(local)
    if not allow_download:
        raise EphemerisDownloadError(
            "Paranoid mode refuses Skyfield ephemeris download. "
            "Place de421.bsp under data/de421.bsp (or install Swiss Ephemeris files) "
            "and re-run."
        )
    return deps.load("de421.bsp")


def compute_planet_positions_skyfield(
    dt_utc: datetime,
    lat: float,
    lon: float,
    *,
    allow_download: bool = True,
) -> Dict[str, Any]:
    if not deps.HAS_SKYFIELD:
        raise RuntimeError("skyfield not available")
    planets = _skyfield_loader(allow_download=allow_download)
    from skyfield.api import load as sf_load
    ts = sf_load.timescale()
    t = ts.from_datetime(dt_utc)
    earth = planets["earth"]
    observer = deps.wgs84.latlon(
        abs(lat) * (deps.N if lat >= 0 else deps.S),
        abs(lon) * (deps.E if lon >= 0 else deps.W),
    )
    top = earth + observer
    res: Dict[str, Any] = {"planets": {}, "houses": {}}
    sf_planet_map = {
        "Sun": "sun", "Moon": "moon",
        "Mercury": "mercury barycenter", "Venus": "venus barycenter",
        "Mars": "mars barycenter", "Jupiter": "jupiter barycenter",
        "Saturn": "saturn barycenter", "Uranus": "uranus barycenter",
        "Neptune": "neptune barycenter", "Pluto": "pluto barycenter",
    }
    for pname, sfname in sf_planet_map.items():
        try:
            target = planets[sfname]
        except Exception:
            continue
        astrometric = top.at(t).observe(target).apparent()
        # Correct API: ecliptic_latlon() — do not use atan2 on RA/Dec
        latlon = astrometric.ecliptic_latlon()
        # skyfield returns (lat, lon, distance) as Angle/Distance objects
        ecl_lat = latlon[0].degrees
        ecl_lon = latlon[1].degrees
        dist = latlon[2].au if len(latlon) > 2 else 0.0
        res["planets"][pname] = {
            "ecl_lon": ecl_lon % 360,
            "ecl_lat": ecl_lat,
            "distance_au": dist,
        }
    # Approximate houses via Equal from a rough ASC (LST-based lightweight)
    # Without Swiss, use Equal from asc≈RAMC estimate: leave empty; chart layer fills.
    return res
