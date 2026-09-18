# r3d_drag0n7

Astrological / astronomical birth-chart generator.

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Canonical entrypoint

One runnable engine (package + thin wrapper):

```bash
pip install -r requirements.txt

# either:
python sistema.py --interactive
python sistema.py --mode Paranoid --date 1990-01-15 --time "12:00" --tz America/New_York --location 10001

# or:
python -m r3d_dragon --interactive
```

Obsolete single-file copies (`sistema7.py`, `sistema_completa.py`, pre-fix `sistema.py`,
and the `sistema_enhanced.py` merge source) live under [`archive/`](archive/) — not deleted.

## Modes (behavior matches the code)

| Mode | Ephemeris | Network |
|------|-----------|---------|
| **Nostradamus** | Swiss Ephemeris (`pyswisseph`) when installed | Geocode / OnThisDay allowed |
| **Ptolemy** | Skyfield (`de421.bsp`; may download on first use) | Geocode / OnThisDay allowed |
| **Paranoid** | Local Swiss **or** local `data/de421.bsp` only | **Refuses** Nominatim and Skyfield downloads; use US zip or `lat,lon` |

Paranoid is **offline-local**, not “full astrology offline magic”: missing zip DB or ephemeris files produce a clear error.

## Layout

```
r3d_dragon/          # package: cli, geo, ephemeris, houses, interpret, …
sistema.py           # thin CLI → r3d_dragon
data/US_zipcodes.csv # code,city,state,county,area_code,lat,lon
archive/             # historical single-file variants
web/                 # optional FastAPI UI (uses r3d_dragon)
tests/               # smoke tests (zip, cusp shape, Swiss unpack mocks)
outputs/             # generated charts
```

## House / Swiss contracts (fixed)

- `cusps, ascmc = swe.houses(...)` (correct order)
- `xx, flag = swe.calc_ut(...); lon = xx[0]`
- MC = `ascmc[1]` (not Vertex / `ascmc[3]`)
- Porphyry prefers Swiss `b'O'`; otherwise geometric trisection fallback (documented on the cusp payload)
- Cusp arrays of length 13 are sliced to 12 (`cusps[1:13]`)
- Interpreter always receives unified shape:
  `{"Placidus": {"cusps": [...12], "asc": ..., "mc": ...}, ...}`

## Zip lookup

`ZIPFILE` → `data/US_zipcodes.csv`, parsed with `csv.DictReader` and columns
`code,city,state,county,area_code,lat,lon`.

## Web UI (optional)

```bash
pip install -r requirements-web.txt
uvicorn web.app:app --reload --port 7860
```

See [`web/README.md`](web/README.md). GitHub Pages (if used) is landing-only; chart compute needs this API or the CLI.

## Tests

```bash
python tests/test_swiss_unpack.py
python tests/test_cusp_shape.py
python tests/test_zip_parse.py
python tests/test_paranoid_geo.py
# or: pytest tests/
```

## Requirements

- Python **3.9+**
- See `requirements.txt` (includes **fpdf2**, not deprecated `fpdf`)
- Optional: Swiss ephemeris data files for Nostradamus; `data/de421.bsp` for offline Skyfield / Paranoid

## License

MIT — see [LICENSE](LICENSE).
