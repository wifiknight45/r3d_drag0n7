"""House cusp helpers and unified cusp data shape for the interpreter."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Union

CuspSystem = Dict[str, Any]
CuspsBySystem = Dict[str, CuspSystem]


def equal_house_cusps(asc: float) -> List[float]:
    return [(asc + i * 30) % 360 for i in range(12)]


def whole_sign_cusps(asc: float) -> List[float]:
    sign_start = (math.floor(asc / 30) * 30) % 360
    return [(sign_start + i * 30) % 360 for i in range(12)]


def porphyry_cusps(asc: float, mc: float) -> List[float]:
    """
    Geometric Porphyry: trisect ASC–MC and MC–DESC quadrants.
    Used when Swiss Porphyry (b'O') is unavailable.
    """
    asc = asc % 360
    mc = mc % 360
    dsc = (asc + 180) % 360
    ic = (mc + 180) % 360

    def arc(a: float, b: float) -> float:
        return (b - a) % 360

    def trisect(start: float, end: float) -> List[float]:
        span = arc(start, end)
        return [(start + span * (i / 3.0)) % 360 for i in range(1, 3)]

    # Houses: 1=ASC, 10=MC, 7=DSC, 4=IC; fill intermediate via trisection
    c = [0.0] * 12
    c[0] = asc
    c[9] = mc
    c[6] = dsc
    c[3] = ic
    # ASC -> IC (houses 2,3)
    t = trisect(asc, ic)
    c[1], c[2] = t[0], t[1]
    # IC -> DSC (houses 5,6)
    t = trisect(ic, dsc)
    c[4], c[5] = t[0], t[1]
    # DSC -> MC (houses 8,9)
    t = trisect(dsc, mc)
    c[7], c[8] = t[0], t[1]
    # MC -> ASC (houses 11,12)
    t = trisect(mc, asc)
    c[10], c[11] = t[0], t[1]
    return [round(x, 6) for x in c]


def normalize_cusp_system(
    data: Union[Sequence[float], Mapping[str, Any], None],
    *,
    asc: Optional[float] = None,
    mc: Optional[float] = None,
) -> CuspSystem:
    """
    Unify cusp payloads to:
      {"cusps": [12 floats], "asc": float, "mc": float}
    Accepts legacy list-of-12 or dicts with ascendant/asc/mc keys.
    """
    if data is None:
        cusps: List[float] = []
    elif isinstance(data, Mapping):
        raw = data.get("cusps", data.get("cusp", []))
        if isinstance(raw, (list, tuple)):
            cusps = [float(x) for x in raw]
        else:
            cusps = []
        if asc is None:
            asc = data.get("asc", data.get("ascendant"))
        if mc is None:
            mc = data.get("mc", data.get("MC"))
    else:
        cusps = [float(x) for x in data]

    if len(cusps) == 13:
        cusps = cusps[1:13]
    elif len(cusps) > 12:
        cusps = cusps[:12]

    if asc is None and cusps:
        asc = float(cusps[0])
    if mc is None:
        mc = float(cusps[9]) if len(cusps) >= 10 else (float(asc) if asc is not None else 0.0)

    return {
        "cusps": cusps,
        "asc": float(asc) if asc is not None else 0.0,
        "mc": float(mc) if mc is not None else 0.0,
    }


def unify_cusps_map(raw: Mapping[str, Any]) -> CuspsBySystem:
    """Normalize an entire {system_name: ...} mapping."""
    out: CuspsBySystem = {}
    for name, val in raw.items():
        out[str(name)] = normalize_cusp_system(val)
    return out


def get_placidus_cusps(cusps: Mapping[str, Any]) -> List[float]:
    """Safe accessor for interpreter — never KeyError on shape mismatch."""
    if not cusps:
        return []
    plac = cusps.get("Placidus")
    if plac is None:
        # try first available system
        plac = next(iter(cusps.values()), None)
    norm = normalize_cusp_system(plac)
    return list(norm["cusps"])


def make_system_entry(cusps12: Sequence[float], asc: float, mc: float) -> CuspSystem:
    return normalize_cusp_system({"cusps": list(cusps12), "asc": asc, "mc": mc})
