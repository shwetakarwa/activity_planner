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

# Milestone 2 — Parse Date & Location, Show on UI

## Setup
- [x] Add `dateparser` to `requirements.txt`

## Date Parsing (`app.py`)
- [x] Add `parse_date(availability_text) -> str | None` using `dateparser.parse()`; return `YYYY-MM-DD` or `None` if unparseable

## Nearby Cities (`app.py`)
- [x] Add `geocode_city(city) -> tuple[float, float]` — fetch lat/lon from `https://geocoding-api.open-meteo.com/v1/search`
- [x] Add `find_nearby_cities(city, miles) -> list[str]` — call `geocode_city`, then query Overpass API with `around:meters,lat,lon`; return city names (include the entered city; deduplicate; cap at 5)
  - Set `User-Agent` header on Overpass requests (required by their ToS)

## UI Confirmation (`app.py`)
- [x] On Search click, call `parse_date()` and `find_nearby_cities()`
- [x] If date parsed: render confirmation above results — `"Here are the events in {cities} on {weekday}, {Month} {day}."`
- [x] If date cannot be parsed: show `st.warning("Couldn't understand the date — try 'this Sunday' or 'April 5'.")`
- [x] Dummy cards still render below as before

## Tests (`tests/test_parse.py`)
- [x] `test_parse_date_this_sunday` — "this Sunday" returns a valid ISO date string
- [x] `test_parse_date_explicit` — "April 5" returns correct date
- [x] `test_parse_date_invalid` — unrecognisable input returns `None`
- [x] `test_find_nearby_cities_includes_entered_city` — entered city always appears in result
- [x] `test_find_nearby_cities_deduplicates` — no duplicate names in result

## Done When
- [x] Submitting "San Carlos" + "this Sunday" + 10 miles shows "Here are the events in San Carlos, Redwood City, and Belmont on Sunday, April 5." above the dummy cards
- [x] Submitting a garbled date shows a warning instead
- [x] All new tests pass

---

# Milestone 3 — Find Activities via Claude Web Search

## Prompts (`prompts.py`)
- [ ] Create `prompts.py`
- [ ] `SYSTEM_PROMPT`: TIMELY + AGE-APPROPRIATE prioritization criteria; `---ACTIVITY---`/`---END---` delimiters with fields EMOJI, TITLE, DESCRIPTION, LOCATION, DISTANCE, AGES, DURATION; rules (no invented events, cite sources)
- [ ] `build_user_message(inputs, today_date, requested_date, cities) -> str` — format user message with pre-resolved cities list
- [ ] `TOOLS`: list with only `web_search_20250305` (type, name, max_uses=8, user_location filled at runtime)

## Agentic Loop (`app.py`)
- [ ] Add `run_search(inputs, today_date, requested_date, cities)`:
  - [ ] Build initial messages list and call `anthropic.messages.create` with `SYSTEM_PROMPT`, user message, `TOOLS`
  - [ ] Handle `tool_use` stop_reason: extract `encrypted_content` from each search result, append `tool_result` block, continue loop
  - [ ] Loop until `stop_reason == "end_turn"`
  - [ ] Parse `---ACTIVITY---`/`---END---` blocks from final response text; return list of activity dicts
- [ ] On Search click, pass `cities` from `st.session_state["nearby_cities"]` + resolved dates into `run_search`
- [ ] Replace dummy cards with real parsed results
- [ ] Wrap in `st.status()` spinner with label "Searching for events..."

## Tests (`tests/test_prompts.py`)
- [ ] `test_build_user_message_includes_cities` — cities list appears in the returned string
- [ ] `test_build_user_message_includes_dates` — today_date and requested_date appear in the returned string
- [ ] `test_parse_activities_basic` — correctly parses a single well-formed `---ACTIVITY---` block
- [ ] `test_parse_activities_count` — parses exactly 5 blocks from a full Claude response

## Done When
- [ ] "San Carlos, 2 years, this Sunday, 10 miles" returns 5 real upcoming events across San Carlos, Redwood City, and Belmont with actual dates/times in titles
- [ ] All new tests pass
