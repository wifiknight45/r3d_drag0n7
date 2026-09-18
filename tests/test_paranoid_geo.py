"""Paranoid mode refuses network geocode."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from r3d_dragon.geo import geocode_location, OfflineDataError


def test_paranoid_accepts_coords():
    lat, lon, display, _ = geocode_location("40.7,-74.0", paranoid=True)
    assert abs(lat - 40.7) < 1e-6


def test_paranoid_accepts_zip():
    lat, lon, display, _ = geocode_location("10001", paranoid=True)
    assert lat != 0


def test_paranoid_refuses_unknown_city():
    try:
        geocode_location("DefinitelyNotARealPlaceXYZ123", paranoid=True)
        assert False, "should have raised"
    except OfflineDataError as e:
        assert "Paranoid" in str(e) or "network" in str(e).lower()


if __name__ == "__main__":
    test_paranoid_accepts_coords()
    test_paranoid_accepts_zip()
    test_paranoid_refuses_unknown_city()
    print("paranoid OK")
