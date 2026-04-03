from __future__ import annotations

import pytest

from cache import get_cached_events, make_cache_key, purge_old_entries, store_events


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Point cache module at a temp DB so tests never touch the real file."""
    import cache
    monkeypatch.setattr(cache, "_DB_PATH", tmp_path / ".activity_cache.db")


def test_cache_miss_returns_none():
    key = make_cache_key(["San Carlos"], "2 years", "2099-12-31")
    assert get_cached_events(key, "2099-12-31") is None


def test_cache_store_and_retrieve():
    key = make_cache_key(["San Carlos", "Redwood City"], "2 years", "2099-12-31")
    store_events(key, ["San Carlos", "Redwood City"], "2 years", "2099-12-31", "some events")
    assert get_cached_events(key, "2099-12-31") == "some events"


def test_cache_expired_for_past_date():
    key = make_cache_key(["San Carlos"], "2 years", "2000-01-01")
    store_events(key, ["San Carlos"], "2 years", "2000-01-01", "old events")
    assert get_cached_events(key, "2000-01-01") is None


def test_cache_key_order_independent():
    key_ab = make_cache_key(["A", "B"], "3 years", "2099-12-31")
    key_ba = make_cache_key(["B", "A"], "3 years", "2099-12-31")
    assert key_ab == key_ba


def test_purge_old_entries_removes_past(monkeypatch):
    import cache

    key = make_cache_key(["Dublin"], "1 year", "2000-06-01")
    store_events(key, ["Dublin"], "1 year", "2000-06-01", "stale events")

    # Confirm it's in the DB before purge
    with cache._connect() as conn:
        row = conn.execute(
            "SELECT cache_key FROM event_cache WHERE cache_key = ?", (key,)
        ).fetchone()
    assert row is not None

    purge_old_entries()

    with cache._connect() as conn:
        row = conn.execute(
            "SELECT cache_key FROM event_cache WHERE cache_key = ?", (key,)
        ).fetchone()
    assert row is None


def test_purge_old_entries_keeps_future():
    key = make_cache_key(["Dublin"], "1 year", "2099-12-31")
    store_events(key, ["Dublin"], "1 year", "2099-12-31", "future events")
    purge_old_entries()
    assert get_cached_events(key, "2099-12-31") == "future events"
