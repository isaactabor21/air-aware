import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

@st.cache_data(ttl=600)
def get_radar_data():
    url = "https://api.rainviewer.com/public/weather-maps.json"
    response = requests.get(url).json()
    return response

def render():  # <-- wrap everything here
    data = get_radar_data()
    host = data['host']
    past_frames = data['radar']['past']

    st.title("AirAware Live Radar")

    frame_idx = st.slider("Past 2 Hours", 0, len(past_frames)-1, len(past_frames)-1)
    selected_path = past_frames[frame_idx]['path']

    m = folium.Map(location=[38.0336, -78.5080], zoom_start=6)

    radar_url = f"{host}{selected_path}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"

    folium.TileLayer(
        tiles=radar_url,
        attr='RainViewer.com',
        name='Live Radar',
        overlay=True,
        opacity=0.7
    ).add_to(m)

    st_folium(m, width=700, height=500)