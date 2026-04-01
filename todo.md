# Milestone 1 — Streamlit UI with Dummy Data ✅

## Setup
- [x] Create `requirements.txt` with `streamlit`, `anthropic`, `httpx`, `python-dotenv`, `pytest`
- [x] Create `.gitignore` — exclude `.env` and `__pycache__/`

## App (`app.py`)
- [x] Two-column layout via `st.columns([1, 2])`
- [x] Left column — form inputs:
  - [x] City (`st.text_input`)
  - [x] Kid Ages (`st.text_input`)
  - [x] Date & Time Availability (`st.text_input`)
  - [x] Max Distance (`st.slider`, 1–50 miles)
  - [x] Optional Preferences (`st.text_area`)
  - [x] "Search Activities" button + "Clear" button
- [x] Right column — results panel:
  - [x] "Top 5 Recommendations" header
  - [x] On Search click: render 5 hardcoded dummy activity cards
  - [x] Each card: `st.container(border=True)` with emoji, bold title + time, description, 📍 location + 🚗 distance footer
  - [x] Clear resets all inputs and hides cards (`st.session_state`)

## Tests (`tests/test_app.py`)
- [x] `test_dummy_activities_count` — confirms exactly 5 activities
- [x] `test_dummy_activities_have_required_keys` — confirms all required fields present
- [x] `test_dummy_activities_no_empty_fields` — confirms no blank values

---

# Milestone 2 — Live Claude API + Web Search + Weather

## Setup
- [ ] Create `.env` with `ANTHROPIC_API_KEY=...`
- [ ] Add `dateparser` to `requirements.txt` (natural language date parsing: "this Sunday" → date)
- [ ] Confirm web search is enabled for your org in the Anthropic Console (one-time admin step)

## Weather Tool (`tools/weather.py` + `tools/__init__.py`)
- [ ] Create `tools/__init__.py` (empty, makes tools/ a package)
- [ ] Geocode city → lat/lon via `https://geocoding-api.open-meteo.com/v1/search`
- [ ] Fetch forecast via `https://api.open-meteo.com/v1/forecast` for the requested date
- [ ] Return dict: `{date, temp_high_f, temp_low_f, condition, suitable_for_outdoor}`
- [ ] Test: `tests/test_weather.py` — mock HTTP calls, verify output shape and F conversion

## Prompts (`prompts.py`)
- [ ] `SYSTEM_PROMPT` — seasonal/timely priority order, output delimiter format (`---ACTIVITY---` / `---END---`), citation requirement
- [ ] `build_user_message(inputs, today_date, requested_date)` — fills placeholders from `prompt.md`
- [ ] `TOOLS` list — `web_search_20250305` (Anthropic server tool, no custom code) + `get_weather` schema
- [ ] Test: `tests/test_prompts.py` — verify user message contains city, dates, and miles

## Agentic Loop (`app.py`)
> Note: `web_search_20250305` is a server-side tool — Anthropic handles search internally and
> returns results as `web_search_tool_result` blocks. Our loop only needs to handle `get_weather`.
> Use non-streaming `messages.create` per iteration (simpler than streaming mid-loop);
> show `st.status()` spinners for UX feedback while waiting.

- [ ] `parse_date(availability_text)` — use `dateparser` to convert free text → `YYYY-MM-DD`
- [ ] `run_search(inputs)` function:
  - [ ] Build messages list with user message from `prompts.py`
  - [ ] Loop: call `client.messages.create(tools=TOOLS, ...)`
    - [ ] `stop_reason == "tool_use"` → find `get_weather` tool_use block → call `tools/weather.py` → append tool_result → continue
    - [ ] `stop_reason == "end_turn"` → extract text → parse `---ACTIVITY---` blocks → return list of card dicts
- [ ] Replace dummy cards with real cards from `run_search()`
- [ ] Wrap call in `with st.status("Finding activities...")` to show progress

## Done When
- [ ] "San Carlos, 2 years, this Sunday, 10 miles" returns 5 real upcoming events
- [ ] Activity titles include specific real dates and times
- [ ] Weather note in descriptions reflects actual Open-Meteo forecast for that city/day
- [ ] All new tests pass
