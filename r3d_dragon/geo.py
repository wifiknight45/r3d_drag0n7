"""Geocoding and US zip lookup. Paranoid mode refuses network geocode."""
from __future__ import annotations

import csv
import os
import time
from typing import Optional, Tuple

from . import deps
from .config import ZIPFILE, ZIP_COLUMNS


class OfflineDataError(RuntimeError):
    """Raised in Paranoid mode when required local data is missing."""


def lookup_zip(code: str, zip_path: Optional[str] = None) -> Optional[Tuple[float, float, str]]:
    """
    Parse data/US_zipcodes.csv with columns:
      code,city,state,county,area_code,lat,lon
    Returns (lat, lon, display_name) or None.
    """
    path = zip_path or ZIPFILE
    if not os.path.exists(path):
        return None
    code = code.strip()
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        rename = {}
        if reader.fieldnames:
            for f in reader.fieldnames:
                fl = f.strip().lower()
                if fl in ("code", "zip", "zipcode", "postal_code"):
                    rename[f] = "code"
                elif fl == "city":
                    rename[f] = "city"
                elif fl == "state":
                    rename[f] = "state"
                elif fl in ("lat", "latitude"):
                    rename[f] = "lat"
                elif fl in ("lon", "lng", "longitude"):
                    rename[f] = "lon"
                elif fl == "county":
                    rename[f] = "county"
                elif fl in ("area_code", "areacode"):
                    rename[f] = "area_code"
                else:
                    rename[f] = fl
        for row in reader:
            row = {rename.get(k, (k or "").strip().lower()): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            if str(row.get("code", "")).lstrip("0") == code.lstrip("0") or str(row.get("code", "")) == code:
                try:
                    lat = float(row["lat"])
                    lon = float(row["lon"])
                except (KeyError, TypeError, ValueError):
                    continue
                city = row.get("city") or ""
                state = row.get("state") or ""
                display = f"{city}, {state}".strip(", ")
                return lat, lon, display or f"ZIP {code}"
    return None


def search_zip_by_text(query: str, zip_path: Optional[str] = None) -> Optional[Tuple[float, float, str]]:
    path = zip_path or ZIPFILE
    if not os.path.exists(path):
        return None
    q = query.lower().strip()
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            blob = ",".join(str(v) for v in row.values()).lower()
            if q in blob:
                try:
                    # normalize keys
                    rk = {k.strip().lower(): v for k, v in row.items()}
                    lat = float(rk.get("lat") or rk.get("latitude"))
                    lon = float(rk.get("lon") or rk.get("lng") or rk.get("longitude"))
                    city = rk.get("city", "")
                    state = rk.get("state", "")
                    return lat, lon, f"{city}, {state}".strip(", ")
                except (TypeError, ValueError):
                    continue
    return None


def _tz_at(lat: float, lon: float) -> Optional[str]:
    if not deps.HAS_TFINDER or deps.TimezoneFinder is None:
        return None
    try:
        return deps.TimezoneFinder().timezone_at(lng=lon, lat=lat)
    except Exception:
        return None


def geocode_location(
    location_input: str,
    *,
    prefer_online: bool = True,
    paranoid: bool = False,
    max_retries: int = 3,
) -> Tuple[float, float, str, Optional[str]]:
    """
    Resolve location to (lat, lon, display, tzname).

    Paranoid / prefer_online=False:
      - Uses lat/lon, US zip CSV, and local text search only.
      - Refuses network Nominatim; raises OfflineDataError with a clear message
        when local data cannot resolve the place.
    """
    s = (location_input or "").strip()
    if not s:
        raise ValueError("Location input is empty")

    # Direct coordinates
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) >= 2:
            try:
                flat = float(parts[0].replace("N", "").replace("S", "").strip())
                flon = float(parts[1].replace("E", "").replace("W", "").strip())
                if "W" in s.upper() and flon > 0:
                    flon = -abs(flon)
                if "S" in s.upper() and flat > 0:
                    flat = -abs(flat)
                return flat, flon, f"Coords {flat},{flon}", _tz_at(flat, flon)
            except ValueError:
                pass

    # US zip
    if s.isdigit() or (len(s) in (5, 9, 10) and s.replace("-", "").isdigit()):
        zip_code = s.replace("-", "")[:5]
        hit = lookup_zip(zip_code)
        if hit:
            lat, lon, display = hit
            return lat, lon, display, _tz_at(lat, lon)
        if paranoid or not prefer_online:
            raise OfflineDataError(
                f"Paranoid/offline mode: zip '{zip_code}' not found in local {ZIPFILE}. "
                "Provide lat,lon or ensure data/US_zipcodes.csv is present."
            )

    # Network geocode (refused in paranoid)
    if paranoid or not prefer_online:
        hit = search_zip_by_text(s)
        if hit:
            lat, lon, display = hit
            return lat, lon, display, _tz_at(lat, lon)
        raise OfflineDataError(
            "Paranoid mode refuses network geocoding. "
            "Provide coordinates (lat,lon), a US zip present in data/US_zipcodes.csv, "
            f"or ensure the zip database exists at {ZIPFILE}."
        )

    if prefer_online and deps.HAS_REQUESTS and deps.requests is not None:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "r3d_dragon/1.0 (local; educational)"}
        params = {"q": s, "format": "json", "limit": 1}
        backoff = 1
        for _ in range(max_retries):
            try:
                r = deps.requests.get(url, params=params, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    if data:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                        display = data[0].get("display_name", s)
                        return lat, lon, display, _tz_at(lat, lon)
                    break
                if r.status_code in (429, 503):
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                break
            except Exception:
                time.sleep(backoff)
                backoff *= 2

    hit = search_zip_by_text(s)
    if hit:
        lat, lon, display = hit
        return lat, lon, display, _tz_at(lat, lon)

    raise ValueError(
        "Could not geocode location; provide lat,lon or ensure data/US_zipcodes.csv exists "
        "or network is available for Nominatim."
    )
