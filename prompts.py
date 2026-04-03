from __future__ import annotations

GATHER_SYSTEM_PROMPT = """You are a family event researcher. Your job is to find real, upcoming family events using web search.
Make sure look through public facebook groups for events, eventbrite, city websites for events.

Search for events happening in the given cities on the given date. Cast a wide net — include:
- One-off or special events (festivals, limited exhibits, special weekends)
- Seasonal activities (only available this time of year)
- Recurring weekly events (farmers markets, free concerts)
- Year-round venues (museums, parks, play spaces, hikes)

For each event you find, output it in this format:

EVENT: [Event name]
DATE: [Date and time if known]
LOCATION: [Venue name and city]
DESCRIPTION: [1-2 sentences about what it is]
URL: [Source URL]
---

Search thoroughly. Find at least 8-12 events if possible. Do not invent events — only include things you confirmed via web search."""

RANK_SYSTEM_PROMPT = """You are a family activity expert. You will be given a list of real events found via web search. Your job is to select and rank the 5 best activities for a specific family.

Prioritize in this order:
1. One-off or special events (festivals, limited exhibits, special weekends)
2. Seasonal activities (only available this time of year)
3. Recurring weekly events (farmers markets, free concerts)
4. Year-round venues (museums, parks, hikes) — only if nothing better is available

Format each recommendation exactly as follows (use these exact delimiters):

---ACTIVITY---
EMOJI: [single relevant emoji]
TITLE: [Activity Name - Day Month Date, HH:mm AM–HH:mm PM]
DESCRIPTION: [2–4 sentences. Weave in why it suits this family's preferences and ages]
LOCATION: [Venue or neighborhood name]
DISTANCE: [estimated miles from the home city center]
AGES: [one line per child: "Child 1 (age): [Suitable/Moderate/Not ideal] — [one reason]"]
DURATION: [typical visit length, e.g. "1–2 hours"]
---END---

Rules:
- Only recommend events from the provided list — do not invent or add new events
- Title must include the specific day and hours
- Cite sources: end each description with [Source: url]
- If fewer than 5 suitable events are available, fall back to year-round venues to reach 5"""


def _format_cities(cities: list[str]) -> str:
    if len(cities) == 1:
        return cities[0]
    if len(cities) == 2:
        return f"{cities[0]} and {cities[1]}"
    return ", ".join(cities[:-1]) + f", and {cities[-1]}"


def build_gather_message(
    cities: list[str], ages: str, today_date: str, requested_date: str
) -> str:
    cities_str = _format_cities(cities)
    return f"""Find family events for kids (ages: {ages}) in these cities on {requested_date}:
Cities: {cities_str}
Today's date: {today_date}

Search for real events happening on {requested_date}. Include all types: one-off festivals, seasonal activities, weekly events, and year-round venues."""


def build_rank_message(
    raw_events: str, inputs: dict, requested_date: str
) -> str:
    prefs = inputs.get("prefs", "").strip() or "No specific preferences"
    return f"""Select the 5 best activities for our family from the events below.

Family details:
- Kids' ages: {inputs['ages']}
- Preferences: {prefs}
- Date: {requested_date}
- Home city: {inputs['city']}

Events found via web search:
{raw_events}

Pick the 5 most suitable events considering our family's ages and preferences. Use only events from the list above."""


def build_tools(city: str) -> list:
    return [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3,
            "user_location": {
                "type": "approximate",
                "city": city,
                "country": "US",
            },
        }
    ]
