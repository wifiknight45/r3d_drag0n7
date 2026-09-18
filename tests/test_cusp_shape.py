"""Unified cusp shape helpers."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from r3d_dragon.houses import (
    normalize_cusp_system,
    unify_cusps_map,
    get_placidus_cusps,
    porphyry_cusps,
    equal_house_cusps,
)


def test_normalize_list():
    n = normalize_cusp_system(list(range(12)))
    assert n["cusps"] == list(range(12))
    assert n["asc"] == 0
    assert "mc" in n


def test_normalize_dict_legacy_ascendant():
    n = normalize_cusp_system({"cusps": list(range(12)), "ascendant": 15.0, "mc": 100.0})
    assert n["asc"] == 15.0
    assert n["mc"] == 100.0


def test_normalize_len13():
    n = normalize_cusp_system(list(range(13)))
    assert len(n["cusps"]) == 12
    assert n["cusps"][0] == 1


def test_unify_and_get_placidus():
    raw = {
        "Placidus": {"cusps": equal_house_cusps(30.0), "ascendant": 30.0, "mc": 120.0},
        "Equal": equal_house_cusps(30.0),
    }
    u = unify_cusps_map(raw)
    assert set(u["Placidus"].keys()) >= {"cusps", "asc", "mc"}
    assert len(get_placidus_cusps(u)) == 12
    # interpreter-style: no KeyError when accessing via helper
    assert get_placidus_cusps(u)[0] == 30.0


def test_porphyry_12():
    c = porphyry_cusps(0.0, 90.0)
    assert len(c) == 12
    assert abs(c[0] - 0.0) < 1e-6
    assert abs(c[9] - 90.0) < 1e-6


if __name__ == "__main__":
    test_normalize_list()
    test_normalize_dict_legacy_ascendant()
    test_normalize_len13()
    test_unify_and_get_placidus()
    test_porphyry_12()
    print("cusps OK")
