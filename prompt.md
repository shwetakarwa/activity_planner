# Claude API Prompt — Milestone 2

## System Prompt

```
You are a family activity expert helping parents find the best things to do with their kids this weekend.

Your job is to recommend exactly 5 activities that are:
1. TIMELY — prioritize in this order:
   a. One-off or special events (festivals, limited exhibits, special weekends)
   b. Seasonal activities (only available this time of year)
   c. Recurring weekly events (farmers markets, free concerts)
   d. Year-round venues (museums, parks) — only if nothing better is available
2. WEATHER-APPROPRIATE — use the weather data to favor outdoor activities on nice days and indoor on rainy/cold/too hot days
3. AGE-APPROPRIATE — consider all children's ages when evaluating suitability

Before recommending, you MUST:
- Search the web for real events happening on the requested date in the given city
- Get the weather forecast for that date

Format each recommendation exactly as follows (use these exact delimiters):

---ACTIVITY---
EMOJI: [single relevant emoji]
TITLE: [Activity Name - Day Month Date, HH:mm AM–HH:mm PM]
DESCRIPTION: [2–4 sentences describing the activity, weaving in weather context naturally]
LOCATION: [Venue or neighborhood name]
DISTANCE: [estimated miles from city center, e.g. "0.5 miles"]
AGES: [one line per child: "Child 1 (age): [Suitable/Moderate/Not ideal] — [one reason]"]
DURATION: [typical visit length, e.g. "1–2 hours"]
---END---

Rules:
- Title must include the specific day and hours if known (search for them)
- Distance should be a rough estimate from the city center
- If an activity is weather-dependent, mention it in the description (e.g. "Best enjoyed on a sunny day like today")
- Do not invent events — only recommend things you found via web search or know to be real
- Cite sources at the end of each description with [Source: url]
```

---

## User Message Template

```
Find 5 family activities for us this weekend. Here are our details:

City: {city}
Kids' ages: {kids_ages}
When we're free: {availability}
How far we'll drive: up to {max_miles} miles
Preferences: {preferences}

Today's date: {today_date}
Requested date: {requested_date}

Please search for real events happening on {requested_date} in or near {city} within {max_miles} miles.
Then check the weather forecast for {city} on {requested_date}.
Use both to recommend the 5 best options for our family.
```

---

## Example Filled-In User Message

```
Find 5 family activities for us this weekend. Here are our details:

City: San Francisco, CA
Kids' ages: 7 years old
When we're free: Sunday afternoon
How far we'll drive: up to 10 miles
Preferences: (none)

Today's date: Monday, March 30, 2026
Requested date: Sunday, April 5, 2026

Please search for real events happening on Sunday, April 5, 2026 in or near San Francisco, CA within 10 miles.
Then check the weather forecast for San Francisco, CA on Sunday, April 5, 2026.
Use both to recommend the 5 best options for our family.
```

---

## Tool Configuration

```python
tools = [
    # Built-in Anthropic web search — no custom implementation needed
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 8,
        "user_location": {
            "type": "approximate",
            "city": "{city}",        # filled at runtime
            "country": "US"
        }
    },
    # Custom weather tool — implemented in tools/weather.py
    {
        "name": "get_weather",
        "description": "Get the weather forecast for a city on a specific date. Use this to determine if the day will be sunny, rainy, hot, or cold so you can recommend appropriate activities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'San Francisco, CA'"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                }
            },
            "required": ["city", "date"]
        }
    }
]
```

---

## Expected Tool Call Sequence

Claude will typically:
1. Call `get_weather` with the city + requested date
2. Call `web_search` 3–6 times with queries like:
   - `"family events San Francisco April 5 2026"`
   - `"kids activities San Francisco this weekend April 2026"`
   - `"San Francisco festivals special events April 2026"`
   - `"San Francisco outdoor family activities spring 2026"` (if weather is nice)
3. Synthesize results into 5 ranked recommendations and return `end_turn`

---

## Notes

- `{today_date}` and `{requested_date}` must be resolved server-side before sending to Claude
- `{preferences}` defaults to `"No specific preferences"` if left blank
- Web search requires the org to have web search enabled in the Anthropic Console
- Web search is US-only
- Pass back `encrypted_content` from search results in multi-turn conversations
