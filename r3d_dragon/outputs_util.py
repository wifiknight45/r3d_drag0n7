"""Output writers and simple chart wheels."""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Mapping

from . import deps


def ensure_dirs(data_dir: str, output_dir: str) -> None:
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)


def write_text_file(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def create_simple_wheel_png(planet_positions: Mapping[str, Any], cusps: List[float], outpath: str) -> bool:
    if not deps.HAS_PIL:
        return False
    size = 800
    img = deps.Image.new("RGB", (size, size), "white")
    draw = deps.ImageDraw.Draw(img)
    cx = cy = size // 2
    r = 300
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline="black", width=2)
    for c in cusps or []:
        ang = math.radians(c)
        x = cx + r * math.cos(ang)
        y = cy - r * math.sin(ang)
        draw.line((cx, cy, x, y), fill="gray", width=1)
    for pname, pdata in (planet_positions or {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            ang = math.radians(pdata["ecl_lon"])
            x = cx + (r - 40) * math.cos(ang)
            y = cy - (r - 40) * math.sin(ang)
            draw.text((x, y), pname[:2], fill="black")
    img.save(outpath)
    return True


def create_plotly_wheel(planet_positions: Mapping[str, Any], cusps: List[float], outpath_html: str) -> bool:
    if not deps.HAS_PLOTLY or deps.go is None:
        return False
    lons = []
    names = []
    for pname, pdata in (planet_positions or {}).items():
        if isinstance(pdata, dict) and "ecl_lon" in pdata:
            names.append(pname)
            lons.append(pdata["ecl_lon"])
    fig = deps.go.Figure()
    fig.add_trace(deps.go.Scatterpolar(r=[1] * len(lons), theta=lons, mode="markers+text", text=names))
    fig.update_layout(template=None, title="Planet positions (ecliptic longitudes)")
    fig.write_html(outpath_html)
    return True
