"""
Flight Results Tab
==================
Shows flight search results with delay risk predictions.
Users can filter, sort, and select flights to view detailed risk analysis.
"""

import streamlit as st
from datetime import date
import time
import plotly.graph_objects as go
from data import flights_data, get_probability_color


# =============================================================================
# SETTINGS
# =============================================================================

# Risk levels (what percentage = what risk)
LOW_RISK_THRESHOLD = 67      # 67%+ = Low Risk (green)
MEDIUM_RISK_THRESHOLD = 33   # 33-66% = Medium Risk (yellow)
                             # 0-32% = High Risk (red)

# Colors
GREEN = '#28a745'
YELLOW = '#ffc107'
RED = '#dc3545'


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_time_period(departure_time: str) -> str:
    """Figure out if a flight is morning, afternoon, or evening."""
    hour = int(departure_time.split(":")[0])
    am_pm = departure_time.split(" ")[1].upper()
    
    # Convert to 24-hour time
    if am_pm == "PM" and hour != 12:
        hour += 12
    elif am_pm == "AM" and hour == 12:
        hour = 0
    
    # Categorize
    if 5 <= hour < 12:
        return "Morning (5AM-12PM)"
    elif 12 <= hour < 17:
        return "Afternoon (12PM-5PM)"
    else:
        return "Evening (5PM-12AM)"


def parse_time_for_sort(time_str: str) -> int:
    """Convert time string to minutes since midnight (for sorting)."""
    hour = int(time_str.split(":")[0])
    minute = int(time_str.split(":")[1].split(" ")[0])
    am_pm = time_str.split(" ")[1].upper()
    
    if am_pm == "PM" and hour != 12:
        hour += 12
    elif am_pm == "AM" and hour == 12:
        hour = 0
    
    return hour * 60 + minute


def get_risk_color(probability: int) -> str:
    """Return color based on on-time probability."""
    if probability >= LOW_RISK_THRESHOLD:
        return GREEN
    elif probability >= MEDIUM_RISK_THRESHOLD:
        return YELLOW
    else:
        return RED


def apply_filters(flights: list, risk_filter: str, time_filter: str, price_filter: str) -> list:
    """Filter flights based on user selections."""
    filtered = flights.copy()
    
    # Risk filter
    if risk_filter == "Low Risk (67-100%)":
        filtered = [f for f in filtered if f['on_time_prob'] >= 67]
    elif risk_filter == "Medium Risk (33-66%)":
        filtered = [f for f in filtered if 33 <= f['on_time_prob'] < 67]
    elif risk_filter == "High Risk (0-32%)":
        filtered = [f for f in filtered if f['on_time_prob'] < 33]
    
    # Time filter
    if time_filter != "All":
        filtered = [f for f in filtered if get_time_period(f['departure']) == time_filter]
    
    # Price filter
    if price_filter == "Under $300":
        filtered = [f for f in filtered if f['price'] < 300]
    elif price_filter == "$300-$400":
        filtered = [f for f in filtered if 300 <= f['price'] <= 400]
    elif price_filter == "Over $400":
        filtered = [f for f in filtered if f['price'] > 400]
    
    return filtered


def sort_flights(flights: list, sort_by: str) -> list:
    """Sort flights based on user selection."""
    if sort_by == "On-Time Probability":
        return sorted(flights, key=lambda x: x['on_time_prob'], reverse=True)
    elif sort_by == "Price":
        return sorted(flights, key=lambda x: x['price'])
    else:
        return sorted(flights, key=lambda x: parse_time_for_sort(x['departure']))


# =============================================================================
# CHART COMPONENTS
# =============================================================================

def render_horizontal_bar_chart(flights: list):
    """Display horizontal bar chart of on-time probabilities."""
    st.markdown(
        "<p style='font-size: 18px; font-weight: 600; margin-bottom: 5px;'>"
        "Horizontal Bar: On-Time Prob. by Flight</p>",
        unsafe_allow_html=True
    )
    
    # Sort by probability (best first)
    sorted_flights = sorted(flights, key=lambda x: x['on_time_prob'], reverse=True)
    
    # Prepare data
    labels = [f"{f['airline']} {f['flight_num']}" for f in sorted_flights]
    probs = [f['on_time_prob'] for f in sorted_flights]
    colors = [get_risk_color(p) for p in probs]
    
    # Create chart
    fig = go.Figure(data=[
        go.Bar(
            y=labels,
            x=probs,
            orientation='h',
            marker_color=colors,
            text=[f"{p}%" for p in probs],
            textposition='inside',
            insidetextanchor='end',
            textfont=dict(size=14, color='white', weight='bold'),
            hovertemplate='<b>%{y}</b><br>On-Time: %{x}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="On-Time Probability (%)", range=[0, 100], dtick=20),
        margin=dict(l=10, r=20, t=5, b=40),
        height=max(200, len(flights) * 40),
        bargap=0.25,
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_pie_chart(flights: list):
    """Display pie chart showing risk distribution."""
    st.markdown(
        "<p style='font-size: 18px; font-weight: 600; margin-bottom: 5px;'>"
        "Pie Chart: Risk of Delay Distribution Today</p>",
        unsafe_allow_html=True
    )
    
    # Count flights in each risk category
    low = len([f for f in flights if f['on_time_prob'] >= 67])
    medium = len([f for f in flights if 33 <= f['on_time_prob'] < 67])
    high = len([f for f in flights if f['on_time_prob'] < 33])
    
    # Build data (only include non-zero categories)
    labels, values, colors = [], [], []
    if low > 0:
        labels.append('Low (67-100%)')
        values.append(low)
        colors.append(GREEN)
    if medium > 0:
        labels.append('Medium (33-66%)')
        values.append(medium)
        colors.append(YELLOW)
    if high > 0:
        labels.append('High (0-32%)')
        values.append(high)
        colors.append(RED)
    
    # Create chart
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors, line=dict(color='#ffffff', width=2)),
            hole=0,
            textinfo='none',
            hovertemplate='<b>%{label}</b><br>Flights: %{value}<br>%{percent}<extra></extra>',
        )
    ])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=5, b=5),
        height=220,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# =============================================================================
# FLIGHT CARD
# =============================================================================

def render_flight_card(flight: dict):
    """Display a single flight card with details and select button."""
    prob_color, _ = get_probability_color(flight['on_time_prob'])
    
    col1, col2, col3, col4 = st.columns([1.5, 2.5, 1.5, 1.5])
    
    # Probability badge
    with col1:
        st.markdown(f"""
            <div style="background-color: {prob_color}; color: white; padding: 12px;
                        border-radius: 10px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold;">{flight['on_time_prob']}%</div>
                <div style="font-size: 11px;">On-Time Probability</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Flight details
    with col2:
        st.markdown(f"**{flight['airline']} {flight['flight_num']}**")
        st.markdown(f"**{flight['origin']}** → **{flight['destination']}**")
        st.markdown(f"{flight['departure']} - {flight['arrival']} · {flight['duration']}")
        st.caption(f"{flight['stops']}")
    
    # Price
    with col3:
        st.markdown(f"### ${flight['price']}")
    
    # Select button
    with col4:
        if st.button("Select", key=f"select_{flight['id']}", use_container_width=True):
            st.session_state.selected_flight = flight
            st.session_state.flight_selected = True
            st.success(f"Selected {flight['airline']} {flight['flight_num']}")
    
    st.markdown("---")


# =============================================================================
# WEATHER ALERTS
# =============================================================================

def render_weather_alerts(filtered_flights: list):
    """Show alerts for high-risk flights and suggest alternatives."""
    st.markdown("### ⚠️ Weather & Risk Alerts")
    
    # Check for risky flights
    risky_flights = [f for f in filtered_flights if f['on_time_prob'] < 50]
    
    if risky_flights:
        # Warning alert
        st.markdown("""
            <div style="background-color: #fff3cd; border-left: 6px solid #dc3545;
                        padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="color: #dc3545; margin: 0;">⚠️ MSP Weather Alert: Winter Storm Dec 16</h4>
                <p style="margin: 10px 0 0 0; color: #856404;">
                    Several flights may be affected. Consider flights with higher on-time probability.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Better option suggestion
        best = max(flights_data, key=lambda x: x['on_time_prob'])
        st.markdown(f"""
            <div style="background-color: #d4edda; border-left: 6px solid #28a745;
                        padding: 15px; border-radius: 8px;">
                <h4 style="color: #155724; margin: 0;">✅ Better Option Found</h4>
                <p style="margin: 10px 0 0 0; color: #155724;">
                    <strong>Dec 15: DCA → MSP - {best['on_time_prob']}% On-Time</strong><br>
                    {best['airline']} {best['flight_num']} · ${best['price']}
                </p>
            </div>
        """, unsafe_allow_html=True)
    elif filtered_flights:
        st.success("✅ All displayed flights have good on-time probability!")
    
    st.info("💡 Select a flight and click the **⚠️ Risk Analysis** tab for details.")


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render():
    """Main function - called by app.py to display this tab."""
    
    # Make sure user searched first
    if not st.session_state.search_completed:
        st.warning("⚠️ Please search for a flight on the Home tab first.")
        return
    
    # Header
    st.subheader("Flight Results")
    if st.session_state.search_params:
        params = st.session_state.search_params
        st.markdown(f"### {params['origin']} → {params['destination']} · {params['departure_date'].strftime('%b %d')}")
    
    # Filter controls
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        risk_filter = st.selectbox("Risk", ["All", "Low Risk (67-100%)", "Medium Risk (33-66%)", "High Risk (0-32%)"])
    with col2:
        time_filter = st.selectbox("Time", ["All", "Morning (5AM-12PM)", "Afternoon (12PM-5PM)", "Evening (5PM-12AM)"])
    with col3:
        price_filter = st.selectbox("Price", ["All", "Under $300", "$300-$400", "Over $400"])
    with col4:
        sort_by = st.selectbox("Sort By", ["On-Time Probability", "Price", "Departure Time"])
    
    # Load and filter flights
    with st.spinner("🔍 Searching for flights..."):
        time.sleep(1)
        filtered = apply_filters(flights_data, risk_filter, time_filter, price_filter)
        filtered = sort_flights(filtered, sort_by)
    
    # Charts
    if filtered:
        col_bar, col_pie = st.columns([1.5, 1])
        with col_bar:
            render_horizontal_bar_chart(filtered)
        with col_pie:
            render_pie_chart(filtered)
    
    st.markdown("---")
    
    # Flight cards
    st.markdown("#### Available Flights")
    if filtered:
        for flight in filtered:
            render_flight_card(flight)
    else:
        st.warning("No flights found. Try adjusting your filters.")
    
    # Alerts
    render_weather_alerts(filtered)