"""Historical events (Wikipedia OnThisDay) with offline cache."""
from __future__ import annotations

import json
import os
from datetime import date
from typing import Any, Dict, List

from . import deps
from .config import EVENTS_CACHE
from .geo import OfflineDataError


def fetch_events_on_date(dt: date, prefer_online: bool = True, paranoid: bool = False) -> List[Dict[str, Any]]:
    if paranoid or not prefer_online:
        return _load_cache(dt)

    if deps.HAS_REQUESTS and deps.requests is not None:
        url = f"https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{dt.month:02d}/{dt.day:02d}"
        try:
            r = deps.requests.get(url, timeout=10, headers={"User-Agent": "r3d_dragon/1.0"})
            if r.status_code == 200:
                data = r.json()
                events = []
                for cat in ("selected", "events", "births", "deaths"):
                    for item in data.get(cat, [])[:5]:
                        events.append({
                            "category": cat,
                            "year": item.get("year"),
                            "text": item.get("text"),
                        })
                return events
        except Exception:
            pass
    return _load_cache(dt)


def _load_cache(dt: date) -> List[Dict[str, Any]]:
    if not os.path.exists(EVENTS_CACHE):
        return []
    try:
        with open(EVENTS_CACHE, "r", encoding="utf-8") as fh:
            cache = json.load(fh)
        key = f"{dt.month:02d}-{dt.day:02d}"
        return cache.get(key, cache.get(dt.isoformat(), []))
    except Exception:
        return []
