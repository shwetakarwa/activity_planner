# Plan: Geolocation-Based City Disambiguation

## Context

When a user types a common city name like "Dublin", "Springfield", or "Portland", `geocode_city()` in `location.py` takes the **first result** from Open-Meteo's API (`count=1`). Open-Meteo sorts by population, so it may return the wrong city (Dublin, Ireland instead of Dublin, CA).

The fix uses two disambiguation signals in priority order:
1. **Explicit state/country qualifier** (`"Dublin, CA"`) — user was unambiguous → trust it directly
2. **IP-based location hint** (`"Dublin"`) — pick the candidate closest to the user's approximate location

---

## Changes

### 1. `location.py` — three coordinated changes

**Add `get_user_location(ip)`** (new function, after `_haversine_miles`):
```python
def get_user_location(ip: str | None = None) -> tuple[float, float] | None:
```
- Returns `None` immediately if `ip` is falsy (no HTTP call)
- Calls `https://ipapi.co/{ip}/json/` with `timeout=5`
- Returns `None` if response contains `"error"` key (private IPs, invalid, etc.)
- Returns `(data["latitude"], data["longitude"])` on success
- Entire body wrapped in `try/except Exception` → returns `None` on any failure

**Modify `geocode_city(city, hint_lat=None, hint_lon=None)`**:
- If `city` contains a comma (e.g. `"Dublin, CA"`, `"Portland, OR"`), the user was explicit → use `"count": 1` and return `results[0]` directly (no hint needed)
- Otherwise, use `"count": 5` and if `hint_lat`/`hint_lon` are provided AND `len(results) > 1`, use `_haversine_miles()` (already exists) to pick the closest candidate
- Falls back to `results[0]` when no hint is available (backward-compatible)

**Modify `find_nearby_cities(city, miles, hint_lat=None, hint_lon=None)`**:
- Pass `hint_lat` and `hint_lon` through to `geocode_city()`
- Only the first line of the function body changes

### 2. `app.py` — two changes

**Update import** (line 10):
```python
from location import find_nearby_cities, get_user_location
```

**Update search handler** (around lines 108–112):
```python
parsed = parse_date(availability)
user_ip = (st.context.ip_address or "").strip()
hint = get_user_location(user_ip)
try:
    if hint:
        nearby = find_nearby_cities(city, miles, hint_lat=hint[0], hint_lon=hint[1])
    else:
        nearby = find_nearby_cities(city, miles)
except Exception:
    nearby = [city]
```

> `st.context.ip_address` is Streamlit's first-class property for the client IP (available since 1.31+). Returns `None` for localhost/loopback, which causes `get_user_location` to skip the HTTP call and fall back gracefully.

### 3. `tests/test_parse.py` — new tests

| Test | What it verifies |
|---|---|
| `test_geocode_city_explicit_qualifier_skips_hint` | City with comma (`"Dublin, CA"`) uses `count=1`, ignores hint entirely |
| `test_geocode_city_uses_hint_to_pick_closest` | Two candidates (Dublin CA vs Dublin IE); Bay Area hint picks CA one |
| `test_geocode_city_no_hint_uses_first_result` | Two candidates, no hint → returns first result |
| `test_geocode_city_single_result_ignores_hint` | One candidate + distant hint → single result returned, no crash |
| `test_find_nearby_cities_passes_hint_through` | End-to-end: hint is accepted, city is included in result |
| `test_get_user_location_success` | Happy path: returns `(lat, lon)` |
| `test_get_user_location_none_ip` | `None` IP → `None` returned, no HTTP call made |
| `test_get_user_location_error_response` | ipapi.co error key → `None` returned |
| `test_get_user_location_network_failure` | `httpx.RequestError` raised → `None` returned |

---

## No New Dependencies

`httpx` is already used; `ipapi.co` is a free, no-key-required API. `st.context.ip_address` is built into Streamlit.

---

## Graceful Degradation

| Scenario | Behavior |
|---|---|
| `st.context.ip_address` is `None` (local dev) | `get_user_location("")` returns `None`; `geocode_city` uses `results[0]` |
| ipapi.co unreachable / slow | `timeout=5` + broad `except` → returns `None` |
| ipapi.co rate limited (HTTP 429) | `raise_for_status()` caught → returns `None` |
| User on VPN | hint may be wrong, but worst case is same as today (first result) |
| Open-Meteo returns 1 result | hint logic skipped, `results[0]` returned |
| Open-Meteo returns 0 results | existing `raise ValueError` unchanged |

---

## Verification

1. `pytest tests/` — all existing + new tests pass
2. Search `"Dublin"` (no qualifier) — resolves to Dublin, CA for Bay Area users
3. Search `"Dublin, CA"` — resolves correctly regardless of IP
4. Search `"Dublin, Ireland"` — resolves correctly regardless of IP
5. Search `"Springfield"` — picks the Springfield closest to the user
6. Disconnect from internet → `get_user_location` fails silently, app still works
