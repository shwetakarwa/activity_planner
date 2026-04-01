from __future__ import annotations

import re

import anthropic

from prompts import SYSTEM_PROMPT, build_tools, build_user_message


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


def run_search(
    inputs: dict, today_date: str, requested_date: str, cities: list[str]
) -> list[dict]:
    client = anthropic.Anthropic()
    tools = build_tools(inputs["city"])
    user_msg = build_user_message(inputs, today_date, requested_date, cities)
    messages = [{"role": "user", "content": user_msg}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

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

    text = "".join(block.text for block in response.content if hasattr(block, "text"))
    return parse_activities(text)
