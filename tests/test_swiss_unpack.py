"""Swiss Ephemeris unpack helpers (mocked; no swe required)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from r3d_dragon.swiss import (
    unpack_calc_ut,
    unpack_houses,
    slice_cusps_12,
    mc_from_ascmc,
    asc_from_ascmc,
)


def test_unpack_calc_ut_tuple():
    lon, lat, dist, fl = unpack_calc_ut(([123.4, 1.2, 0.9], 42))
    assert abs(lon - 123.4) < 1e-9
    assert abs(lat - 1.2) < 1e-9
    assert abs(dist - 0.9) < 1e-9
    assert fl == 42


def test_unpack_houses_order():
    cusps = [0] + list(range(10, 130, 10))  # 13 elems
    ascmc = [10.0, 280.0, 1.0, 99.0]  # asc, mc, armc, vertex
    c, a = unpack_houses((cusps, ascmc))
    assert len(c) == 13
    assert mc_from_ascmc(a) == 280.0
    assert asc_from_ascmc(a) == 10.0
    assert mc_from_ascmc(a) != a[3]  # not Vertex


def test_slice_cusps_13():
    vals = list(range(13))
    out = slice_cusps_12(vals)
    assert out == list(range(1, 13))


def test_slice_cusps_12():
    vals = list(range(12))
    assert slice_cusps_12(vals) == vals


if __name__ == "__main__":
    test_unpack_calc_ut_tuple()
    test_unpack_houses_order()
    test_slice_cusps_13()
    test_slice_cusps_12()
    print("swiss OK")
