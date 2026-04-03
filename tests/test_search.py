from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from search import gather_events, parse_activities, rank_events, run_search

CITIES = ["San Carlos", "Redwood City"]
AGES = "2 years"
DATE_ISO = "2099-12-31"
TODAY = "Monday, March 30, 2026"
REQUESTED = "Sunday, December 31, 2099"
INPUTS = {"city": "San Carlos", "ages": AGES, "availability": "Sunday", "miles": 10, "prefs": ""}

RAW_EVENTS = """EVENT: Spring Fair
DATE: Sunday December 31, 10am-5pm
LOCATION: Central Park, San Carlos
DESCRIPTION: A fun fair with rides.
URL: https://example.com
---"""

RANKED_RESPONSE = (
    "---ACTIVITY---\n"
    "EMOJI: 🎪\n"
    "TITLE: Spring Fair - Sunday December 31, 10:00 AM–5:00 PM\n"
    "DESCRIPTION: A fun fair. [Source: https://example.com]\n"
    "LOCATION: Central Park, San Carlos\n"
    "DISTANCE: 1 mile\n"
    "AGES: Child 1 (2): Suitable — fun for toddlers\n"
    "DURATION: 2 hours\n"
    "---END---\n"
)


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    import cache
    monkeypatch.setattr(cache, "_DB_PATH", tmp_path / ".activity_cache.db")


def _mock_loop(text):
    """Return a patch for _run_agentic_loop that yields a fixed string."""
    return patch("search._run_agentic_loop", return_value=text)


def test_gather_events_stores_result_on_miss():
    with _mock_loop(RAW_EVENTS):
        result, from_cache = gather_events(CITIES, AGES, DATE_ISO, TODAY, REQUESTED, "San Carlos")
    assert result == RAW_EVENTS
    assert from_cache is False

    # Second call should hit cache without calling the loop
    with patch("search._run_agentic_loop", side_effect=AssertionError("should not call API")):
        result2, from_cache2 = gather_events(CITIES, AGES, DATE_ISO, TODAY, REQUESTED, "San Carlos")
    assert result2 == RAW_EVENTS
    assert from_cache2 is True


def test_run_search_hits_cache_on_second_call():
    with _mock_loop(RAW_EVENTS):
        run_search(INPUTS, TODAY, REQUESTED, CITIES, DATE_ISO)

    # Second call: gather must not hit API; only rank (Haiku) runs
    api_call_count = 0

    def count_calls(client, model, system, user_msg, tools=None):
        nonlocal api_call_count
        api_call_count += 1
        assert tools is None, "Phase 2 must not use web search tools"
        return RANKED_RESPONSE

    with patch("search._run_agentic_loop", side_effect=count_calls):
        run_search(INPUTS, TODAY, REQUESTED, CITIES, DATE_ISO)

    assert api_call_count == 1  # only rank phase ran


def test_rank_events_uses_haiku():
    captured_model = {}

    def capture(client, model, system, user_msg, tools=None):
        captured_model["model"] = model
        return RANKED_RESPONSE

    with patch("search._run_agentic_loop", side_effect=capture):
        rank_events(RAW_EVENTS, INPUTS, REQUESTED)

    assert captured_model["model"] == "claude-haiku-4-5-20251001"


def test_rank_events_no_tools():
    def assert_no_tools(client, model, system, user_msg, tools=None):
        assert tools is None
        return RANKED_RESPONSE

    with patch("search._run_agentic_loop", side_effect=assert_no_tools):
        rank_events(RAW_EVENTS, INPUTS, REQUESTED)
