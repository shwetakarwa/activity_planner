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

### Milestone 2 — Live Claude API + Web Search + Weather
Replace dummy data with real agentic backend.

- `tools/weather.py`: Open-Meteo geocoding + forecast → returns temp, conditions, outdoor suitability for the requested date
- `prompts.py`: system prompt with seasonal/timely prioritization; tool definitions for `web_search_20250305` (built-in) + custom `get_weather`
- `app.py`: agentic loop replacing dummy cards:
  - Loop handles `tool_use` stop_reason → execute tools → append results → continue until `end_turn`
  - Stream final response with `st.write_stream()`
  - Show live status via `st.status()` while tools run

**Done when:** "San Carlos, kid age 3 months and 7 years, this Sunday, 10 miles" returns 5 real upcoming events with actual weather context.

---

### Milestone 3 — Polish & Deploy
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
