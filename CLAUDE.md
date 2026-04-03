# Claude Code Instructions

## Working Style
- Always follow `docs/spec.md` and `docs/todo.md` when implementing features. Only deviate from them during active debugging sessions.
- Always add tests for new functionality.
- Keep code as simple as possible — prefer straightforward solutions over clever or abstract ones.
- The user is a staff engineer returning from a break — use Insights to explain what you're doing and why. Suggest improvements where appropriate.
- Always propose a fix and wait for approval before writing code during debugging sessions.
- Save implementation plans in the `docs/` folder, not elsewhere.
- **Keep this file (`CLAUDE.md`) up to date.** After any session that adds a module, completes a milestone, makes a key architecture decision, or changes how the project runs — update the relevant section here before finishing. This file is the primary onboarding document for future sessions.

---

## Project: Family Activity Finder

A Streamlit web app that helps parents find timely, age-appropriate weekend activities nearby. It uses Claude with Anthropic's built-in web search tool to find real events — prioritizing one-off/seasonal events over generic year-round options.

**Run locally:** `streamlit run app.py`
**Key env var:** `ANTHROPIC_API_KEY` in `.env`
**Tests:** `pytest tests/`

---

## Module Map

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI, form inputs, session state, `parse_date()`, `format_city_list()`, `render_card()`, `validate_inputs()`, main search trigger |
| `location.py` | `geocode_city()` via Open-Meteo, `find_nearby_cities()` via Overpass API (OSM) |
| `search.py` | `run_search()` agentic loop (calls Claude + handles `web_search_20250305` tool use), `parse_activities()` parses `---ACTIVITY---` blocks |
| `prompts.py` | `SYSTEM_PROMPT`, `build_user_message()`, `build_tools()` (web search tool schema with user_location) |
| `tests/` | `test_app.py` (UI/card), `test_parse.py` (date + city parsing), `test_prompts.py` (message building + activity parsing) |
| `docs/spec.md` | Full product spec — inputs, outputs, tech stack, all 5 milestones |
| `docs/todo.md` | Milestone-by-milestone checklist — **check this before starting any feature work** |

---

## Milestone Status (as of last commit)

| Milestone | Status | Summary |
|---|---|---|
| M1 — Streamlit UI with dummy data | ✅ Done | Two-column layout, 5 hardcoded activity cards |
| M2 — Parse date & location | ✅ Done | `parse_date()` via dateparser, `find_nearby_cities()` via Overpass API |
| M3 — Claude web search integration | ✅ Done | Agentic loop in `search.py`, real events from Claude |
| M4 — Weather-aware suggestions | ❌ Not started | Needs `tools/weather.py` + Open-Meteo forecast + weather tool in `TOOLS` |
| M5 — Polish & deploy | ❌ Not started | Error states, validation, citations, Streamlit Community Cloud deploy |

> **Note:** `docs/todo.md` M3 checkboxes may show as unchecked — the code is complete (see git log).

---

## Key Architecture Decisions

- **Agentic loop pattern:** `search.py:run_search()` calls Claude, handles `tool_use` stop_reason by echoing back `encrypted_content` from Anthropic's web search results, loops until `end_turn`. This is how Anthropic's hosted web_search_20250305 tool works — results are returned in the tool response content and must be passed back as-is.
- **Structured output via delimiters:** Claude formats each activity between `---ACTIVITY---` / `---END---` markers; `parse_activities()` uses regex to extract them. Simple and robust — no JSON parsing needed.
- **Location resolution:** Overpass API (OpenStreetMap) is used instead of Google Maps — free, no key needed. Requires `User-Agent` header by their ToS.
- **Date parsing:** `dateparser` with a regex pre-pass to strip "this/next" prefixes and time-of-day suffixes that confuse it.
- **No weather yet:** Open-Meteo weather integration is M4 (not started). `tools/weather.py` doesn't exist yet.

---

## Tech Stack

- **UI:** Streamlit (`st.columns`, `st.container(border=True)`, `st.status()`, `st.session_state`)
- **LLM:** `claude-sonnet-4-6` via `anthropic` SDK
- **Web search:** `web_search_20250305` (Anthropic built-in, US-only, requires org admin enablement in Console)
- **Geocoding:** Open-Meteo geocoding API (free, no key)
- **Nearby cities:** Overpass API / OpenStreetMap (free, no key)
- **Weather (M4):** Open-Meteo forecast API (free, no key) — not yet implemented
- **Dependencies:** `streamlit`, `anthropic`, `httpx`, `python-dotenv`, `dateparser`, `pytest`

---

## What to Read for Common Tasks

- **Adding a new feature:** Start with `docs/spec.md` (design) + `docs/todo.md` (checklist)
- **Changing how Claude searches:** `prompts.py` (system prompt, tool schema, user message)
- **Changing the agentic loop / tool handling:** `search.py`
- **Changing location/nearby-city logic:** `location.py`
- **Changing UI layout or form fields:** `app.py`
- **Working on M4 (weather):** Will need new `tools/weather.py` + updates to `prompts.py` and `search.py`
