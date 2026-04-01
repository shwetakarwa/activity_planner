import streamlit as st

st.set_page_config(page_title="Family Activity Finder", layout="wide")

DUMMY_ACTIVITIES = [
    {
        "emoji": "🚃",
        "title": "Muni Heritage Weekend - Sunday 10am–4pm",
        "description": (
            "A special event where families can ride vintage transit vehicles rarely seen on "
            "San Francisco streets, including vintage buses and the Blackpool Boat Tram. "
            "All rides on these special streetcars are FREE all weekend. Perfect for a cool, "
            "partly cloudy day like today — no sun required!"
        ),
        "location": "San Francisco Railway Museum",
        "distance": "0.5 miles",
    },
    {
        "emoji": "🇬🇷",
        "title": "Greek Food Festival - Sunday 11am–8pm",
        "description": (
            "The annual Greek Food Festival features delicious traditional food like Spanakopita "
            "and Moussaka, plus desserts and Greek wine. Visitors can enjoy classic Greek music, "
            "watch award-winning folk dance groups perform, and browse unique gifts from local vendors. "
            "Mostly outdoors — great if the afternoon clears up."
        ),
        "location": "Mission District",
        "distance": "1.2 miles",
    },
    {
        "emoji": "🎨",
        "title": "Sunday Funnies Exhibit - Sunday 10am–5pm",
        "description": (
            "The Cartoon Art Museum's 40th anniversary showcase features classic comic strips "
            "from the dawn of the comics medium to the present day, including works from legendary "
            "cartoonists like Charles M. Schulz (Peanuts) and contemporary classics like Phoebe and "
            "Her Unicorn. A great indoor option if the marine layer sticks around."
        ),
        "location": "Cartoon Art Museum",
        "distance": "2 miles",
    },
    {
        "emoji": "💃",
        "title": "Lindy in the Park Dance Party - Sunday 11am–2pm",
        "description": (
            "A weekly free swing dance event near the de Young Museum when the streets of Golden Gate "
            "Park are closed to traffic. Get ready to swing in Golden Gate Park at this family-friendly "
            "dance gathering — kids love watching the dancers. Best enjoyed on a sunny Sunday."
        ),
        "location": "Golden Gate Park",
        "distance": "3.1 miles",
    },
    {
        "emoji": "🦁",
        "title": "San Francisco Zoo - Open Sunday 10am–5pm",
        "description": (
            "The SF Zoo is home to over 2,000 animals including grizzly bears, African penguins, "
            "and the new lemur forest exhibit. The children's zoo area has hands-on animal encounters "
            "ideal for younger kids. Mild temperatures make this a comfortable all-day outing."
        ),
        "location": "San Francisco Zoo",
        "distance": "7.4 miles",
    },
]


def render_card(rank: int, activity: dict):
    with st.container(border=True):
        num_col, content_col = st.columns([0.07, 0.93])
        with num_col:
            st.markdown(f"### #{rank}")
        with content_col:
            st.markdown(f"### {activity['emoji']} {activity['title']}")
            st.write(activity["description"])
            st.caption(f"📍 {activity['location']} &nbsp;&nbsp; 🚗 {activity['distance']}")


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
    for key in ["city", "ages", "availability", "miles", "prefs"]:
        st.session_state.pop(key, None)
    st.session_state["searched"] = False


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
            st.session_state["searched"] = True

with results_col:
    if st.session_state["searched"]:
        st.subheader("Top 5 Recommendations")
        st.caption("SORTED BY RELEVANCE")
        for i, activity in enumerate(DUMMY_ACTIVITIES, start=1):
            render_card(i, activity)
    else:
        st.info("Fill in your details and click **Search Activities** to find things to do.")
