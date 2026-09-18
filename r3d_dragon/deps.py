"""Optional dependency detection."""
from __future__ import annotations

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

swe = None
load = None
wgs84 = None
N = E = W = S = None
TimezoneFinder = None
requests = None
FPDF = None
go = None
Image = ImageDraw = ImageFont = None

try:
    import swisseph as _swe
    swe = _swe
    HAS_PYSWISSEPH = True
except Exception:
    pass

try:
    from skyfield.api import load as _load, wgs84 as _wgs84
    from skyfield.api import N as _N, E as _E, W as _W, S as _S
    load = _load
    wgs84 = _wgs84
    N, E, W, S = _N, _E, _W, _S
    HAS_SKYFIELD = True
except Exception:
    pass

try:
    import matplotlib.pyplot as plt  # noqa: F401
    HAS_MATPLOTLIB = True
except Exception:
    pass

try:
    import plotly.graph_objects as _go
    go = _go
    HAS_PLOTLY = True
except Exception:
    pass

try:
    from PIL import Image as _Image, ImageDraw as _ImageDraw, ImageFont as _ImageFont
    Image, ImageDraw, ImageFont = _Image, _ImageDraw, _ImageFont
    HAS_PIL = True
except Exception:
    pass

try:
    from fpdf import FPDF as _FPDF
    FPDF = _FPDF
    HAS_FPDF = True
except Exception:
    pass

try:
    from geopy.geocoders import Nominatim  # noqa: F401
    HAS_GEOPY = True
except Exception:
    pass

try:
    from timezonefinder import TimezoneFinder as _TF
    TimezoneFinder = _TF
    HAS_TFINDER = True
except Exception:
    pass

try:
    import requests as _requests
    requests = _requests
    HAS_REQUESTS = True
except Exception:
    pass

try:
    from dateutil import parser as du_parser  # noqa: F401
    HAS_DATEUTIL = True
except Exception:
    pass
