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
