from prompts import build_user_message
from search import parse_activities


INPUTS = {
    "city": "San Carlos",
    "ages": "2 years",
    "availability": "Sunday afternoon",
    "miles": 10,
    "prefs": "",
}
CITIES = ["San Carlos", "Redwood City", "Belmont"]
TODAY = "Monday, March 30, 2026"
REQUESTED = "Sunday, April 5, 2026"


def test_build_user_message_includes_cities():
    msg = build_user_message(INPUTS, TODAY, REQUESTED, CITIES)
    assert "San Carlos" in msg
    assert "Redwood City" in msg
    assert "Belmont" in msg


def test_build_user_message_includes_dates():
    msg = build_user_message(INPUTS, TODAY, REQUESTED, CITIES)
    assert TODAY in msg
    assert REQUESTED in msg


SINGLE_BLOCK = """
---ACTIVITY---
EMOJI: 🎪
TITLE: Spring Fair - Sunday April 5, 10:00 AM–5:00 PM
DESCRIPTION: A fun spring fair with rides and games. Great for families with young children. [Source: https://example.com]
LOCATION: Central Park, San Carlos
DISTANCE: 1.5 miles
AGES: Child 1 (2): Suitable — lots of toddler-friendly activities
DURATION: 2–3 hours
---END---
"""

FIVE_BLOCKS = "\n".join(
    f"---ACTIVITY---\nEMOJI: 🎪\nTITLE: Activity {i}\nDESCRIPTION: Desc {i}\n"
    f"LOCATION: Loc {i}\nDISTANCE: 1 mile\nAGES: Child 1: Suitable\nDURATION: 1 hour\n---END---"
    for i in range(1, 6)
)


def test_parse_activities_basic():
    activities = parse_activities(SINGLE_BLOCK)
    assert len(activities) == 1
    assert activities[0]["emoji"] == "🎪"
    assert activities[0]["title"] == "Spring Fair - Sunday April 5, 10:00 AM–5:00 PM"
    assert activities[0]["location"] == "Central Park, San Carlos"


def test_parse_activities_count():
    activities = parse_activities(FIVE_BLOCKS)
    assert len(activities) == 5
