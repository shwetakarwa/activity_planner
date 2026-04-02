from __future__ import annotations

import re
from datetime import datetime

import dateparser
import streamlit as st
from dotenv import load_dotenv

from location import find_nearby_cities, get_user_location
from search import run_search

load_dotenv()

st.set_page_config(page_title="Family Activity Finder", layout="wide")


def render_card(rank: int, activity: dict):
    with st.container(border=True):
        num_col, content_col = st.columns([0.07, 0.93])
        with num_col:
            st.markdown(f"### #{rank}")
        with content_col:
            st.markdown(f"### {activity['emoji']} {activity['title']}")
            st.write(activity["description"])
            if activity.get("ages"):
                st.caption(f"👨‍👩‍👧 {activity['ages']}")
            footer = f"📍 {activity['location']} &nbsp;&nbsp; 🚗 {activity['distance']}"
            if activity.get("duration"):
                footer += f" &nbsp;&nbsp; ⏱ {activity['duration']}"
            st.caption(footer)


def validate_inputs(city: str, ages: str, availability: str) -> list[str]:
    errors = []
    if not city.strip():
        errors.append("City is required.")
    if not ages.strip():
        errors.append("Kid Ages is required.")
    if not availability.strip():
        errors.append("Date & Time Availability is required.")
    return errors


def clear_state():
    for key in ["city", "ages", "availability", "miles", "prefs", "parsed_date", "nearby_cities", "activities"]:
        st.session_state.pop(key, None)
    st.session_state["searched"] = False


def parse_date(availability_text: str) -> str | None:
    # dateparser doesn't handle "this/next X" or trailing time-of-day words well; strip them first
    cleaned = re.sub(r"^(this|next)\s+", "", availability_text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+(morning|afternoon|evening|night)$", "", cleaned, flags=re.IGNORECASE)
    result = dateparser.parse(cleaned, settings={"PREFER_DATES_FROM": "future"})
    if result is None:
        return None
    return result.strftime("%Y-%m-%d")


def format_city_list(cities: list[str]) -> str:
    if len(cities) == 1:
        return cities[0]
    if len(cities) == 2:
        return f"{cities[0]} and {cities[1]}"
    return ", ".join(cities[:-1]) + f", and {cities[-1]}"


# --- Page header ---
st.title("🎯 Family Activity Finder")
st.caption("Discover perfect activities for your family")
st.divider()

if "searched" not in st.session_state:
    st.session_state["searched"] = False

# --- Two-column layout ---
form_col, results_col = st.columns([1, 2])

with form_col:
    st.subheader("Find Activities")
    st.caption("Tell us about your family's preferences")

    city = st.text_input("📍 City", key="city", value="San Carlos")
    ages = st.text_input("👨‍👩‍👧 Kid Ages", key="ages", value="2 years")
    availability = st.text_input(
        "📅 Date & Time Availability", key="availability", placeholder="e.g. Sunday afternoon"
    )
    miles = st.slider("🚗 Maximum Distance (miles)", 1, 50, 10, key="miles")
    prefs = st.text_area(
        "✨ Optional Preferences",
        key="prefs",
        placeholder="e.g. indoor activities, educational, budget-friendly",
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        search_clicked = st.button("🔍 Search Activities", type="primary", use_container_width=True)
    with btn_col2:
        st.button("Clear", on_click=clear_state, use_container_width=True)

    if search_clicked:
        errors = validate_inputs(city, ages, availability)
        if errors:
            for msg in errors:
                st.error(msg)
        else:
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

            activities = None
            if parsed:
                now = datetime.now()
                today_str = now.strftime("%A, %B") + f" {now.day}, {now.year}"
                dt = datetime.strptime(parsed, "%Y-%m-%d")
                requested_str = dt.strftime("%A, %B") + f" {dt.day}, {dt.year}"
                inputs_dict = {
                    "city": city,
                    "ages": ages,
                    "availability": availability,
                    "miles": miles,
                    "prefs": prefs,
                }
                with st.status("Searching for events...", expanded=True):
                    try:
                        activities = run_search(inputs_dict, today_str, requested_str, nearby)
                    except Exception as e:
                        st.error(f"Search failed: {e}")

            st.session_state["searched"] = True
            st.session_state["parsed_date"] = parsed
            st.session_state["nearby_cities"] = nearby
            st.session_state["activities"] = activities

with results_col:
    if st.session_state["searched"]:
        parsed_date = st.session_state.get("parsed_date")
        nearby_cities = st.session_state.get("nearby_cities", [city])

        if parsed_date:
            dt = datetime.strptime(parsed_date, "%Y-%m-%d")
            date_str = dt.strftime("%A, %B") + f" {dt.day}"
            st.markdown(f"Here are the events in **{format_city_list(nearby_cities)}** on **{date_str}**.")
        else:
            st.warning("Couldn't understand the date — try 'this Sunday' or 'April 5'.")

        activities = st.session_state.get("activities")
        if activities:
            st.subheader("Top 5 Recommendations")
            st.caption("SORTED BY RELEVANCE")
            for i, activity in enumerate(activities, start=1):
                render_card(i, activity)
    else:
        st.info("Fill in your details and click **Search Activities** to find things to do.")
