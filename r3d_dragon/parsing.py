"""Date/time/timezone parsing helpers."""
from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Tuple, Union
from zoneinfo import ZoneInfo

from .config import TZ_ABBREV_MAP


def eprint(*a, **k):
    import sys
    print(*a, file=sys.stderr, **k)


def parse_date_input(raw_date: str, preferred_format: Optional[str] = None) -> date:
    s = (raw_date or "").strip()
    # ISO
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", s)
    if not m:
        raise ValueError(f"Unrecognized date: {raw_date}")
    a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if preferred_format == "DMY":
        return date(y, b, a)
    if preferred_format == "MDY":
        return date(y, a, b)
    # disambiguate
    if a > 12 and b <= 12:
        return date(y, b, a)  # DMY
    if b > 12 and a <= 12:
        return date(y, a, b)  # MDY
    # ambiguous — default MDY for US-centric zip data, document in README
    return date(y, a, b)


def resolve_tz(tz_hint: Optional[str]) -> Optional[Union[ZoneInfo, timezone]]:
    if not tz_hint:
        return None
    s = tz_hint.strip()
    if s.upper() in TZ_ABBREV_MAP:
        s = TZ_ABBREV_MAP[s.upper()]
    if re.match(r"^[Uu][Tt][Cc]([+-]\d{1,2}(:?\d{2})?)?$", s) or re.match(r"^[+-]\d{1,2}(:?\d{2})?$", s):
        m = re.search(r"([+-])(\d{1,2})(?::?(\d{2}))?", s)
        if m:
            sign = 1 if m.group(1) == "+" else -1
            hours = int(m.group(2))
            mins = int(m.group(3) or 0)
            return timezone(sign * timedelta(hours=hours, minutes=mins))
        return timezone.utc
    try:
        return ZoneInfo(s)
    except Exception:
        return None


def parse_time_input(time_str: str, tz_hint: Optional[str] = None) -> Tuple[time, Optional[Union[ZoneInfo, timezone]]]:
    s = (time_str or "").strip()
    tzinfo = resolve_tz(tz_hint) if tz_hint else None
    # peel trailing tz token
    parts = s.split()
    if parts:
        maybe_tz = parts[-1]
        resolved = resolve_tz(maybe_tz)
        if resolved is not None and not re.match(r"^\d", maybe_tz):
            tzinfo = tzinfo or resolved
            s = " ".join(parts[:-1])
    s = s.strip()
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM|am|pm)?$", s)
    if not m:
        raise ValueError(f"Unrecognized time: {time_str}")
    hh, mm, ss = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    ampm = m.group(4)
    if ampm:
        ampm = ampm.upper()
        if ampm == "PM" and hh < 12:
            hh += 12
        if ampm == "AM" and hh == 12:
            hh = 0
    return time(hh, mm, ss), tzinfo
