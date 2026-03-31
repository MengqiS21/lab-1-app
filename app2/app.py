import datetime as dt
import streamlit as st


st.set_page_config(page_title="GIX Wayfinder", page_icon="🧭", layout="centered")

_FRESH_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap');
    html, body, [class*="stApp"] {
        font-family: 'Nunito', system-ui, sans-serif !important;
    }
    html,
    body {
        background-color: #eff6ff !important;
    }
    .stApp {
        background: linear-gradient(165deg, #eff6ff 0%, #f0fdf4 42%, #fffbeb 100%) !important;
        background-attachment: fixed !important;
    }
    /* Avoid a solid white strip under the Streamlit toolbar (header + main chrome) */
    [data-testid="stHeader"],
    [data-testid="stHeader"] > div,
    [data-testid="stToolbar"],
    [data-testid="stToolbar"] > div {
        background: transparent !important;
        background-image: none !important;
        backdrop-filter: none !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > section,
    section[data-testid="stMain"],
    section.main {
        background: transparent !important;
    }
    .main .block-container {
        background-color: transparent !important;
        padding-top: 0.75rem !important;
    }
    div[data-testid="stExpander"] {
        border-radius: 16px !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06) !important;
        margin-bottom: 0.5rem !important;
    }
    div[data-testid="stExpander"] details summary {
        font-weight: 600 !important;
        font-family: 'Quicksand', 'Nunito', sans-serif !important;
        letter-spacing: -0.01em;
        color: #0f172a !important;
    }
    .stMarkdown a { text-underline-offset: 0.15em; }
    /* Keyboard focus: buttons + native fields (Streamlit wraps some controls) */
    .stApp button:focus-visible,
    .stApp input:focus-visible,
    .stApp textarea:focus-visible,
    .stApp select:focus-visible,
    .stApp a:focus-visible {
        outline: 2px solid #0369a1 !important;
        outline-offset: 2px !important;
    }
    .wayfinder-hero h1 {
        font-family: 'Quicksand', sans-serif !important;
        font-size: clamp(1.75rem, 4vw, 2.35rem);
        font-weight: 700;
        letter-spacing: -0.03em;
        margin: 0;
        line-height: 1.15;
        color: #0f172a !important;
        border-bottom: 3px solid #0369a1;
        display: inline-block;
        padding-bottom: 0.15rem;
    }
    .wayfinder-hero p {
        color: #334155;
        margin: 0.45rem 0 0 0;
        font-size: 1.05rem;
    }
</style>
"""
st.markdown(_FRESH_CSS, unsafe_allow_html=True)

st.markdown(
    """
<div class="wayfinder-hero" style="text-align:center; padding: 0.25rem 0 1rem 0;">
  <h1>GIX Wayfinder</h1>
  <p>Explore campus spots — study, make, print, stash your bike, and more.</p>
</div>
""",
    unsafe_allow_html=True,
)


# Varied hours so "Open right now only" usually splits the list (not all open/closed together).
RESOURCES = [
    {
        "name": "Orca Quiet Pods",
        "category": "Study",
        "floor": "2F",
        "hours_open": "07:00",
        "hours_close": "23:30",
        "description": "Small enclosed desks designed for focused solo work.",
        "location_tip": "From the main staircase, turn left and follow signs to the north window corner.",
        "access_notes": "First-come, first-served; keep calls outside.",
        "pro_tip": "Best availability is usually before 10:00.",
        "tags": ["quiet", "focus", "solo", "pods"],
    },
    {
        "name": "Rainier Collaboration Lounge",
        "category": "Study",
        "floor": "1F",
        "hours_open": "08:00",
        "hours_close": "22:00",
        "description": "Open tables with whiteboards for team planning sessions.",
        "location_tip": "Across from the cafe seating area near the digital notice wall.",
        "access_notes": "Group-friendly zone; headphones recommended for deep work.",
        "pro_tip": "Whiteboard markers run out fast in evenings, bring your own.",
        "tags": ["group", "whiteboard", "meeting", "teamwork"],
    },
    {
        "name": "Prototype Garage",
        "category": "Maker",
        "floor": "3F",
        "hours_open": "09:00",
        "hours_close": "18:00",
        "description": "Hands-on makerspace with soldering stations and hand tools.",
        "location_tip": "Take the elevator to 3F and follow the yellow floor stripe.",
        "access_notes": "Safety orientation required for first-time users. Closes when staff leaves.",
        "pro_tip": "Book your orientation early in the quarter.",
        "tags": ["makerspace", "hardware", "soldering", "tools"],
    },
    {
        "name": "Rapid Fab Corner",
        "category": "Maker",
        "floor": "3F",
        "hours_open": "10:00",
        "hours_close": "16:00",
        "description": "Staffed fab window for laser-cutting prep and assembly (not 24/7).",
        "location_tip": "Inside Prototype Garage, right side workbench zone.",
        "access_notes": "Staff approval required before using specialty materials.",
        "pro_tip": "Queue is shortest right at opening; after 16:00 use the self-serve bins only.",
        "tags": ["laser", "fabrication", "assembly", "design files"],
    },
    {
        "name": "Cascade Bike Storage",
        "category": "Storage",
        "floor": "1F",
        "hours_open": "05:30",
        "hours_close": "23:59",
        "description": "Secure indoor bike rack area for commuter students (building access hours).",
        "location_tip": "Near the south entrance, behind the mail lockers.",
        "access_notes": "Student ID tap required; lock your bike even indoors.",
        "pro_tip": "Top rack spots are easiest if you arrive before 09:00.",
        "tags": ["bike", "commute", "rack", "secure"],
    },
    {
        "name": "North Hall Gear Lockers",
        "category": "Storage",
        "floor": "2F",
        "hours_open": "08:00",
        "hours_close": "13:00",
        "description": "Staffed day-use lockers; desk helps with combo issues during morning hours only.",
        "location_tip": "Past the student services desk in the north hallway.",
        "access_notes": "After 13:00 the bay is self-serve grab-and-go only (no new checkouts).",
        "pro_tip": "If you need help resetting a lock, come before noon.",
        "tags": ["locker", "storage", "helmet", "gear"],
    },
    {
        "name": "Cloud Print Hub",
        "category": "Print",
        "floor": "2F",
        "hours_open": "08:00",
        "hours_close": "17:00",
        "description": "Free black-and-white printing while the IT counter is staffed.",
        "location_tip": "Next to the IT help counter, across from elevator B.",
        "access_notes": "Use campus account; daily page limit applies.",
        "pro_tip": "Upload files before peak class-change times.",
        "tags": ["printing", "free", "documents", "it desk"],
    },
    {
        "name": "Poster Plotter Nook",
        "category": "Print",
        "floor": "3F",
        "hours_open": "09:30",
        "hours_close": "17:30",
        "description": "Large-format poster printing for demos and showcases.",
        "location_tip": "Inside the media lab, near the rear glass wall.",
        "access_notes": "Reservation recommended for posters over A1 size.",
        "pro_tip": "Bring PDF with embedded fonts to avoid formatting errors.",
        "tags": ["poster", "plotter", "large format", "media lab"],
    },
    {
        "name": "Harbor Recharge Nook",
        "category": "Other",
        "floor": "1F",
        "hours_open": "17:00",
        "hours_close": "23:00",
        "description": "Evening lounge with soft seating and chargers (opens after cafe peak).",
        "location_tip": "Behind the cafe line, near the indoor plant wall.",
        "access_notes": "Shared charging cables are short; bring your own adapter.",
        "pro_tip": "Best for winding down after classes; before 17:00 use the main atrium seats.",
        "tags": ["charging", "outlets", "seating", "break"],
    },
]


def parse_hhmm(value: str) -> dt.time:
    hour, minute = map(int, value.split(":"))
    return dt.time(hour=hour, minute=minute)


def is_open_now(hours_open: str, hours_close: str, now_time: dt.time) -> bool:
    start = parse_hhmm(hours_open)
    end = parse_hhmm(hours_close)
    if start <= end:
        return start <= now_time <= end
    return now_time >= start or now_time <= end


def ensure_state() -> None:
    defaults = {
        "search_text": "",
        "category_filter": "All",
        "floor_filter": "Any",
        "open_now_only": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_filters() -> None:
    st.session_state.search_text = ""
    st.session_state.category_filter = "All"
    st.session_state.floor_filter = "Any"
    st.session_state.open_now_only = False


ensure_state()

top_left, top_right = st.columns([5, 1])
with top_left:
    st.text_input(
        "Search resources",
        key="search_text",
        placeholder="Try: quiet, bike, printing, whiteboard...",
    )
with top_right:
    st.write("")
    st.write("")
    st.button("Reset", on_click=reset_filters)

f1, f2, f3 = st.columns([2, 2, 2])
with f1:
    st.selectbox(
        "Category",
        ["All", "Study", "Maker", "Storage", "Print", "Other"],
        key="category_filter",
    )
with f2:
    st.radio(
        "Floor",
        ["Any", "1F", "2F", "3F"],
        key="floor_filter",
        horizontal=True,
    )
with f3:
    # Match vertical offset of Category/Floor label row so the checkbox lines up with the inputs.
    st.markdown(
        "<p style='min-height: 1.5rem; margin: 0 0 0.4rem 0; font-size: 0.875rem; line-height: 1.25;'>&nbsp;</p>",
        unsafe_allow_html=True,
    )
    st.checkbox("Open right now only", key="open_now_only")

active_filters = []
if st.session_state.search_text.strip():
    active_filters.append(f"search: {st.session_state.search_text.strip()}")
if st.session_state.category_filter != "All":
    active_filters.append(f"category: {st.session_state.category_filter}")
if st.session_state.floor_filter != "Any":
    active_filters.append(f"floor: {st.session_state.floor_filter}")
if st.session_state.open_now_only:
    active_filters.append("open now only")

if active_filters:
    st.caption("Active filters: " + " · ".join(active_filters))
else:
    st.caption("Active filters: none")

st.divider()

query = st.session_state.search_text.strip().lower()
category_value = st.session_state.category_filter
floor_value = st.session_state.floor_filter
open_now_only = st.session_state.open_now_only
now = dt.datetime.now().time()

results = []
for resource in RESOURCES:
    searchable_blob = " ".join(
        [
            resource["name"],
            resource["description"],
            " ".join(resource.get("tags", [])),
        ]
    ).lower()

    matches_query = (not query) or (query in searchable_blob)
    matches_category = (category_value == "All") or (resource["category"] == category_value)
    matches_floor = (floor_value == "Any") or (resource["floor"] == floor_value)
    open_flag = is_open_now(resource["hours_open"], resource["hours_close"], now)
    matches_open = (not open_now_only) or open_flag

    if matches_query and matches_category and matches_floor and matches_open:
        resource_with_flag = dict(resource)
        resource_with_flag["open_now"] = open_flag
        results.append(resource_with_flag)

st.markdown(
    f'<p style="font-family:Quicksand,sans-serif;font-weight:700;font-size:1.1rem;color:#0f172a;'
    f'margin:0 0 0.75rem 0;">'
    f'<span style="display:inline-block;background:#e0f2fe;color:#0c4a6e;'
    f'padding:0.12rem 0.55rem;border-radius:999px;font-size:0.88rem;font-weight:700;'
    f'border:1px solid #bae6fd;">{len(results)}</span>'
    f"&nbsp;resources found</p>",
    unsafe_allow_html=True,
)

if not results:
    st.markdown(
        """
<div style="background:#ffffff;border-radius:16px;border:2px dashed #94a3b8;
padding:1.35rem 1rem;text-align:center;color:#334155;line-height:1.55;">
  <strong style="color:#0f172a;font-size:1.05rem;">No matches yet</strong><br/>
  <span style="font-size:0.95rem;">Broaden your search or tap <b>Reset</b> to start fresh.</span>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    for item in results:
        header = (
            f"{item['name']} · {item['category']} · {item['floor']} · "
            f"{item['hours_open']}-{item['hours_close']}"
        )
        with st.expander(header, expanded=False):
            if item["open_now"]:
                st.markdown(
                    '<span style="display:inline-block;background:#15803d;'
                    "color:#ffffff;padding:0.2rem 0.65rem;border-radius:999px;font-size:0.82rem;"
                    'font-weight:700;letter-spacing:0.02em;border:1px solid #14532d;">Open now</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span style="color:#475569;font-size:0.9rem;font-weight:600;">Currently closed</span>',
                    unsafe_allow_html=True,
                )
            st.write(f"**Description:** {item['description']}")
            st.write(f"**Location tip:** {item['location_tip']}")
            st.write(f"**Access notes:** {item['access_notes']}")
            if item.get("pro_tip"):
                st.write(f"**Pro tip:** {item['pro_tip']}")
