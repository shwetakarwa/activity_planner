from __future__ import annotations

SYSTEM_PROMPT = """You are a family activity expert helping parents find the best things to do with their kids this weekend.

Your job is to recommend exactly 5 activities that are:
1. TIMELY — prioritize in this order:
   a. One-off or special events (festivals, limited exhibits, special weekends)
   b. Seasonal activities (only available this time of year)
   c. Recurring weekly events (farmers markets, free concerts)
   d. Year-round venues (museums, parks) — only if nothing better is available
2. AGE-APPROPRIATE — consider all children's ages when evaluating suitability

Before recommending, you MUST:
- Search the web for real events happening on the requested date in the given cities

Format each recommendation exactly as follows (use these exact delimiters):

---ACTIVITY---
EMOJI: [single relevant emoji]
TITLE: [Activity Name - Day Month Date, HH:mm AM–HH:mm PM]
DESCRIPTION: [2–4 sentences describing the activity]
LOCATION: [Venue or neighborhood name]
DISTANCE: [estimated miles from city center, e.g. "0.5 miles"]
AGES: [one line per child: "Child 1 (age): [Suitable/Moderate/Not ideal] — [one reason]"]
DURATION: [typical visit length, e.g. "1–2 hours"]
---END---

Rules:
- Title must include the specific day and hours if known (search for them)
- Distance should be a rough estimate from the city center
- Do not invent events — only recommend things you found via web search or know to be real
- Cite sources at the end of each description with [Source: url]"""


def _format_cities(cities: list[str]) -> str:
    if len(cities) == 1:
        return cities[0]
    if len(cities) == 2:
        return f"{cities[0]} and {cities[1]}"
    return ", ".join(cities[:-1]) + f", and {cities[-1]}"


def build_user_message(
    inputs: dict, today_date: str, requested_date: str, cities: list[str]
) -> str:
    cities_str = _format_cities(cities)
    prefs = inputs.get("prefs", "").strip() or "No specific preferences"
    return f"""Find 5 family activities for us this weekend. Here are our details:

Cities: {cities_str}
Kids' ages: {inputs['ages']}
When we're free: {inputs['availability']}
Preferences: {prefs}

Today's date: {today_date}
Requested date: {requested_date}

Please search for real events happening on {requested_date} in {cities_str}.
Use this to recommend the 5 best options for our family."""


def build_tools(city: str) -> list:
    return [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
            "user_location": {
                "type": "approximate",
                "city": city,
                "country": "US",
            },
        }
    ]
