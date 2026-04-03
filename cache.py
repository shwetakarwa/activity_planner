from __future__ import annotations

import hashlib
import sqlite3
from datetime import date
from pathlib import Path

_DB_PATH = Path(__file__).parent / ".activity_cache.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS event_cache (
            cache_key   TEXT PRIMARY KEY,
            cities      TEXT,
            ages        TEXT,
            date_iso    TEXT,
            raw_events  TEXT,
            created_at  TEXT
        )
    """)
    conn.commit()
    return conn


def make_cache_key(cities: list[str], ages: str, date_iso: str) -> str:
    """Order-independent cache key based on cities, ages, and date."""
    parts = "|".join(sorted(c.lower().strip() for c in cities))
    parts += f"|{ages.lower().strip()}|{date_iso}"
    return hashlib.sha256(parts.encode()).hexdigest()


def get_cached_events(cache_key: str, date_iso: str) -> str | None:
    """Return cached raw events, or None if not found or date has passed."""
    if date_iso < date.today().isoformat():
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT raw_events FROM event_cache WHERE cache_key = ?",
            (cache_key,),
        ).fetchone()
    return row[0] if row else None


def store_events(
    cache_key: str,
    cities: list[str],
    ages: str,
    date_iso: str,
    raw_events: str,
) -> None:
    """Persist raw events to the cache."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO event_cache
                (cache_key, cities, ages, date_iso, raw_events, created_at)
            VALUES (?, ?, ?, ?, ?, date('now'))
            """,
            (cache_key, ", ".join(cities), ages, date_iso, raw_events),
        )


def purge_old_entries() -> None:
    """Remove cache entries for dates that have already passed."""
    today = date.today().isoformat()
    with _connect() as conn:
        conn.execute("DELETE FROM event_cache WHERE date_iso < ?", (today,))
