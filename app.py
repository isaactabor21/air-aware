import streamlit as st
from datetime import date, timedelta

# Page configuration
st.set_page_config(
    page_title="Air Aware - Flight Search",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
        /* Hide sidebar */
        [data-testid="collapsedControl"] {display: none;}
        section[data-testid="stSidebar"] {display: none;}
        
        /* Main background - neutral gradient */
        .stApp {
            background: linear-gradient(180deg, #f5f7fa 0%, #e4e8ed 50%, #d1d8e0 100%);
            background-attachment: fixed;
        }
        
        /* Main container styling */
        .main .block-container {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 20px;
            padding: 2rem 3rem;
            margin-top: 1rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(0, 0, 0, 0.05);
            max-width: 1200px;
        }
        
        /* Header styling */
        .air-aware-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #2c3e50 100%);
            padding: 25px 40px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(44, 62, 80, 0.3);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .air-aware-header h1 {
            color: white;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .air-aware-header .tagline {
            color: rgba(255, 255, 255, 0.85);
            font-size: 1rem;
            margin-top: 5px;
        }
        
        .header-stats {
            display: flex;
            gap: 30px;
        }
        
        .header-stat {
            text-align: center;
            color: white;
        }
        
        .header-stat .number {
            font-size: 1.8rem;
            font-weight: 700;
        }
        
        .header-stat .label {
            font-size: 0.75rem;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 10px 15px;
            border-radius: 15px;
            gap: 8px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: white;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 0.95rem;
            color: #495057;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #5a6c7d 0%, #34495e 100%);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 73, 94, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            border: none;
            box-shadow: 0 6px 20px rgba(44, 62, 80, 0.4);
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }
        
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(52, 152, 219, 0.5);
            background: linear-gradient(135deg, #2980b9 0%, #1a5276 100%);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Form styling - tighter layout */
        .stForm {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        
        /* Reduce gap between form columns */
        .stForm [data-testid="column"] {
            padding: 0 8px;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stDateInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #e9ecef;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus {
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }
        
        /* Tighter vertical spacing in forms */
        .stForm .stMarkdown p {
            margin-bottom: 4px;
            font-size: 0.9rem;
        }
        
        /* Cards */
        .info-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }
        
        /* Success/Warning/Error messages */
        .stSuccess {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 10px;
            border-left: 5px solid #28a745;
        }
        
        .stWarning {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
            border-radius: 10px;
            border-left: 5px solid #ffc107;
        }
        
        .stError {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-radius: 10px;
            border-left: 5px solid #dc3545;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-color: #3498db;
        }
        
        /* Metric styling */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
        }
        
        /* Divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #bdc3c7, transparent);
            margin: 25px 0;
        }
        
        /* Subheader styling */
        .stSubheader {
            color: #2c3e50;
            font-weight: 700;
        }
        
        /* Flight card styling */
        .flight-card {
            background: white;
            border-radius: 15px;
            padding: 20px 25px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .flight-card:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            border-left: 4px solid #3498db;
        }
        
        /* Probability badge */
        .prob-badge {
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            color: white;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .prob-badge .number {
            font-size: 2rem;
            display: block;
        }
        
        .prob-badge .label {
            font-size: 0.7rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Alert boxes */
        .alert-box {
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .alert-danger {
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
            border-left: 5px solid #e53e3e;
        }
        
        .alert-success {
            background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
            border-left: 5px solid #38a169;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%);
            border-left: 5px solid #dd6b20;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 30px;
            border-top: 1px solid #e9ecef;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Radio buttons - inline and compact */
        .stRadio > div {
            background: white;
            padding: 8px 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .stRadio > div > div {
            gap: 15px;
        }
        
        /* Selectbox */
        .stSelectbox label {
            font-weight: 600;
            color: #495057;
        }
        
        /* Map container */
        iframe {
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }
        
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recent_searches' not in st.session_state:
    st.session_state.recent_searches = []

if 'search_completed' not in st.session_state:
    st.session_state.search_completed = False

if 'search_params' not in st.session_state:
    st.session_state.search_params = {}

if 'selected_flight' not in st.session_state:
    st.session_state.selected_flight = None

# Import tab modules
from tabs import home, flight_results, flight_risk, weather_map

# Custom Header
st.markdown("""
    <div class="air-aware-header">
        <div>
            <h1>✈️ Air Aware</h1>
            <div class="tagline">Predict delays. Travel smarter. Fly confident.</div>
        </div>
        <div class="header-stats">
            <div class="header-stat">
                <div class="number">98%</div>
                <div class="label">Accuracy</div>
            </div>
            <div class="header-stat">
                <div class="number">500+</div>
                <div class="label">Airports</div>
            </div>
            <div class="header-stat">
                <div class="number">Live</div>
                <div class="label">Weather Data</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Navigation Tabs at the top
tab_home, tab_results, tab_risk, tab_weather = st.tabs([
    "🏠 Home", 
    "📋 Flight Results", 
    "⚠️ Risk Analysis", 
    "🌤️ Weather Radar"
])

# Render each tab content from separate files
with tab_home:
    home.render()

with tab_results:
    flight_results.render()

with tab_risk:
    flight_risk.render()

# with tab_weather:
#     weather_map.render()

# Footer
st.markdown("""
    <div class="footer">
        <p>✈️ <strong>Air Aware</strong> · Powered by Machine Learning & Real-Time Weather Data</p>
        <p>© 2026 Air Aware · DS 5023 Project</p>
    </div>
""", unsafe_allow_html=True)