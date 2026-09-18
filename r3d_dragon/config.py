"""Paths and shared configuration for r3d_dragon."""
from __future__ import annotations

import os

# Package root is r3d_dragon/; repo root is parent.
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PACKAGE_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs")
KEYS_FILE = os.path.join(DATA_DIR, "keys.json")
ZIPFILE = os.path.join(DATA_DIR, "US_zipcodes.csv")
TZ_CACHE = os.path.join(DATA_DIR, "tz_cache.csv")
EPHEM_SNAPSHOT = os.path.join(DATA_DIR, "ephem_snapshot.json")
EVENTS_CACHE = os.path.join(DATA_DIR, "events_cache.json")

OUT_VERBOSE = os.path.join(OUTPUT_DIR, "chart_verbose.txt")
OUT_SUMMARY = os.path.join(OUTPUT_DIR, "chart_summary.txt")
OUT_INTERPRETATION = os.path.join(OUTPUT_DIR, "chart_interpretation.txt")
OUT_HOROSCOPE = os.path.join(OUTPUT_DIR, "chart_horoscope.txt")
OUT_ASTRO_RAW = os.path.join(OUTPUT_DIR, "astro_data_raw.json")
OUT_WHEEL_PNG = os.path.join(OUTPUT_DIR, "int_chart_wheel.png")
OUT_WHEEL_HTML = os.path.join(OUTPUT_DIR, "chart_wheel.html")
OUT_PDF = os.path.join(OUTPUT_DIR, "chart_report.pdf")

TZ_ABBREV_MAP = {
    "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    "EST": "America/New_York", "EDT": "America/New_York",
    "CST": "America/Chicago", "CDT": "America/Chicago",
    "MST": "America/Denver", "MDT": "America/Denver",
    "UTC": "UTC", "GMT": "Etc/Greenwich",
    "BST": "Europe/London", "CET": "Europe/Paris", "CEST": "Europe/Paris",
}

# Expected columns in data/US_zipcodes.csv
ZIP_COLUMNS = ("code", "city", "state", "county", "area_code", "lat", "lon")
