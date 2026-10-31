"""
LabLine Indian Standard Time (IST) & UTC Formatting Utility
All timestamps are stored in UTC in the database and rendered in IST (Asia/Kolkata, UTC+05:30).
Strict format specification: 'HH:MM DD/MM/YY' (24-hour time, no seconds, no month names).
Example: '14:32 31/10/26'
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# Indian Standard Time (IST) is UTC+05:30
IST_TIMEZONE = timezone(timedelta(hours=5, minutes=30))


def to_utc(dt: Optional[datetime] = None) -> datetime:
    """Return timezone-aware UTC datetime."""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def to_ist(dt: Optional[datetime]) -> Optional[datetime]:
    """Convert UTC or naive datetime to timezone-aware IST (UTC+05:30)."""
    if dt is None:
        return None
    utc_dt = to_utc(dt)
    return utc_dt.astimezone(IST_TIMEZONE)


def format_ist(dt: Optional[datetime], default_empty: str = "Never logged in") -> str:
    """
    Format datetime into exact Indian Timezone (IST) representation:
    HH:MM in 24-hour format and DD/MM/YY date (e.g. '14:32 31/10/26').
    No seconds, no month names.
    """
    if dt is None:
        return default_empty
    ist_dt = to_ist(dt)
    if ist_dt is None:
        return default_empty
    return ist_dt.strftime("%H:%M %d/%m/%y")


def to_iso_utc(dt: Optional[datetime]) -> Optional[str]:
    """Return standardized ISO-8601 string with explicit UTC timezone offset."""
    if dt is None:
        return None
    return to_utc(dt).isoformat()

