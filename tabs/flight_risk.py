"""
Flight Risk Analysis Tab
========================
Shows detailed risk breakdown for a selected flight.
Explains WHY a flight has its predicted on-time probability.
"""

import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from data import get_probability_color, flights_data


# =============================================================================
# SETTINGS
# =============================================================================

# Colors
GREEN = '#28a745'
YELLOW = '#ffc107'
RED = '#dc3545'

# Background colors for cards
BG_GREEN = '#d4edda'
BG_YELLOW = '#fff3cd'
BG_RED = '#f8d7da'


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_risk_level(probability: int) -> str:
    """Return risk level text based on probability."""
    if probability >= 67:
        return "LOW RISK"
    elif probability >= 33:
        return "MEDIUM RISK"
    else:
        return "HIGH RISK"


def get_bar_color(probability: int) -> str:
    """Return bar color based on probability."""
    if probability >= 67:
        return GREEN
    elif probability >= 33:
        return YELLOW
    else:
        return RED


# =============================================================================
# DISPLAY COMPONENTS
# =============================================================================

def render_flight_header(flight: dict):
    """Show flight info at the top of the page."""
    col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
    
    with col1:
        if st.session_state.search_params:
            dep_date = st.session_state.search_params.get("departure_date", datetime.today())
            st.markdown(f"**{dep_date.strftime('%b %d')}**")
        else:
            st.markdown("**Dec 16**")
    with col2:
        st.markdown(f"**{flight['airline']} {flight['flight_num']}**")
    with col3:
        st.markdown(f"**{flight['origin']}** → **{flight['destination']}**")
    with col4:
        st.markdown(f"**{flight['departure']} - {flight['arrival']}** · {flight['duration']}")


def render_probability_badge(flight: dict, color: str, risk_level: str):
    """Show the big probability badge."""
    st.markdown(f"""
        <div style="background-color: {color}; color: white; padding: 15px 25px;
                    border-radius: 10px; text-align: center; display: inline-block; margin: 15px 0;">
            <div style="font-size: 36px; font-weight: bold;">{flight['on_time_prob']}%</div>
            <div style="font-size: 14px;">On-Time Probability · {risk_level}</div>
        </div>
    """, unsafe_allow_html=True)


def render_weather_cards(flight: dict):
    """Show weather conditions at both airports."""
    col1, col2 = st.columns(2)
    
    # Origin weather (always good for demo)
    with col1:
        st.markdown(f"""
            <div style="background-color: {BG_GREEN}; border-left: 6px solid {GREEN};
                        padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="color: #155724; margin: 0 0 10px 0;">🌤️ Weather at {flight['origin']}</h4>
                <p style="margin: 0; color: #155724; font-size: 14px;">
                    Clear skies, 34°F<br>Low wind. No icing risk.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Destination weather (bad if low probability)
    with col2:
        if flight['on_time_prob'] < 50:
            st.markdown(f"""
                <div style="background-color: {BG_YELLOW}; border-left: 6px solid {RED};
                            padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: {RED}; margin: 0 0 10px 0;">⚠️ Weather at {flight['destination']}</h4>
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        Heavy Snow, 28°F<br>High wind. Icing risk.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: {BG_GREEN}; border-left: 6px solid {GREEN};
                            padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h4 style="color: #155724; margin: 0 0 10px 0;">🌤️ Weather at {flight['destination']}</h4>
                    <p style="margin: 0; color: #155724; font-size: 14px;">
                        Clear skies, 42°F<br>Calm conditions.
                    </p>
                </div>
            """, unsafe_allow_html=True)


def render_performance_cards(flight: dict):
    """Show route performance and airport congestion."""
    col1, col2 = st.columns(2)
    
    delay_pct = 100 - flight['on_time_prob']
    
    # Route performance card
    with col1:
        if delay_pct > 50:
            bg, border, text = BG_RED, RED, "#721c24"
        elif delay_pct > 25:
            bg, border, text = BG_YELLOW, YELLOW, "#856404"
        else:
            bg, border, text = BG_GREEN, GREEN, "#155724"
        
        st.markdown(f"""
            <div style="background-color: {bg}; border-left: 6px solid {border};
                        padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="color: {text}; margin: 0 0 10px 0;">📊 Historic Route Performance</h4>
                <p style="margin: 0; color: {text}; font-size: 14px;">
                    Route {flight['origin']} → {flight['destination']} has<br>
                    <strong>{delay_pct}% historical delay rate</strong> in winter.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Congestion card
    with col2:
        if flight['on_time_prob'] < 50:
            level, indicator = "High", "🔴"
            bg, border, text = BG_RED, RED, "#721c24"
        elif flight['on_time_prob'] < 75:
            level, indicator = "Moderate", "🟡"
            bg, border, text = BG_YELLOW, YELLOW, "#856404"
        else:
            level, indicator = "Low", "🟢"
            bg, border, text = BG_GREEN, GREEN, "#155724"
        
        st.markdown(f"""
            <div style="background-color: {bg}; border-left: 6px solid {border};
                        padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="color: {text}; margin: 0 0 10px 0;">🛫 Airport Congestion</h4>
                <p style="margin: 0; color: {text}; font-size: 14px;">
                    {indicator} <strong>{level} congestion</strong> at {flight['destination']}<br>
                    during your arrival window.
                </p>
            </div>
        """, unsafe_allow_html=True)


def render_historical_chart(flight: dict):
    """Show bar chart of on-time probability over time."""
    st.markdown("### 📊 Flight Volume & Delay Risk Stability")
    st.markdown(f"**{flight['origin']} → {flight['destination']}** · Historical Window")
    
    # Sample data (in real app, this would come from database)
    dates = ["12-09", "12-10", "12-11", "12-12", "12-13", "12-14", "12-15", "12-16", "12-17", "12-18", "12-19"]
    probs = [78, 82, 75, 80, 85, 72, 88, flight['on_time_prob'], 94, 91, 89]
    colors = [get_bar_color(p) for p in probs]
    
    # Highlight selected date
    borders = ['rgba(0,0,0,0)'] * len(dates)
    widths = [0] * len(dates)
    borders[7] = '#000000'  # 12-16 is index 7
    widths[7] = 3
    
    fig = go.Figure(data=[
        go.Bar(
            x=dates, y=probs,
            marker_color=colors,
            marker_line_color=borders,
            marker_line_width=widths,
            text=[f"{p}%" for p in probs],
            textposition='outside',
        )
    ])
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title="Date"),
        yaxis=dict(title="On-Time Probability (%)", range=[0, 105]),
        margin=dict(l=60, r=40, t=30, b=60),
        height=350,
    )
    
    # Add "Your Flight" annotation
    fig.add_annotation(
        x="12-16", y=flight['on_time_prob'] + 8,
        text="Your Flight", showarrow=True, arrowhead=2,
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with col2:
        # Legend
        st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <p style="font-weight: bold; margin-bottom: 12px;">Risk Level Key</p>
                <div style="margin-bottom: 8px;">
                    <span style="display: inline-block; width: 16px; height: 16px; 
                                 background-color: {GREEN}; border-radius: 3px;"></span>
                    <strong>Low</strong> 68%+
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="display: inline-block; width: 16px; height: 16px; 
                                 background-color: {YELLOW}; border-radius: 3px;"></span>
                    <strong>Medium</strong> 33-67%
                </div>
                <div>
                    <span style="display: inline-block; width: 16px; height: 16px; 
                                 background-color: {RED}; border-radius: 3px;"></span>
                    <strong>High</strong> 0-32%
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_alternatives(flight: dict):
    """Show better flight alternatives if available."""
    st.markdown("### ✅ Alternatives with Lower Risk")
    
    # Find flights with better probability
    better = [f for f in flights_data 
              if f['on_time_prob'] > flight['on_time_prob'] and f['id'] != flight['id']]
    better = sorted(better, key=lambda x: x['on_time_prob'], reverse=True)[:3]
    
    if better:
        for alt in better:
            color, _ = get_probability_color(alt['on_time_prob'])
            st.markdown(f"""
                <div style="background-color: {BG_GREEN}; border-left: 6px solid {GREEN};
                            padding: 12px 15px; border-radius: 8px; margin-bottom: 10px;">
                    <strong style="color: #155724;">Dec 17 - {alt['airline']} {alt['flight_num']}</strong>
                    <span style="color: #155724;"> · {alt['departure']} - {alt['arrival']}</span>
                    <span style="background-color: {color}; color: white; padding: 5px 12px;
                                 border-radius: 5px; font-weight: bold; float: right;">
                        {alt['on_time_prob']}%
                    </span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ You've selected one of the best options available!")


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render():
    """Main function - called by app.py to display this tab."""
    
    # Make sure a flight is selected
    if not st.session_state.get('selected_flight'):
        st.warning("⚠️ Please select a flight on the Flight Results tab first.")
        return
    
    flight = st.session_state.selected_flight
    prob_color, _ = get_probability_color(flight['on_time_prob'])
    risk_level = get_risk_level(flight['on_time_prob'])
    
    # Header section
    st.subheader("Flight Detail & Risk Breakdown")
    render_flight_header(flight)
    render_probability_badge(flight, prob_color, risk_level)
    
    st.markdown("---")
    
    # Why this prediction?
    st.markdown("## Why this prediction?")
    st.caption("*Plain-language explanation of risk factors affecting your flight*")
    
    render_weather_cards(flight)
    render_performance_cards(flight)
    
    st.markdown("---")
    
    # Historical chart
    render_historical_chart(flight)
    
    st.markdown("---")
    
    # Alternatives
    render_alternatives(flight)