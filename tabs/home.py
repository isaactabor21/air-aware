import streamlit as st
from datetime import date, timedelta

def render():
    st.subheader("Home & Search")
    
    # Trip Type Selection
    st.markdown("### Trip Type")
    trip_type = st.radio(
        "Select trip type:",
        ["One-Way", "Round-Trip", "Multi-City"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Flight Search Form
    with st.form("flight_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**From:**")
            origin = st.text_input(
                "Origin",
                placeholder="DCA - Washington D.C.",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**To:**")
            destination = st.text_input(
                "Destination",
                placeholder="MSP - Minneapolis Saint Paul",
                label_visibility="collapsed"
            )
        
        # Adjust columns based on trip type
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
                label_visibility="collapsed"
            )
        
        if trip_type == "Round-Trip":
            with col4:
                st.markdown("**Return Date:**")
                return_date = st.date_input(
                    "Return",
                    min_value=departure_date,
                    value=departure_date + timedelta(days=7),
                    label_visibility="collapsed"
                )
        else:
            return_date = None
        
        with col5:
            st.markdown("**Passengers:**")
            passengers = st.selectbox(
                "Passengers",
                ["1 Adult", "2 Adults", "3 Adults", "4 Adults", "5+ Adults"],
                label_visibility="collapsed"
            )
        
        # Search Button
        search_submitted = st.form_submit_button("🔍 Search Flights")
        
        if search_submitted:
            if not origin or not destination:
                st.error("⚠️ Please enter all flight search details.")
            elif origin == destination:
                st.error("⚠️ Origin and destination cannot be the same.")
            else:
                st.session_state.search_params = {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "passengers": passengers,
                    "trip_type": trip_type
                }
                
                search_entry = f"{origin} → {destination} - {departure_date.strftime('%b %d')}"
                if search_entry not in st.session_state.recent_searches:
                    st.session_state.recent_searches.insert(0, search_entry)
                    st.session_state.recent_searches = st.session_state.recent_searches[:5]
                
                st.session_state.search_completed = True
                st.success("✅ Search complete! Click the **📋 Flight Results** tab above.")

    # Recent Searches Section
    st.markdown("---")
    st.markdown("### Recent Searches")
    st.caption("*Optimized for experienced users to use quickly*")

    if st.session_state.recent_searches:
        for search in st.session_state.recent_searches:
            if st.button(f"🔄 {search}", key=search):
                st.session_state.search_completed = True
                st.info(f"Re-searching: {search}")
    else:
        st.info("No recent searches yet. Your searches will appear here.")