"""US zip CSV parse smoke test."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from r3d_dragon.geo import lookup_zip
from r3d_dragon.config import ZIPFILE


def test_zipfile_path():
    assert ZIPFILE.endswith("US_zipcodes.csv")
    assert Path(ZIPFILE).exists(), f"missing {ZIPFILE}"


def test_lookup_known_zip():
    # Holtsville NY 00501 from sample header rows
    hit = lookup_zip("00501")
    assert hit is not None, "00501 should resolve"
    lat, lon, display = hit
    assert 40.0 < lat < 42.0
    assert -74.0 < lon < -71.0
    assert "Holtsville" in display or "NY" in display


def test_lookup_nycish():
    hit = lookup_zip("10001")
    assert hit is not None
    lat, lon, display = hit
    assert 40.0 < lat < 41.5


if __name__ == "__main__":
    test_zipfile_path()
    test_lookup_known_zip()
    test_lookup_nycish()
    print("zip OK")
