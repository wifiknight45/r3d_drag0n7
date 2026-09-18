"""Main chart generation pipeline."""
from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from . import deps
from .config import (
    DATA_DIR,
    EVENTS_CACHE,
    OUT_ASTRO_RAW,
    OUT_INTERPRETATION,
    OUT_PDF,
    OUT_SUMMARY,
    OUT_VERBOSE,
    OUT_WHEEL_HTML,
    OUT_WHEEL_PNG,
    OUTPUT_DIR,
)
from .ephemeris import (
    EphemerisDownloadError,
    compute_planet_positions_skyfield,
    compute_planet_positions_swisseph,
    jd_from_datetime,
    load_ephemeris_preference,
)
from .events import fetch_events_on_date
from .geo import OfflineDataError, geocode_location
from .houses import (
    equal_house_cusps,
    get_placidus_cusps,
    make_system_entry,
    normalize_cusp_system,
    porphyry_cusps,
    unify_cusps_map,
    whole_sign_cusps,
)
from .interpret import ChartInterpreter, sign_from_degree
from .knowledge import RULERS
from .outputs_util import create_plotly_wheel, create_simple_wheel_png, ensure_dirs, write_text_file
from .parsing import eprint, parse_date_input, parse_time_input, resolve_tz


def aspects_between(a_deg: float, b_deg: float):
    dif = abs((a_deg - b_deg + 180) % 360 - 180)
    aspects = []
    table = {
        0: ("Conjunction", 8),
        180: ("Opposition", 8),
        120: ("Trine", 7),
        60: ("Sextile", 6),
        90: ("Square", 6),
        150: ("Quincunx", 3),
    }
    for ang, (name, orb) in table.items():
        if abs(dif - ang) <= orb:
            aspects.append((name, ang, dif))
    return aspects


def generate_chart(
    mode: str,
    date_str: str,
    time_str: str,
    tz_input: Optional[str],
    location_input: str,
    date_format_pref: Optional[str] = None,
    interactive: bool = True,
) -> Dict[str, Any]:
    """
    mode: 'Nostradamus' | 'Ptolemy' | 'Paranoid'

    Paranoid reality (documented):
      - No network geocode (Nominatim)
      - No Skyfield ephemeris download
      - Prefer US zip CSV + local Swiss/Skyfield files
      - Clear OfflineDataError / EphemerisDownloadError when local data missing
    """
    ensure_dirs(DATA_DIR, OUTPUT_DIR)
    paranoid = mode == "Paranoid"
    prefer_online = not paranoid

    dt_date = parse_date_input(
        date_str,
        preferred_format="DMY" if date_format_pref == "DMY" else ("MDY" if date_format_pref == "MDY" else None),
    )
    ttime, tzinfo = parse_time_input(time_str, tz_hint=tz_input)
    tzinfo = tzinfo or resolve_tz(tz_input)

    if isinstance(tzinfo, (ZoneInfo, timezone)):
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
    else:
        local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=timezone.utc)
    dt_utc = local_dt.astimezone(timezone.utc)

    try:
        geo_lat, geo_lon, geo_display, tzname = geocode_location(
            location_input, prefer_online=prefer_online, paranoid=paranoid
        )
    except OfflineDataError:
        raise
    except Exception as exc:
        if paranoid:
            raise OfflineDataError(str(exc)) from exc
        raise

    if tzname and not tzinfo:
        try:
            tzinfo = ZoneInfo(tzname)
            local_dt = datetime.combine(dt_date, ttime).replace(tzinfo=tzinfo)
            dt_utc = local_dt.astimezone(timezone.utc)
        except Exception:
            pass

    backend = load_ephemeris_preference()
    jd_ut = jd_from_datetime(dt_utc)
    astro: Dict[str, Any] = {}

    # Backend selection
    # Nostradamus: Swiss preferred
    # Ptolemy: Skyfield
    # Paranoid: local Swiss if present, else local Skyfield file only (no download)
    try:
        if mode == "Nostradamus" and deps.HAS_PYSWISSEPH:
            astro = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
            backend = "swisseph"
        elif mode == "Ptolemy":
            if deps.HAS_SKYFIELD:
                astro = compute_planet_positions_skyfield(
                    dt_utc, geo_lat, geo_lon, allow_download=True
                )
                backend = "skyfield"
            elif deps.HAS_PYSWISSEPH:
                astro = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
                backend = "swisseph"
            else:
                astro = {"error": "No ephemeris backend available. Install pyswisseph or skyfield."}
        elif paranoid:
            if deps.HAS_PYSWISSEPH:
                astro = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
                backend = "swisseph"
            elif deps.HAS_SKYFIELD:
                astro = compute_planet_positions_skyfield(
                    dt_utc, geo_lat, geo_lon, allow_download=False
                )
                backend = "skyfield"
            else:
                raise OfflineDataError(
                    "Paranoid mode: no local ephemeris. Install pyswisseph with local ephemeris files, "
                    "or place data/de421.bsp for Skyfield."
                )
        else:
            # default fallbacks
            if deps.HAS_PYSWISSEPH:
                astro = compute_planet_positions_swisseph(jd_ut, geo_lat, geo_lon)
                backend = "swisseph"
            elif deps.HAS_SKYFIELD:
                astro = compute_planet_positions_skyfield(
                    dt_utc, geo_lat, geo_lon, allow_download=prefer_online
                )
                backend = "skyfield"
            else:
                astro = {"error": "No ephemeris backend available. Install pyswisseph or skyfield."}
    except EphemerisDownloadError:
        raise
    except OfflineDataError:
        raise
    except Exception as e:
        eprint("Ephemeris error:", e)
        traceback.print_exc()
        if deps.HAS_SKYFIELD and not paranoid:
            try:
                astro = compute_planet_positions_skyfield(
                    dt_utc, geo_lat, geo_lon, allow_download=True
                )
                backend = "skyfield"
            except Exception as e2:
                astro = {"error": str(e2)}
        else:
            astro = {"error": str(e)}

    # Unify house / cusp shape
    cusps: Dict[str, Any] = {}
    if "houses" in astro and isinstance(astro["houses"], dict) and astro["houses"]:
        cusps = unify_cusps_map(astro["houses"])
        # Ensure expected keys exist
        plac = cusps.get("Placidus") or next(iter(cusps.values()))
        asc = plac["asc"]
        mc = plac["mc"]
    else:
        asc, mc = 0.0, 0.0
        cusps["Placidus"] = make_system_entry(equal_house_cusps(asc), asc, mc)

    if "Equal" not in cusps:
        cusps["Equal"] = make_system_entry(equal_house_cusps(asc), asc, mc)
    if "Whole" not in cusps:
        cusps["Whole"] = make_system_entry(whole_sign_cusps(asc), asc, mc)
    if "Porphyry" not in cusps:
        cusps["Porphyry"] = make_system_entry(porphyry_cusps(asc, mc), asc, mc)
        cusps["Porphyry"]["method"] = "geometric_fallback"
    if "Campanus" not in cusps:
        cusps["Campanus"] = make_system_entry(equal_house_cusps(asc), asc, mc)
        cusps["Campanus"]["note"] = "Approximate Equal fallback (no Swiss Campanus)"

    # Keep astro houses in unified shape too
    if "houses" in astro:
        astro["houses"] = cusps

    verbose_lines = []
    verbose_lines.append(
        f"Input (interpreted): date={dt_date.isoformat()}, local_time={local_dt.isoformat()}, UTC={dt_utc.isoformat()}"
    )
    verbose_lines.append(f"Location: {geo_display} (lat={geo_lat}, lon={geo_lon})")
    verbose_lines.append(f"Backend: {backend}; Mode: {mode}")
    verbose_lines.append("")
    verbose_lines.append("Planetary positions (ecliptic longitude degrees) and signs:")
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            verbose_lines.append(
                f" - {pname}: {pdata['ecl_lon']:.4f}° (sign {sign} {deg_in:.2f}°), "
                f"lat {pdata.get('ecl_lat')}, dist {pdata.get('distance_au')}"
            )
        else:
            verbose_lines.append(f" - {pname}: {pdata}")
    verbose_lines.append("")
    verbose_lines.append("Houses (cusps) by system (degrees):")
    for sysname, sysdata in cusps.items():
        cvals = normalize_cusp_system(sysdata)["cusps"]
        verbose_lines.append(f" - {sysname}: " + ", ".join(f"{round(c, 4)}" for c in cvals))
    verbose_lines.append("")
    verbose_lines.append("Significant aspects (sample pairwise check among classical planets):")
    planet_list = list(astro.get("planets", {}).keys())
    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            pa = astro["planets"].get(planet_list[i], {})
            pb = astro["planets"].get(planet_list[j], {})
            if not pa or not pb or "ecl_lon" not in pa or "ecl_lon" not in pb:
                continue
            for a in aspects_between(pa["ecl_lon"], pb["ecl_lon"]):
                verbose_lines.append(
                    f"  * {planet_list[i]} - {planet_list[j]}: {a[0]} (angle={a[1]}°, diff={a[2]:.2f}°)"
                )

    summary_lines = ["Chart summary:"]
    for pname, pdata in astro.get("planets", {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            sign, deg_in = sign_from_degree(pdata["ecl_lon"])
            summary_lines.append(f"{pname} in {sign} {deg_in:.1f}° (ruler: {RULERS.get(sign, 'Unknown')})")

    events = fetch_events_on_date(dt_date, prefer_online=prefer_online, paranoid=paranoid)
    event_lines = ["Historical events on this date (sample):"]
    if events:
        for ev in events[:8]:
            event_lines.append(f" - [{ev.get('category')}] {ev.get('year')}: {ev.get('text')}")
    else:
        event_lines.append(" - No events found; optional offline cache: data/events_cache.json")

    interpreter = ChartInterpreter()
    planets_interp = interpreter.interpret_planets_and_aspects(astro)
    patterns_interp = interpreter.interpret_chart_patterns(astro)
    houses_interp = interpreter.interpret_houses(astro, cusps)
    synthesis = interpreter.generate_synthesis(astro, cusps)
    full_interp = "\n".join([planets_interp, patterns_interp, houses_interp, synthesis])

    write_text_file(OUT_VERBOSE, "\n".join(verbose_lines))
    write_text_file(OUT_SUMMARY, "\n".join(summary_lines + [""] + event_lines))
    write_text_file(OUT_INTERPRETATION, full_interp)

    payload = {
        "input": {
            "date": dt_date.isoformat(),
            "local_time": local_dt.isoformat(),
            "utc": dt_utc.isoformat(),
            "location": {"lat": geo_lat, "lon": geo_lon, "display": geo_display},
            "mode": mode,
            "backend": backend,
        },
        "astro": astro,
        "cusps": cusps,
        "events": events,
    }
    with open(OUT_ASTRO_RAW, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    placidus_list = get_placidus_cusps(cusps)
    create_simple_wheel_png(astro.get("planets", {}), placidus_list, OUT_WHEEL_PNG)
    create_plotly_wheel(astro.get("planets", {}), placidus_list, OUT_WHEEL_HTML)

    if deps.HAS_FPDF and deps.FPDF is not None:
        pdf = deps.FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 6, "\n".join(verbose_lines))
        import os
        if os.path.exists(OUT_WHEEL_PNG):
            try:
                pdf.image(OUT_WHEEL_PNG, x=10, w=180)
            except Exception:
                pass
        pdf.output(OUT_PDF)

    print("Outputs written to 'outputs/' directory:")
    print(" - Verbose chart:", OUT_VERBOSE)
    print(" - Summary:", OUT_SUMMARY)
    print(" - Interpretation:", OUT_INTERPRETATION)
    print(" - Raw astro JSON:", OUT_ASTRO_RAW)
    print(" - Wheel PNG (if PIL available):", OUT_WHEEL_PNG)
    print(" - Wheel interactive HTML (if Plotly available):", OUT_WHEEL_HTML)
    if deps.HAS_FPDF:
        print(" - PDF report:", OUT_PDF)
    if mode == "Paranoid":
        print(
            "\nParanoid mode: network geocode and Skyfield downloads are refused. "
            "Used local zip/ephemeris only."
        )
    return payload
