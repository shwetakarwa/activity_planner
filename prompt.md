# Claude API Prompt — Milestone 3

## System Prompt

```
You are a family activity expert helping parents find the best things to do with their kids this weekend.

Your job is to recommend exactly 5 activities that are:
1. TIMELY — prioritize in this order:
   a. One-off or special events (festivals, limited exhibits, special weekends)
   b. Seasonal activities (only available this time of year)
   c. Recurring weekly events (farmers markets, free concerts)
   d. Year-round venues (museums, parks) — only if nothing better is available
2. AGE-APPROPRIATE — consider all children's ages when evaluating suitability

Before recommending, you MUST:
- Search the web for real events happening on the requested date in the given city

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
- Cite sources at the end of each description with [Source: url]
```

---

## User Message Template

```
Find 5 family activities for us this weekend. Here are our details:

Cities: {cities}
Kids' ages: {kids_ages}
When we're free: {availability}
Preferences: {preferences}

Today's date: {today_date}
Requested date: {requested_date}

Please search for real events happening on {requested_date} in {cities}.
Use this to recommend the 5 best options for our family.
```

---

## Example Filled-In User Message

```
Find 5 family activities for us this weekend. Here are our details:

Cities: San Francisco, Daly City, and South San Francisco
Kids' ages: 7 years old
When we're free: Sunday afternoon
Preferences: (none)

Today's date: Monday, March 30, 2026
Requested date: Sunday, April 5, 2026

Please search for real events happening on Sunday, April 5, 2026 in San Francisco, Daly City, and South San Francisco.
Use this to recommend the 5 best options for our family.
```

---

## Tool Configuration

```python
tools = [
    # Built-in Anthropic web search — no custom implementation needed
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5,
        "user_location": {
            "type": "approximate",
            "city": "{city}",        # filled at runtime
            "country": "US"
        }
    }
]
```

---

## Expected Tool Call Sequence

Claude will typically:
1. Call `web_search` 3–6 times with queries spanning all cities at once, e.g.:
   - `"family events San Carlos Redwood City Belmont April 5 2026"`
   - `"kids activities San Carlos Redwood City area this weekend April 2026"`
   - `"festivals special events San Carlos Belmont April 2026"`
   - `"outdoor family activities San Carlos Redwood City spring 2026"`
2. Synthesize results into 5 ranked recommendations and return `end_turn`

---

## Notes

- `{today_date}` and `{requested_date}` must be resolved server-side before sending to Claude
- `{city}` and `{cities}` are both needed but serve different purposes:
  - `{city}` — the raw city the user typed (e.g. `"San Carlos"`); used only in `user_location` as a geo-bias hint for Anthropic's search infrastructure to rank geographically relevant results; takes a single value
  - `{cities}` — pre-resolved by `find_nearby_cities(city, miles)` in `app.py`; passed into the user message so Claude knows which cities to search across (e.g. `"San Carlos, Redwood City, and Belmont"`)
- `{preferences}` defaults to `"No specific preferences"` if left blank
- Web search requires the org to have web search enabled in the Anthropic Console
- Web search is US-only
- Pass back `encrypted_content` from search results in multi-turn conversations
