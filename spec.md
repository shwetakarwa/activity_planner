# Family Activity Finder — Spec

## Overview
A web app that helps parents find timely, age-appropriate weekend activities nearby. Prioritizes one-off and seasonal events over generic year-round options. Built with Streamlit for simplicity — single Python file UI, free deployment on Streamlit Community Cloud.

---

## Requirements

**Inputs**
- City (text)
- Kid ages (free text, e.g. "3 months and 2 years")
- Date & time availability (free text, e.g. "Saturday afternoon")
- Maximum driving distance (slider, 1–50 miles)
- Optional preferences (free text, e.g. "indoor, budget-friendly")

**Outputs — 5 activity cards, each with:**
- Numbered rank (#1–#5) + activity emoji
- Bold title including day and specific hours (e.g. "Muni Heritage Weekend - Sunday 10am–4pm")
- 2–4 sentence description with weather context woven in
- Location name + estimated driving distance
- Age appropriateness per child
- Source citation link (required by Anthropic ToS for web search results)

**Prioritization order:** one-off events → seasonal/limited-run → recurring weekly → year-round venues

---

## Tech Stack

| Layer | Choice |
|---|---|
| UI + Backend | Python + Streamlit (single `app.py`) |
| LLM | Claude claude-sonnet-4-6 via Anthropic SDK |
| Web search | Anthropic built-in `web_search_20250305` |
| Weather | Open-Meteo API (free, no key needed) |
| Streaming | `st.write_stream()` |
| Deployment | Streamlit Community Cloud (free) |

**Dependencies:** `streamlit`, `anthropic`, `httpx`, `python-dotenv`

---

## File Structure

```
activity_finder/
├── app.py           # Entire Streamlit app (UI + agentic loop)
├── tools/
│   └── weather.py   # Open-Meteo geocoding + forecast
├── prompts.py       # System prompt + tool definitions
├── requirements.txt
├── .env             # ANTHROPIC_API_KEY (local only, never committed)
├── .gitignore
└── CLAUDE.md
```

---

## Design Guidelines

- Two-column layout via `st.columns([1, 2])`: form on left, results on right
- Activity cards via `st.container(border=True)` + `st.markdown()` for bold titles and emojis
- Show progress while loading via `st.status()` ("Searching for events...", "Checking weather...")
- Keep styling minimal — lean on Streamlit defaults, avoid heavy custom CSS
- Responsive: Streamlit handles mobile automatically (two columns may stack on narrow screens)

---

## Milestones

### Milestone 1 — Streamlit UI with Dummy Data
Static Streamlit app with no backend calls.

- `app.py`: two-column layout, all 5 form inputs, "Search Activities" + "Clear" buttons
- On click: renders 5 hardcoded dummy activity cards in the results column
- `requirements.txt`: all dependencies listed

**Done when:** `streamlit run app.py` loads, form renders correctly, dummy cards display on submit.

---

### Milestone 2 — Parse Date & Location, Show on UI
Parse the existing City, Date & Time Availability, and Max Distance fields to confirm what was understood. No new form fields.

- `requirements.txt`: add `dateparser`
- `app.py`:
  - `parse_date(availability_text) -> str | None` using `dateparser`
  - `find_nearby_cities(city, miles) -> list[str]`: geocode the entered city to lat/lon via Open-Meteo geocoding API, then query nearby populated places within the given radius (e.g. via Nominatim/OpenStreetMap `https://nominatim.openstreetmap.org/search`); return a list of city names including the entered city
  - On Search click, show a plain-English confirmation above the results: "Here are the events in San Carlos, Redwood City, and Belmont on Sunday, April 5."
  - If date can't be parsed, show a warning instead; dummy cards still display below as before

**Done when:** Submitting "San Carlos" + "this Sunday" + 10 miles renders a confirmation listing nearby cities and the resolved date above the existing dummy cards.

---

### Milestone 3 — Find Activities via Claude Web Search
Replace dummy cards with real results using the Anthropic web search tool (no weather yet).

- `prompts.py`: `SYSTEM_PROMPT` with activity prioritization and `---ACTIVITY---` / `---END---` delimiters; `build_user_message(inputs, today_date, requested_date)`; `TOOLS` list containing only `web_search_20250305`
- `app.py`: `run_search(inputs)` agentic loop; loop until `end_turn`, parse activity blocks, replace dummy cards with real results; wrap in `st.status()` spinner

**Done when:** "San Carlos, 2 years, this Sunday, 10 miles" returns 5 real upcoming events with actual dates/times in titles.

---

### Milestone 4 — Weather-Aware Suggestions
Layer Open-Meteo weather data so Claude can recommend weather-appropriate activities.

- `tools/weather.py`: `geocode(city)` → lat/lon via Open-Meteo geocoding API; `get_weather(city, date)` → `{date, temp_high_f, temp_low_f, condition, suitable_for_outdoor}`
- `prompts.py`: add `get_weather` schema to `TOOLS`; update `SYSTEM_PROMPT` to instruct Claude to call it and factor conditions into picks
- `app.py`: handle `tool_use` stop_reason in `run_search()` → call `tools/weather.py` → append `tool_result` → continue loop

**Done when:** Activity descriptions reflect actual Open-Meteo forecast for the requested city/day.

---

### Milestone 5 — Polish & Deploy
- Error states: API down, web search not enabled, no results found
- Input validation: warn on empty city or date before submitting
- Source citation links beneath each card (Anthropic ToS requirement)
- Mobile check: test on both phones, adjust layout if columns are too cramped
- **Deploy to Streamlit Community Cloud:**
  - Push repo to GitHub (`.env` excluded via `.gitignore`)
  - Connect repo in Streamlit Community Cloud dashboard
  - Set `ANTHROPIC_API_KEY` as a secret in the dashboard
  - Share the permanent `yourapp.streamlit.app` URL

---

## APIs & Services

| Service | Key Required | Cost |
|---|---|---|
| Anthropic Claude | Yes | Per token |
| Anthropic web search | Yes + org admin enables in Console | $10 / 1000 searches |
| Open-Meteo | No | Free |
| Streamlit Community Cloud | No | Free |

**Note:** Web search (`web_search_20250305`) is US-only.
