# r3d_drag0n7 Web App

Celestial Chinese-dragon UI that runs birth charts via the canonical `r3d_dragon` engine
(`sistema.py` / `python -m r3d_dragon`).

## Quick start

From the repository root:

```bash
pip install -r requirements.txt -r requirements-web.txt
uvicorn web.app:app --reload --port 7860
```

Open http://127.0.0.1:7860

## API

- `POST /api/chart` — compute natal chart JSON (calls `r3d_dragon.chart.generate_chart`)
- `GET /` — static frontend when `web/static/index.html` is present
- `GET /api/health` — backend + ephemeris status

## Chart request body

```json
{
  "name": "Ada",
  "date": "1815-12-10",
  "time": "14:30",
  "place": "10001",
  "timezone": "America/New_York",
  "house_system": "Placidus",
  "mode": "Ptolemy"
}
```

Modes: `Nostradamus` | `Ptolemy` | `Paranoid`. House systems: `Placidus`, `Equal`, `Whole`, `Porphyry`, `Campanus`.

Paranoid mode refuses network geocode and Skyfield downloads; use US zip or lat,lon plus local ephemeris.
