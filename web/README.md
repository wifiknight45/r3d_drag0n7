# r3d_drag0n7 Web App

Celestial Chinese-dragon UI that runs birth charts via the local sistema engine.

## Quick start

From the repository root:

```
pip install fastapi uvicorn
uvicorn web.app:app --reload --port 7860
```

Or with the pinned web extras:

```
pip install -r requirements-web.txt
# optional ephemeris backends (recommended):
pip install skyfield pyswisseph geopy timezonefinder requests python-dateutil
uvicorn web.app:app --reload --port 7860
```

Open http://127.0.0.1:7860

## API

- `POST /api/chart` — compute natal chart JSON
- `POST /api/ai/reading` — AI enrichment (templated / heuristic unless `OPENAI_API_KEY` or `PERPLEXITY_API_KEY` is set)
- `GET /` — static frontend
- `GET /api/health` — backend + sistema status

## Chart request body

```json
{
  "name": "Ada",
  "date": "1815-12-10",
  "time": "14:30",
  "place": "London, UK",
  "lat": null,
  "lon": null,
  "timezone": "Europe/London",
  "house_system": "Placidus",
  "mode": "Ptolemy"
}
```

Modes: `Nostradamus` | `Ptolemy` | `Paranoid`. House systems: `Placidus`, `Equal`, `Whole`, `Porphyry`, `Campanus`.

## Notes

GitHub Pages hosts the landing page only; full chart compute needs this local API.
