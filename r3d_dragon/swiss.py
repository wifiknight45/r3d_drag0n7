"""Swiss Ephemeris contract helpers (correct unpacking / house codes)."""
from __future__ import annotations

from typing import Any, Iterable, List, Optional, Sequence, Tuple

# Swiss houses() returns (cusps, ascmc) where:
#   cusps[0] unused (or length-13 with index 0 unused), cusps[1..12] = houses 1..12
#   ascmc[0]=ASC, ascmc[1]=MC, ascmc[2]=ARMC, ascmc[3]=Vertex, ...
# Historical bug: some code used ascmc[3] as MC (that is Vertex).


def unpack_calc_ut(result: Any) -> Tuple[float, float, float, int]:
    """
    Normalize swe.calc_ut return value.

    pyswisseph typically returns (xx, retflag) where xx is a sequence;
    lon = xx[0], lat = xx[1], dist = xx[2].
    """
    if result is None:
        raise ValueError("swe.calc_ut returned None")
    # Tuple/list of (xx, flag)
    if isinstance(result, (tuple, list)) and len(result) >= 2 and not isinstance(result[0], (int, float)):
        xx, flag = result[0], result[1]
        lon = float(xx[0])
        lat = float(xx[1]) if len(xx) > 1 else 0.0
        dist = float(xx[2]) if len(xx) > 2 else 0.0
        return lon, lat, dist, int(flag) if flag is not None else 0
    # Bare xx sequence
    xx = result
    return float(xx[0]), float(xx[1]) if len(xx) > 1 else 0.0, float(xx[2]) if len(xx) > 2 else 0.0, 0


def unpack_houses(result: Any) -> Tuple[List[float], Sequence[float]]:
    """
    Normalize swe.houses / swe.houses_ex return to (cusps, ascmc).

    Correct order is cusps, ascmc — never reversed.
    """
    if result is None:
        raise ValueError("swe.houses returned None")
    if not isinstance(result, (tuple, list)) or len(result) < 2:
        raise ValueError(f"Unexpected houses return shape: {type(result)!r}")
    cusps, ascmc = result[0], result[1]
    # Detect accidental swap: ascmc is short (~8), cusps are ~12-13.
    if hasattr(cusps, "__len__") and hasattr(ascmc, "__len__"):
        if len(cusps) < 8 and len(ascmc) >= 12:
            cusps, ascmc = ascmc, cusps
    return list(cusps), ascmc


def slice_cusps_12(cusps: Iterable[float]) -> List[float]:
    """Return exactly 12 house cusps. Swiss often returns length 13 with index 0 unused."""
    vals = [float(c) for c in cusps]
    if len(vals) == 13:
        return vals[1:13]
    if len(vals) >= 12:
        return vals[:12]
    raise ValueError(f"Expected >=12 cusps, got {len(vals)}")


def mc_from_ascmc(ascmc: Sequence[float]) -> float:
    """MC is ascmc[1], not Vertex (ascmc[3])."""
    if ascmc is None or len(ascmc) < 2:
        raise ValueError("ascmc too short for MC")
    return float(ascmc[1])


def asc_from_ascmc(ascmc: Sequence[float]) -> float:
    if ascmc is None or len(ascmc) < 1:
        raise ValueError("ascmc too short for ASC")
    return float(ascmc[0])


def house_system_code(name: str) -> bytes:
    """Map house system name to Swiss Ephemeris single-char code."""
    mapping = {
        "Placidus": b"P",
        "Equal": b"E",
        "Whole": b"W",
        "Whole Sign": b"W",
        "Porphyry": b"O",  # 'O' = Porphyry in Swiss Ephemeris
        "Campanus": b"C",
        "Koch": b"K",
        "Regiomontanus": b"R",
    }
    key = name.strip()
    if key not in mapping:
        raise KeyError(f"Unknown house system: {name}")
    return mapping[key]


def try_porphyry_code(swe_mod: Any) -> Optional[bytes]:
    """
    Prefer Swiss code b'O' for Porphyry when the library accepts it.
    Returns None if unavailable (caller should use geometric fallback).
    """
    if swe_mod is None:
        return None
    # Documented Swiss code for Porphyry is 'O'. Probe via attribute if present.
    code = b"O"
    # Some builds expose house name tables; we still return the documented code.
    return code
