"""r3d_dragon — canonical chart engine package."""
from __future__ import annotations

__version__ = "0.2.0"

from . import deps
from .chart import generate_chart
from .cli import main
from .ephemeris import (
    compute_planet_positions_skyfield,
    compute_planet_positions_swisseph,
    jd_from_datetime,
    load_ephemeris_preference,
)
from .houses import normalize_cusp_system, unify_cusps_map, equal_house_cusps, whole_sign_cusps, porphyry_cusps
from .interpret import ChartInterpreter, sign_from_degree
from .swiss import unpack_calc_ut, unpack_houses, slice_cusps_12, mc_from_ascmc

# Compatibility aliases expected by web/chart_service.py
HAS_PYSWISSEPH = deps.HAS_PYSWISSEPH
HAS_SKYFIELD = deps.HAS_SKYFIELD
HAS_FPDF = deps.HAS_FPDF
HAS_PLOTLY = deps.HAS_PLOTLY
HAS_PIL = deps.HAS_PIL
HAS_REQUESTS = deps.HAS_REQUESTS
HAS_TFINDER = deps.HAS_TFINDER

__all__ = [
    "__version__",
    "generate_chart",
    "main",
    "normalize_cusp_system",
    "unify_cusps_map",
    "unpack_calc_ut",
    "unpack_houses",
    "slice_cusps_12",
    "mc_from_ascmc",
    "compute_planet_positions_swisseph",
    "compute_planet_positions_skyfield",
    "jd_from_datetime",
    "load_ephemeris_preference",
    "ChartInterpreter",
    "sign_from_degree",
    "equal_house_cusps",
    "whole_sign_cusps",
    "porphyry_cusps",
    "HAS_PYSWISSEPH",
    "HAS_SKYFIELD",
    "HAS_FPDF",
    "HAS_PLOTLY",
    "HAS_PIL",
    "HAS_REQUESTS",
    "HAS_TFINDER",
]
