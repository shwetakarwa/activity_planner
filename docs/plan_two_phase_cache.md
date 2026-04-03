# Plan: Two-Phase Search + SQLite Cache

## Context

Every search currently runs a single Claude call that bundles web search + ranking together. This means:
- Re-adding preferences → full re-search (same cities, web search fires again)
- Repeating the same search → full re-search ($0 savings)

The fix: split into **gather** (expensive, cached) and **rank** (cheap, no web search). Prefs-only changes skip Phase 1 entirely. Repeated searches cost nothing.

---

## Architecture

```
Phase 1 — Gather (cached per cities + ages + date)
  Input:  cities[], ages, date_iso
  Tools:  web_search (max_uses=3, reduced from 5)
  Model:  claude-sonnet-4-6
  Output: raw events text (all found events, unfiltered)
  Cache:  SQLite keyed by SHA256(sorted_cities|ages_norm|date_iso)

Phase 2 — Rank (runs every search, no web search)
  Input:  raw events text + prefs + ages
  Tools:  none
  Model:  claude-haiku-4-5-20251001
  Output: top 5 activities in ---ACTIVITY--- format
  Cache:  none (fast + cheap to skip)
```

**Cost profile for common usage patterns:**

| Scenario | Current | After |
|---|---|---|
| Same search again | Full API call | ~$0 (cache hit) |
| Same cities + new/changed prefs | Full API call | Phase 2 only (~$0.002) |
| Expand miles (new cities) | Full API call | Phase 1 re-runs + Phase 2 |
| First-time search | Full API call | Same cost, but now cached |

> Prompt text for both phases is in `docs/prompt.md` under "Milestone 4 — Two-Phase Search".

---

## Files to Create/Modify

| File | Change |
|---|---|
| `cache.py` | **New** — SQLite cache module |
| `prompts.py` | Replace single prompt with gather + rank prompt pairs |
| `search.py` | Split `run_search()` into `gather_events()` + `rank_events()` + `run_search()` |
| `app.py` | Pass `date_iso` to `run_search()`; update spinner labels; call `purge_old_entries()` on startup |
| `.gitignore` | Add `.activity_cache.db` |

### `cache.py` public API

```python
make_cache_key(cities: list[str], ages: str, date_iso: str) -> str
get_cached_events(cache_key: str, date_iso: str) -> str | None   # None if past date
store_events(cache_key: str, cities: list[str], ages: str, date_iso: str, raw_events: str) -> None
purge_old_entries() -> None  # removes entries where date_iso < today
```

SQLite schema:
```sql
CREATE TABLE IF NOT EXISTS event_cache (
    cache_key   TEXT PRIMARY KEY,
    cities      TEXT,
    ages        TEXT,
    date_iso    TEXT,
    raw_events  TEXT,
    created_at  TEXT
)
```

DB file: `.activity_cache.db` at project root (gitignored).

---

## Tests

### `tests/test_cache.py` (new)
- `test_cache_miss_returns_none` — key with no entry returns None
- `test_cache_store_and_retrieve` — store then get returns the same value
- `test_cache_expired_for_past_date` — entry with yesterday's date returns None
- `test_cache_key_order_independent` — `["A","B"]` and `["B","A"]` produce the same key

### `tests/test_search.py` (new)
- `test_run_search_hits_cache_on_second_call` — verify gather is not re-called on repeat
- `test_gather_events_stores_result` — result stored in cache after a miss
- `test_rank_events_uses_haiku` — verify `claude-haiku-4-5-20251001` is used in Phase 2

---

## Implementation Tasks

Divided into 4 parts so each can be reviewed independently before moving to the next.

### Part 1 — Cache module (self-contained, no existing code touched)
- [ ] Create `cache.py` with `make_cache_key`, `get_cached_events`, `store_events`, `purge_old_entries`
- [ ] Add `.activity_cache.db` to `.gitignore`
- [ ] Create `tests/test_cache.py` with all 4 cache tests
- [ ] Run `pytest tests/test_cache.py` — all pass

### Part 2 — Prompts refactor (text changes only, no behavior change yet)
- [ ] Replace `SYSTEM_PROMPT` + `build_user_message` in `prompts.py` with `GATHER_SYSTEM_PROMPT`, `build_gather_message`, `RANK_SYSTEM_PROMPT`, `build_rank_message`
- [ ] Reduce `max_uses` from 5 → 3 in `build_tools()`
- [ ] Update `tests/test_prompts.py` — rename tests to match new function names, verify cities/dates still appear in gather message
- [ ] Run `pytest tests/test_prompts.py` — all pass

### Part 3 — Search refactor (core logic, wires cache + two-phase loop)
- [ ] Split `run_search()` in `search.py` into `gather_events()`, `rank_events()`, and updated `run_search(inputs, today_str, requested_str, cities, date_iso)`
- [ ] `gather_events()` checks cache first; stores result on miss
- [ ] `rank_events()` uses `claude-haiku-4-5-20251001`, no tools
- [ ] Create `tests/test_search.py` with all 3 search tests
- [ ] Run `pytest tests/test_search.py` — all pass

### Part 4 — App integration (UI wiring only)
- [ ] Pass `st.session_state["parsed_date"]` as `date_iso` when calling `run_search()` in `app.py`
- [ ] Call `cache.purge_old_entries()` once on app startup
- [ ] Update `st.status()` label: cache hit → `"Ranking activities (from cache)..."`, miss → `"Searching for events..."`
- [ ] Run full `pytest tests/` — all pass
- [ ] Manual smoke test (see Verification below)

---

## Verification

1. `streamlit run app.py`
2. Search "San Carlos, 2 years, this Sunday, 10 miles" — cache miss, calls Claude, returns 5 results
3. Add pref "indoor", search again — spinner says "Ranking activities (from cache)...", fast return
4. Repeat the exact first search — instant return from cache
5. `pytest tests/` — all tests pass
6. Confirm `.activity_cache.db` exists with one row
