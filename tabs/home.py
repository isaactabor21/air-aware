"""
Home Tab — Air Aware
====================
Search form with full Milestone 3 adaptive interactivity:
  - Dynamic UI: trip type radio shows/hides return date (1);
                "Advanced Options" expander shows airline + class filters (2)
  - Widget keys: all interactive widgets have key= with comments on 3+
  - Callbacks: on_click reset button; on_change origin clears airline selection
  - Dependent dropdowns: airline list updates based on selected origin airport
"""

import streamlit as st
from datetime import date, timedelta
from data import ALL_AIRPORTS, get_airlines_for_origin, fetch_live_flights, flights_data
from navigation import start_view_transition

RESULTS_FILTER_DEFAULTS = {
    "risk_filter_select": "All",
    "time_filter_select": "All",
    "price_filter_select": "All",
    "sort_by_select": "On-Time Probability",
    "results_airline_filter": "All Airlines",
}


# =============================================================================
# CALLBACKS
# =============================================================================

def reset_search():
    """
    on_click callback: resets all search filters and results.
    A callback is needed here (not just an if-block) because we must clear
    multiple independent session_state keys atomically before re-render.
    """
    st.session_state.search_completed = False
    st.session_state.search_params = {}
    st.session_state.selected_flight = None
    st.session_state.flight_selected = False
    st.session_state.live_flights = None
    st.session_state.airline_filter = "All Airlines"
    st.session_state.active_view = "home"
    for key, value in RESULTS_FILTER_DEFAULTS.items():
        st.session_state[key] = value
    st.toast("🔄 Search cleared!", icon="✅")


def on_origin_change():
    """
    on_change callback: when origin changes, reset the dependent airline
    dropdown so stale selections from the previous origin don't carry over.
    Without this, a user who had 'Alaska Airlines' selected for LAX would
    see a broken selection after switching to MSP (where Alaska doesn't fly).
    """
    st.session_state.airline_filter = "All Airlines"


def reset_results_filters():
    for key, value in RESULTS_FILTER_DEFAULTS.items():
        st.session_state[key] = value


def sync_search_widgets(search_params):
    origin = search_params.get("origin", "MSP")
    if origin not in ALL_AIRPORTS:
        origin = ALL_AIRPORTS[0]

    destination_options = [airport for airport in ALL_AIRPORTS if airport != origin]
    destination = search_params.get("destination", destination_options[0] if destination_options else origin)
    if destination_options and destination not in destination_options:
        destination = destination_options[0]

    departure_date = search_params.get("departure_date", date.today() + timedelta(days=7))
    return_date = search_params.get("return_date") or (departure_date + timedelta(days=7))

    available_airlines = ["All Airlines"] + get_airlines_for_origin(origin)
    preferred_airline = search_params.get("preferred_airline", "All Airlines")
    if preferred_airline not in available_airlines:
        preferred_airline = "All Airlines"

    st.session_state.trip_type_radio = search_params.get("trip_type", "One-Way")
    st.session_state.origin_select = origin
    st.session_state.destination_select = destination
    st.session_state.departure_date_input = departure_date
    st.session_state.return_date_input = return_date
    st.session_state.passengers_select = search_params.get("passengers", "1 Adult")
    st.session_state.airline_filter = preferred_airline
    st.session_state.cabin_class_select = search_params.get("cabin_class", "Economy")


def make_recent_search_record(search_params):
    label = (
        f"{search_params['origin']} → {search_params['destination']} — "
        f"{search_params['departure_date'].strftime('%b %d')}"
    )
    return {
        "label": label,
        "params": dict(search_params),
    }


def save_recent_search(search_params):
    record = make_recent_search_record(search_params)
    recent = st.session_state.get("recent_searches", [])
    deduped = [
        item for item in recent
        if not isinstance(item, dict) or item.get("label") != record["label"]
    ]
    deduped.insert(0, record)
    st.session_state.recent_searches = deduped[:5]


def execute_search(search_params, save_recent=True):
    st.session_state.search_params = search_params
    st.session_state.selected_flight = None
    st.session_state.flight_selected = False
    reset_results_filters()

    live = fetch_live_flights(search_params["origin"], search_params["destination"])

    if live is None or len(live) == 0:
        st.session_state.live_flights = flights_data
    else:
        st.session_state.live_flights = live

    if save_recent:
        save_recent_search(search_params)

    st.session_state.search_completed = True


def render_recent_searches():
    with st.expander("Recent Searches", expanded=False):
        st.caption("Re-run a recent route and restore the last search details.")
        recent = st.session_state.get("recent_searches", [])
        if recent:
            for i, search in enumerate(recent):
                record = search if isinstance(search, dict) else {"label": str(search), "params": None}
                if st.button(f"🔄 {record['label']}", key=f"recent_{i}"):
                    if record.get("params"):
                        st.toast(f"Re-running {record['label']}", icon="✈️")
                        start_view_transition(
                            "results",
                            "Re-loading your saved flight options...",
                            action="search_flights",
                            payload={"search_params": record["params"], "save_recent": False},
                        )
                    else:
                        start_view_transition("results", "Opening your saved flight options...")
        else:
            st.info("No recent searches yet. Your searches will appear here.")


# =============================================================================
# RENDER
# =============================================================================

def render():
    st.subheader("Search Flights")
    st.caption("Choose a route and we will take you straight to the flight options that match.")

    # ── Step indicator (user feedback: multi-step workflow tracker) ──────────
    step = 1
    if st.session_state.get("search_completed"):
        step = 2
    if st.session_state.get("selected_flight"):
        step = 3

    st.markdown(
        f"""
        <div style="display:flex; gap:10px; margin-bottom:16px; align-items:center; flex-wrap:wrap;">
            {''.join([
                f'<span style="background:{"#13233a" if i+1 <= step else "#0d1117"};'
                f'border:1px solid {"#1f6feb66" if i+1 <= step else "#30363d"};'
                f'color:{"#e6edf3" if i+1 <= step else "#8b949e"};'
                f'padding:6px 14px; border-radius:20px; font-size:0.82rem; font-weight:600;">'
                f'{"✓" if i+1 < step else str(i+1)} {label}</span>'
                for i, label in enumerate(["Search", "Select Flight", "View Risk"])
            ])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Trip Type (Dynamic UI #1: shows/hides return date field) ─────────────
    st.markdown("### Trip Type")
    trip_type = st.radio(
        "Select trip type:",
        ["One-Way", "Round-Trip", "Multi-City"],
        horizontal=True,
        label_visibility="collapsed",
        key="trip_type_radio",  # key= ensures reset callback can target this widget
    )

    # ── Origin / Destination — OUTSIDE the form so on_change callback is allowed.
    # Streamlit forbids callbacks on widgets inside st.form (only form_submit_button
    # may have a callback inside a form). We place these here and read their values
    # from session_state inside the form below.
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**From:**")
        origin = st.selectbox(
            "Origin Airport",
            ALL_AIRPORTS,
            index=ALL_AIRPORTS.index("MSP") if "MSP" in ALL_AIRPORTS else 0,
            label_visibility="collapsed",
            key="origin_select",      # key= lets on_change and reset_search target this widget;
                                      # without a stable key Streamlit can't identify it across reruns
            on_change=on_origin_change,  # clears dependent airline dropdown when origin changes
        )

    with col2:
        st.markdown("**To:**")
        dest_options = [a for a in ALL_AIRPORTS if a != origin]
        destination = st.selectbox(
            "Destination Airport",
            dest_options,
            label_visibility="collapsed",
            key="destination_select",
        )

    # ── Advanced Options (Dynamic UI #2) — also outside form so airline dropdown
    # can react immediately to origin changes without needing a form submit.
    with st.expander("⚙️ Advanced Options"):
        adv_col1, adv_col2 = st.columns(2)
        with adv_col1:
            # Dependent dropdown: options come from origin via get_airlines_for_origin().
            # on_origin_change() resets airline_filter in session_state so this widget
            # re-renders with the correct options whenever the origin changes.
            available_airlines = ["All Airlines"] + get_airlines_for_origin(origin)
            preferred_airline = st.selectbox(
                "Preferred Airline",
                available_airlines,
                key="airline_filter",  # key= is essential: reset_search() and on_origin_change()
                                       # both write to this key to clear the selection
            )
        with adv_col2:
            cabin_class = st.selectbox(
                "Cabin Class",
                ["Economy", "Premium Economy", "Business", "First"],
                key="cabin_class_select",
            )

    # ── Main Search Form (dates + passengers + submit) ────────────────────────
    with st.form("flight_search_form"):

        # Date row — return date only appears for Round-Trip (Dynamic UI #1 continued)
        if trip_type == "Round-Trip":
            col3, col4, col5 = st.columns(3)
        else:
            col3, col5 = st.columns(2)

        with col3:
            st.markdown("**Departure Date:**")
            departure_date = st.date_input(
                "Departure",
                min_value=date.today(),
                value=date.today() + timedelta(days=7),
                label_visibility="collapsed",
                key="departure_date_input",  # key= required so reset_search() can target it
                                              # and return date min_value stays in sync
            )

        return_date = None
        if trip_type == "Round-Trip":
            with col4:
                st.markdown("**Return Date:**")
                return_date = st.date_input(
                    "Return",
                    min_value=departure_date + timedelta(days=1),
                    value=departure_date + timedelta(days=7),
                    label_visibility="collapsed",
                    key="return_date_input",
                )

        with col5:
            st.markdown("**Passengers:**")
            passengers = st.selectbox(
                "Passengers",
                ["1 Adult", "2 Adults", "3 Adults", "4 Adults", "5+ Adults"],
                label_visibility="collapsed",
                key="passengers_select",
            )

        # ── Validation + Submit ───────────────────────────────────────────────
        search_submitted = st.form_submit_button("🔍 Search Flights")

        if search_submitted:
            # Input validation: same origin & destination
            if origin == destination:
                st.error("⚠️ Origin and destination cannot be the same airport.")
                st.stop()

            # Input validation: return date must be after departure (extra guard)
            if trip_type == "Round-Trip" and return_date and return_date <= departure_date:
                st.error("⚠️ Return date must be after your departure date.")
                st.stop()

            # Input validation: departure must be today or future
            if departure_date < date.today():
                st.error("⚠️ Departure date cannot be in the past.")
                st.stop()

            # All good — save params and fetch
            search_params = {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "trip_type": trip_type,
                "preferred_airline": preferred_airline,
                "cabin_class": cabin_class,
            }
            start_view_transition(
                "results",
                "Searching flights and preparing your options...",
                action="search_flights",
                payload={"search_params": search_params, "save_recent": True},
            )

    # ── Reset Button (on_click callback) ─────────────────────────────────────
    if st.session_state.get("search_completed"):
        st.button(
            "🗑️ Reset Search",
            on_click=reset_search,
            key="reset_btn",
            help="Clears all filters and search results",
        )

    # ── Recent Searches ───────────────────────────────────────────────────────
    st.markdown("---")
    render_recent_searches()
    return
    st.markdown("### Recent Searches")
    st.caption("*Click to quickly re-run a past search*")

    recent = st.session_state.get("recent_searches", [])
    if recent:
        for i, search in enumerate(recent):
            if st.button(f"🔄 {search}", key=f"recent_{i}"):  # key= prevents widget ID
                                                                # collision across re-renders
                st.session_state.search_completed = True
                st.session_state.active_view = "results"
                st.info(f"Re-searching: {search}")
                st.rerun()
    else:
        st.info("No recent searches yet. Your searches will appear here.")
