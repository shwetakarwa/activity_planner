from __future__ import annotations

import re
import time

import anthropic

_RETRY_DELAYS = [5, 10, 20]  # seconds between attempts 1→2, 2→3, 3→4


def _create_with_retry(client: anthropic.Anthropic, **kwargs) -> anthropic.types.Message:
    """Call messages.create, retrying up to 3 times on 529 overloaded errors."""
    for i, delay in enumerate([0] + _RETRY_DELAYS):
        if delay:
            time.sleep(delay)
        try:
            return client.messages.create(**kwargs)
        except anthropic.APIStatusError as e:
            if e.status_code == 529 and i < len(_RETRY_DELAYS):
                continue
            raise

from cache import get_cached_events, make_cache_key, store_events
from prompts import (
    GATHER_SYSTEM_PROMPT,
    RANK_SYSTEM_PROMPT,
    build_gather_message,
    build_rank_message,
    build_tools,
)


def parse_activities(text: str) -> list[dict]:
    blocks = re.findall(r"---ACTIVITY---(.*?)---END---", text, re.DOTALL)
    activities = []
    for block in blocks:
        activity = {}
        for m in re.finditer(r"^([A-Z]+):\s*(.*?)(?=\n[A-Z]+:|\Z)", block, re.MULTILINE | re.DOTALL):
            activity[m.group(1).lower()] = m.group(2).strip()
        if activity:
            activities.append(activity)
    return activities


def _run_agentic_loop(
    client: anthropic.Anthropic,
    model: str,
    system: str,
    user_msg: str,
    tools: list | None = None,
) -> str:
    """Run a Claude agentic loop and return the final text response."""
    messages = [{"role": "user", "content": user_msg}]
    kwargs: dict = {"model": model, "max_tokens": 4096, "system": system, "messages": messages}
    if tools:
        kwargs["tools"] = tools

    while True:
        response = _create_with_retry(client, **kwargs)

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            # For web_search_20250305, search results (including encrypted_content)
            # are returned by Anthropic's servers in block.content — echo them back
            # as tool_result so Claude can continue with additional searches.
            tool_results = [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": block.content,
                }
                for block in response.content
                if block.type == "tool_use"
            ]
            messages.append({"role": "user", "content": tool_results})
            kwargs["messages"] = messages

    return "".join(block.text for block in response.content if hasattr(block, "text"))


def gather_events(
    cities: list[str],
    ages: str,
    date_iso: str,
    today_date: str,
    requested_date: str,
    city: str,
) -> tuple[str, bool]:
    """Phase 1: find events via web search, with SQLite caching.

    Returns (raw_events_text, from_cache).
    """
    key = make_cache_key(cities, ages, date_iso)
    cached = get_cached_events(key, date_iso)
    if cached:
        return cached, True

    client = anthropic.Anthropic()
    tools = build_tools(city)
    user_msg = build_gather_message(cities, ages, today_date, requested_date)
    raw_events = _run_agentic_loop(
        client, "claude-sonnet-4-6", GATHER_SYSTEM_PROMPT, user_msg, tools
    )
    store_events(key, cities, ages, date_iso, raw_events)
    return raw_events, False


def rank_events(
    raw_events: str, inputs: dict, requested_date: str
) -> list[dict]:
    """Phase 2: rank gathered events using Haiku (no web search)."""
    client = anthropic.Anthropic()
    user_msg = build_rank_message(raw_events, inputs, requested_date)
    text = _run_agentic_loop(
        client, "claude-haiku-4-5-20251001", RANK_SYSTEM_PROMPT, user_msg
    )
    return parse_activities(text)


def run_search(
    inputs: dict,
    today_date: str,
    requested_date: str,
    cities: list[str],
    date_iso: str,
) -> tuple[list[dict], bool]:
    """Entry point: gather (cached) then rank.

    Returns (activities, from_cache) so the caller can update the UI label.
    """
    raw_events, from_cache = gather_events(
        cities, inputs["ages"], date_iso, today_date, requested_date, inputs["city"]
    )
    activities = rank_events(raw_events, inputs, requested_date)
    return activities, from_cache
