import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import io
import zipfile
import os
import openpyxl
from xml.etree import ElementTree as ET

# Last.fm API configuration
API_KEY = "YOUR_LASTFM_API_KEY"  # Replace with your Last.fm API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Custom CSS for minimal, elegant, stylish UI
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@300;400;700&display=swap');

* {
    font-family: 'Bricolage Grotesque', sans-serif !important;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

/* Theme Styles */
.theme-light {
    --bg: #F5F7FA;
    --text: #2D3748;
    --accent: #4A5568;
    --card-bg: rgba(255, 255, 255, 0.8);
    --hover: #E2E8F0;
}
.theme-dark {
    --bg: #1A202C;
    --text: #E2E8F0;
    --accent: #A0AEC0;
    --card-bg: rgba(45, 55, 72, 0.8);
    --hover: #4A5568;
}
.theme-black {
    --bg: #000000;
    --text: #FFFFFF;
    --accent: #CBD5E0;
    --card-bg: rgba(26, 32, 44, 0.8);
    --hover: #2D3748;
}
.theme-blue {
    --bg: #0E1B3D;
    --text: #E6F3FF;
    --accent: #90CDF4;
    --card-bg: rgba(44, 82, 130, 0.8);
    --hover: #2B6CB0;
}
.theme-orange {
    --bg: #3C1A00;
    --text: #FFE8D6;
    --accent: #F6AD55;
    --card-bg: rgba(124, 45, 18, 0.8);
    --hover: #DD6B20;
}
.theme-graffiti {
    --bg: linear-gradient(135deg, #FF0066, #00FFCC, #FFCC00, #FF0066);
    --text: #000000;
    --accent: #FFFFFF;
    --card-bg: rgba(255, 255, 255, 0.7);
    --hover: rgba(0, 0, 0, 0.1);
    background-size: 200% 200%;
    animation: gradientShift 8s ease infinite;
}

/* Global Styles */
[data-testid="stAppViewContainer"] {
    background: var(--bg);
    color: var(--text);
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease-out;
}

.stMarkdown, .stDataFrame, h1, h2, h3, p, div {
    color: var(--text) !important;
}

/* Top Navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    border-bottom: 1px solid var(--hover);
}

.navbar-title {
    font-size: 1.2rem;
    font-weight: 700;
}

.navbar-user {
    font-size: 0.9rem;
    opacity: 0.8;
}

.navbar-theme {
    cursor: pointer;
    padding: 6px;
    border-radius: 50%;
    transition: background 0.2s;
}
.navbar-theme:hover {
    background: var(--hover);
}

/* Sidebar */
.stSidebar {
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    width: 220px !important;
    padding: 16px;
    border-right: 1px solid var(--hover);
    transition: width 0.3s ease;
}

.sidebar-item {
    display: flex;
    align-items: center;
    padding: 10px;
    margin: 4px 0;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s, transform 0.2s;
}
.sidebar-item:hover {
    background: var(--hover);
    transform: translateX(4px);
}
.sidebar-item svg {
    margin-right: 8px;
}

/* Cards */
.quick-facts-card, .error-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
    animation: fadeIn 0.6s ease-out;
}
.quick-facts-card:hover, .error-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.error-card {
    border-left: 4px solid #FF4D4D;
}

/* Tabs */
[data-testid="stTabs"] button {
    background: none;
    border: none;
    padding: 10px 16px;
    font-size: 1rem;
    color: var(--text);
    position: relative;
    transition: color 0.2s;
}
[data-testid="stTabs"] button:hover {
    color: var(--accent);
}
[data-testid="stTabs"] button[aria-selected="true"]::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent);
}

/* Charts and Tables */
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {
    border-radius: 12px;
    padding: 12px;
    background: var(--card-bg);
    transition: box-shadow 0.2s;
}
[data-testid="stPlotlyChart"]:hover, [data-testid="stDataFrame"]:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stDataFrame tr:nth-child(even) {
    background: rgba(0, 0, 0, 0.05);
}
.stDataFrame tr:hover {
    background: var(--hover);
}

/* Graffiti Theme */
.theme-graffiti h2, .theme-graffiti .navbar-title {
    animation: bounce 2s infinite;
}
</style>
"""

# Function to apply theme
def apply_theme(theme, custom_accent, card_opacity, font_size, animation_speed):
    st.markdown(f"""
        <style>
            [data-testid="stAppViewContainer"] {{ 
                background: {'#F5F7FA' if theme == 'light' else 
                            '#1A202C' if theme == 'dark' else 
                            '#000000' if theme == 'black' else 
                            '#0E1B3D' if theme == 'blue' else 
                            '#3C1A00' if theme == 'orange' else 
                            'linear-gradient(135deg, #FF0066, #00FFCC, #FFCC00, #FF0066)'};
                background-size: {'200% 200%' if theme == 'graffiti' else 'auto'};
                animation: {'gradientShift 8s ease infinite' if theme == 'graffiti' else 'none'};
                font-size: {font_size}px;
            }}
            .stMarkdown, .stDataFrame, h1, h2, h3, p, div {{ 
                color: {'#2D3748' if theme == 'light' else 
                        '#E2E8F0' if theme == 'dark' else 
                        '#FFFFFF' if theme == 'black' else 
                        '#E6F3FF' if theme == 'blue' else 
                        '#FFE8D6' if theme == 'orange' else 
                        '#000000'} !important; 
            }}
            .quick-facts-card, .error-card {{
                background: {'rgba(255, 255, 255, ' + str(card_opacity) + ')' if theme == 'light' or theme == 'graffiti' else 
                            'rgba(45, 55, 72, ' + str(card_opacity) + ')' if theme == 'dark' else 
                            'rgba(26, 32, 44, ' + str(card_opacity) + ')' if theme == 'black' else 
                            'rgba(44, 82, 130, ' + str(card_opacity) + ')' if theme == 'blue' else 
                            'rgba(124, 45, 18, ' + str(card_opacity) + ')'};
                transition-duration: {animation_speed}s;
            }}
            .navbar, .stSidebar {{
                background: {'rgba(255, 255, 255, ' + str(card_opacity) + ')' if theme == 'light' else 
                            'rgba(45, 55, 72, ' + str(card_opacity) + ')' if theme == 'dark' else 
                            'rgba(26, 32, 44, ' + str(card_opacity) + ')' if theme == 'black' else 
                            'rgba(44, 82, 130, ' + str(card_opacity) + ')' if theme == 'blue' else 
                            'rgba(124, 45, 18, ' + str(card_opacity) + ')' if theme == 'orange' else 
                            'rgba(255, 255, 255, ' + str(card_opacity * 0.7) + ')'};
            }}
            .theme-{theme} {{ --accent: {custom_accent if custom_accent else {'#4A5568' if theme == 'light' else '#A0AEC0' if theme == 'dark' else '#CBD5E0' if theme == 'black' else '#90CDF4' if theme == 'blue' else '#F6AD55' if theme == 'orange' else '#FFFFFF'}}; }}
        </style>
    """, unsafe_allow_html=True)

# Function to fetch Last.fm data
@st.cache_data
def fetch_lastfm_data(method, username, limit=10, page=1, period="overall", from_ts=None, to_ts=None, **extra_params):
    params = {
        "method": method,
        "user": username,
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
        "page": page,
        "period": period
    }
    if from_ts:
        params["from"] = from_ts
    if to_ts:
        params["to"] = to_ts
    params.update(extra_params)
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Function to check if user exists
def check_user_exists(username):
    data = fetch_lastfm_data("user.getInfo", username)
    return data and "user" in data

# Data fetching functions
def get_top_artists(username, limit=10, period="overall"):
    data = fetch_lastfm_data("user.getTopArtists", username, limit, period=period)
    if data and "topartists" in data:
        artists = data["topartists"]["artist"]
        return pd.DataFrame([
            {"Artist": artist["name"], "Playcount": int(artist["playcount"])}
            for artist in artists
        ])
    return pd.DataFrame()

def get_top_tracks(username, limit=10, period="overall"):
    data = fetch_lastfm_data("user.getTopTracks", username, limit, period=period)
    if data and "toptracks" in data:
        tracks = data["toptracks"]["track"]
        return pd.DataFrame([
            {"Track": track["name"], "Artist": track["artist"]["name"], "Playcount": int(track["playcount"])}
            for track in tracks
        ])
    return pd.DataFrame()

def get_top_albums(username, limit=10, period="overall"):
    data = fetch_lastfm_data("user.getTopAlbums", username, limit, period=period)
    if data and "topalbums" in data:
        albums = data["topalbums"]["album"]
        return pd.DataFrame([
            {"Album": album["name"], "Artist": album["artist"]["name"], "Playcount": int(album["playcount"])}
            for album in albums
        ])
    return pd.DataFrame()

def get_recent_tracks(username, limit=10):
    data = fetch_lastfm_data("user.getRecentTracks", username, limit)
    if data and "recenttracks" in data:
        tracks = data["recenttracks"]["track"]
        return pd.DataFrame([
            {
                "Track": track["name"],
                "Artist": track["artist"]["#text"],
                "Album": track.get("album", {}).get("#text", "Unknown"),
                "Date": track.get("date", {}).get("#text", "Now Playing") if "date" in track else "Now Playing"
            }
            for track in tracks
        ])
    return pd.DataFrame()

def get_listening_heatmap(username, limit=200):
    data = fetch_lastfm_data("user.getRecentTracks", username, limit)
    if data and "recenttracks" in data:
        tracks = data["recenttracks"]["track"]
        df = pd.DataFrame([
            {"Date": track.get("date", {}).get("#text", None)}
            for track in tracks if "date" in track
        ])
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y, %H:%M")
            df["Day"] = df["Date"].dt.day_name()
            df["Hour"] = df["Date"].dt.hour
            heatmap_data = df.groupby(["Day", "Hour"]).size().reset_index(name="Plays")
            return heatmap_data
    return pd.DataFrame()

def get_weekly_comparison(username):
    now = datetime.utcnow()
    current_week_end = now
    current_week_start = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second)
    previous_week_end = current_week_start - timedelta(seconds=1)
    previous_week_start = previous_week_end - timedelta(days=6, hours=23, minutes=59, seconds=59)

    current_week_from = int(current_week_start.timestamp())
    current_week_to = int(current_week_end.timestamp())
    previous_week_from = int(previous_week_start.timestamp())
    previous_week_to = int(previous_week_end.timestamp())

    def fetch_all_tracks(from_ts, to_ts, limit=200):
        all_tracks = []
        page = 1
        while True:
            data = fetch_lastfm_data("user.getRecentTracks", username, limit=limit, page=page, from_ts=from_ts, to_ts=to_ts)
            if not data or "recenttracks" not in data:
                break
            tracks = data["recenttracks"]["track"]
            all_tracks.extend(tracks)
            if len(tracks) < limit:
                break
            page += 1
            time.sleep(0.5)
        return all_tracks

    current_tracks = fetch_all_tracks(current_week_from, current_week_to)
    previous_tracks = fetch_all_tracks(previous_week_from, previous_week_to)

    def calculate_metrics(tracks):
        if not tracks:
            return {
                "artists": 0,
                "tracks": 0,
                "scrobbles": 0,
                "listening_time": 0,
                "avg_scrobbles": 0,
                "most_active_day": {"day": "None", "scrobbles": 0}
            }
        artists = len(set(track["artist"]["#text"] for track in tracks))
        unique_tracks = len(set((track["name"], track["artist"]["#text"]) for track in tracks))
        scrobbles = len(tracks)
        listening_time = (scrobbles * 3.5) / 60
        days = 7 if tracks == previous_tracks else (now - current_week_start).days + 1
        avg_scrobbles = scrobbles / max(days, 1)
        dates = [datetime.strptime(track["date"]["#text"], "%d %b %Y, %H:%M") for track in tracks if "date" in track]
        if dates:
            day_counts = pd.Series([d.strftime("%b %d") for d in dates]).value_counts()
            most_active = day_counts.idxmax()
            most_active_scrobbles = day_counts.max()
        else:
            most_active = "None"
            most_active_scrobbles = 0
        return {
            "artists": artists,
            "tracks": unique_tracks,
            "scrobbles": scrobbles,
            "listening_time": round(listening_time, 1),
            "avg_scrobbles": round(avg_scrobbles, 1),
            "most_active_day": {"day": most_active, "scrobbles": most_active_scrobbles}
        }

    current_metrics = calculate_metrics(current_tracks)
    previous_metrics = calculate_metrics(previous_tracks)

    return {
        "current": current_metrics,
        "previous": previous_metrics,
        "current_period": f"{current_week_start.strftime('%b %d')} - {current_week_end.strftime('%b %d')}",
        "previous_period": f"{previous_week_start.strftime('%b %d')} - {previous_week_end.strftime('%b %d')}"
    }

def get_top_decades(username, limit=10):
    data = fetch_lastfm_data("user.getTopTracks", username, limit=limit)
    if not data or "toptracks" not in data:
        return pd.DataFrame()
    
    tracks = data["toptracks"]["track"]
    decade_data = []
    for track in tracks:
        track_name = track["name"]
        artist_name = track["artist"]["name"]
        playcount = int(track["playcount"])
        
        track_info = fetch_lastfm_data("track.getInfo", username, limit=1, track=track_name, artist=artist_name)
        time.sleep(0.5)
        
        year = None
        if track_info and "track" in track_info and "album" in track_info["track"]:
            release_date = track_info["track"]["album"].get("releasedate", "")
            try:
                year = int(release_date.strip()[-4:]) if release_date and release_date.strip() else None
            except (ValueError, TypeError):
                year = None
        
        if year:
            decade = (year // 10) * 10
            decade_data.append({"Decade": str(decade), "Playcount": playcount})
    
    if decade_data:
        df = pd.DataFrame(decade_data)
        return df.groupby("Decade")["Playcount"].sum().reset_index()
    return pd.DataFrame()

# Function to export data
def export_data(datasets, format_type, username):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if format_type == "csv":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, df in datasets.items():
                if not df.empty:
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    zf.writestr(f"{username}_{name}.csv", csv_buffer.getvalue())
        buffer.seek(0)
        return buffer, f"{username}_data_{timestamp}.zip"

    elif format_type == "json":
        export_data = {name: df.to_dict(orient="records") for name, df in datasets.items() if not df.empty}
        buffer = io.BytesIO()
        buffer.write(json.dumps(export_data, indent=2).encode("utf-8"))
        buffer.seek(0)
        return buffer, f"{username}_data_{timestamp}.json"

    elif format_type == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for name, df in datasets.items():
                if not df.empty:
                    df.to_excel(writer, sheet_name=name, index=False)
        buffer.seek(0)
        return buffer, f"{username}_data_{timestamp}.xlsx"

    elif format_type == "pbix":
        temp_dir = f"temp_{username}_{timestamp}"
        os.makedirs(temp_dir, exist_ok=True)
        csv_files = []
        for name, df in datasets.items():
            if not df.empty:
                csv_path = os.path.join(temp_dir, f"{name}.csv")
                df.to_csv(csv_path, index=False)
                csv_files.append(csv_path)
        
        readme = (
            "To use in Power BI:\n"
            "1. Open Power BI Desktop.\n"
            "2. Click 'Get Data' > 'Text/CSV'.\n"
            "3. Import each CSV file from this folder.\n"
            "4. Create your visualizations."
        )
        readme_path = os.path.join(temp_dir, "README.txt")
        with open(readme_path, "w") as f:
            f.write(readme)
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for csv_file in csv_files:
                zf.write(csv_file, os.path.basename(csv_file))
            zf.write(readme_path, "README.txt")
        
        for file in csv_files + [readme_path]:
            os.remove(file)
        os.rmdir(temp_dir)
        
        buffer.seek(0)
        return buffer, f"{username}_data_for_pbix_{timestamp}.zip"

    elif format_type == "twb":
        temp_dir = f"temp_{username}_{timestamp}"
        os.makedirs(temp_dir, exist_ok=True)
        csv_files = []
        for name, df in datasets.items():
            if not df.empty:
                csv_path = os.path.join(temp_dir, f"{name}.csv")
                df.to_csv(csv_path, index=False)
                csv_files.append(csv_path)
        
        twb_content = ET.Element("workbook", xmlns="http://www.tableausoftware.com/xml/workbook", version="2021.4")
        datasources = ET.SubElement(twb_content, "datasources")
        for csv_file in csv_files:
            datasource = ET.SubElement(datasources, "datasource", name=os.path.basename(csv_file).replace(".csv", ""))
            connection = ET.SubElement(datasource, "connection", attrib={"class": "csv"})  # Fixed syntax
            ET.SubElement(connection, "named-connections")
            relation = ET.SubElement(connection, "relation", name=os.path.basename(csv_file), type="table")
            metadata = ET.SubElement(datasource, "metadata")
            for col in datasets[os.path.basename(csv_file).replace(".csv", "")].columns:
                ET.SubElement(metadata, "column", name=col, datatype="string")
        
        twb_buffer = io.BytesIO()
        ET.ElementTree(twb_content).write(twb_buffer, encoding="utf-8", xml_declaration=True)
        twb_buffer.seek(0)
        
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for csv_file in csv_files:
                zf.write(csv_file, os.path.basename(csv_file))
            zf.writestr(f"{username}_data.twb", twb_buffer.getvalue())
        
        for csv_file in csv_files:
            os.remove(csv_file)
        os.rmdir(temp_dir)
        
        buffer.seek(0)
        return buffer, f"{username}_data_for_tableau_{timestamp}.zip"

# Streamlit app
st.set_page_config(page_title="Last.fm Dashboard", layout="wide")
st.markdown(custom_css, unsafe_allow_html=True)

# Session state for sidebar and export
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "export_clicked" not in st.session_state:
    st.session_state.export_clicked = False

# Sidebar
with st.sidebar:
    st.markdown("""
        <div class='sidebar-item' onclick='toggleSidebar()'>
            <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='var(--text)'><path d='M3 6h18M3 12h18M3 18h18'/></svg>
            <span>Menu</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.sidebar_open:
        st.markdown("<div class='sidebar-item'>", unsafe_allow_html=True)
        username = st.text_input("Username", "", placeholder="Enter Last.fm username")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='sidebar-item'>", unsafe_allow_html=True)
        period = st.selectbox("Time Range", ["overall", "7day", "1month", "3month", "6month", "12month"], index=0)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='sidebar-item'>", unsafe_allow_html=True)
        theme = st.selectbox("Theme", ["light", "dark", "black", "blue", "orange", "graffiti"], index=0)
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander("Customize"):
            font_size = st.slider("Font Size (px)", 12, 20, 16)
            card_opacity = st.slider("Card Opacity", 0.3, 1.0, 0.8, 0.1)
            animation_speed = st.slider("Animation Speed (s)", 0.1, 1.0, 0.3, 0.1)
            custom_accent = st.text_input("Custom Accent Color (Hex)", "", placeholder="#4A5568")
        
        if username and check_user_exists(username):
            with st.expander("Export Data"):
                export_format = st.selectbox("Format", ["csv", "json", "excel", "pbix", "twb"])
                if st.button("Export"):
                    st.session_state.export_clicked = True

# Top Navbar
st.markdown(f"""
    <div class='navbar'>
        <div class='navbar-title'>Last.fm Dashboard</div>
        <div class='navbar-user'>{username if username else 'No user'}</div>
        <div class='navbar-theme' onclick='toggleTheme()'>
            <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='var(--text)'><path d='M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z'/></svg>
        </div>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Tracks", "Albums", "Artists"])

# Main content
if not username:
    with tab1:
        st.markdown("<div class='error-card'>Please enter a Last.fm username in the sidebar.</div>", unsafe_allow_html=True)
else:
    if not check_user_exists(username):
        with tab1:
            st.markdown("<div class='error-card'>No user exists with that username.</div>", unsafe_allow_html=True)
    else:
        with st.spinner("Fetching data..."):
            # Fetch data
            top_artists_df = get_top_artists(username, limit=10, period=period)
            top_tracks_df = get_top_tracks(username, limit=10, period=period)
            top_albums_df = get_top_albums(username, limit=10, period=period)
            recent_tracks_df = get_recent_tracks(username, limit=10)
            heatmap_df = get_listening_heatmap(username)
            weekly_comparison = get_weekly_comparison(username)
            decades_df = get_top_decades(username)

            # Prepare datasets for export
            datasets = {
                "top_artists": top_artists_df,
                "top_tracks": top_tracks_df,
                "top_albums": top_albums_df,
                "recent_tracks": recent_tracks_df,
                "heatmap": heatmap_df,
                "decades": decades_df,
                "weekly_comparison": pd.DataFrame([
                    {"Period": weekly_comparison["current_period"], **weekly_comparison["current"]},
                    {"Period": weekly_comparison["previous_period"], **weekly_comparison["previous"]}
                ])
            }

            # Handle export
            if st.session_state.export_clicked:
                buffer, filename = export_data(datasets, export_format, username)
                st.download_button(
                    label="Download File",
                    data=buffer,
                    file_name=filename,
                    mime="application/zip" if filename.endswith(".zip") else "application/octet-stream"
                )
                st.session_state.export_clicked = False

            # Theme-specific chart colors
            theme_colors = {
                "light": "Blues",
                "dark": "Viridis",
                "black": "Inferno",
                "blue": "Cividis",
                "orange": "Oranges",
                "graffiti": "Plotly"
            }

            # Tab 1: Home
            with tab1:
                st.markdown("<h2>Welcome</h2>", unsafe_allow_html=True)
                st.markdown(f"Exploring <b>{username}</b>'s music taste", unsafe_allow_html=True)

                # Quick Facts
                st.markdown("<h3>Quick Facts</h3>", unsafe_allow_html=True)
                current = weekly_comparison["current"]
                previous = weekly_comparison["previous"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                    st.write(f"**This Week ({weekly_comparison['current_period']})**")
                    st.write(f"- Listening Time: {current['listening_time']} hours")
                    st.write(f"- Avg. Scrobbles/Day: {current['avg_scrobbles']}")
                    st.write(f"- Most Active Day: {current['most_active_day']['day']} ({current['most_active_day']['scrobbles']} scrobbles)")
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                    st.write(f"**Last Week ({weekly_comparison['previous_period']})**")
                    st.write(f"- Listening Time: {previous['listening_time']} hours")
                    st.write(f"- Avg. Scrobbles/Day: {previous['avg_scrobbles']}")
                    st.write(f"- Most Active Day: {previous['most_active_day']['day']} ({previous['most_active_day']['scrobbles']} scrobbles)")
                    st.markdown("</div>", unsafe_allow_html=True)

                # Weekly Insights
                st.markdown("<h3>Weekly Insights</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                    st.write(f"**This Week ({weekly_comparison['current_period']})**")
                    st.write(f"- Unique Artists: {current['artists']}")
                    st.write(f"- Unique Tracks: {current['tracks']}")
                    st.write(f"- Total Scrobbles: {current['scrobbles']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                    st.write(f"**Last Week ({weekly_comparison['previous_period']})**")
                    st.write(f"- Unique Artists: {previous['artists']}")
                    st.write(f"- Unique Tracks: {previous['tracks']}")
                    st.write(f"- Total Scrobbles: {previous['scrobbles']}")
                    st.markdown("</div>", unsafe_allow_html=True)

                # Top Decades
                st.markdown("<h3>Top Decades</h3>", unsafe_allow_html=True)
                if not decades_df.empty:
                    st.dataframe(decades_df, use_container_width=True)
                    fig_decades = px.bar(
                        decades_df,
                        x="Decade",
                        y="Playcount",
                        title="",
                        color="Playcount",
                        color_continuous_scale=theme_colors[theme]
                    )
                    fig_decades.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_decades, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No decade data available (release years may be missing).</div>", unsafe_allow_html=True)

                # Quick Insights
                st.markdown("<h3>Quick Insights</h3>", unsafe_allow_html=True)
                if not top_artists_df.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                        st.write(f"🎸 Favorite Artist: **{top_artists_df.iloc[0]['Artist']}**")
                        if not top_tracks_df.empty:
                            st.write(f"🎵 Top Track: **{top_tracks_df.iloc[0]['Track']}**")
                        st.markdown("</div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                        if not top_albums_df.empty:
                            st.write(f"💿 Top Album: **{top_albums_df.iloc[0]['Album']}**")
                        if not recent_tracks_df.empty and "Now Playing" in recent_tracks_df["Date"].values:
                            now_playing = recent_tracks_df[recent_tracks_df["Date"] == "Now Playing"].iloc[0]
                            st.write(f"▶️ Now Playing: **{now_playing['Track']}** by **{now_playing['Artist']}**")
                        st.markdown("</div>", unsafe_allow_html=True)

                # Listening Activity Heatmap
                if not heatmap_df.empty:
                    st.markdown("<h3>Listening Activity</h3>", unsafe_allow_html=True)
                    fig_heatmap = px.density_heatmap(
                        heatmap_df,
                        x="Hour",
                        y="Day",
                        z="Plays",
                        title="",
                        category_orders={"Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                        color_continuous_scale=theme_colors[theme]
                    )
                    fig_heatmap.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)

            # Tab 2: Tracks
            with tab2:
                st.markdown("<h2>Tracks</h2>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<h3>Top Tracks</h3>", unsafe_allow_html=True)
                    if not top_tracks_df.empty:
                        st.dataframe(top_tracks_df, use_container_width=True)
                        fig_tracks = px.bar(
                            top_tracks_df,
                            x="Track",
                            y="Playcount",
                            title="",
                            color="Playcount",
                            color_continuous_scale=theme_colors[theme],
                            hover_data=["Artist"]
                        )
                        fig_tracks.update_layout(
                            margin=dict(l=20, r=20, t=20, b=20),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                        st.plotly_chart(fig_tracks, use_container_width=True)
                    else:
                        st.markdown("<div class='error-card'>No top tracks data available.</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<h3>Recent Tracks</h3>", unsafe_allow_html=True)
                    if not recent_tracks_df.empty:
                        st.dataframe(recent_tracks_df, use_container_width=True)
                        artist_counts = recent_tracks_df["Artist"].value_counts().reset_index()
                        artist_counts.columns = ["Artist", "Count"]
                        fig_doughnut = go.Figure(data=[
                            go.Pie(
                                labels=artist_counts["Artist"],
                                values=artist_counts["Count"],
                                hole=0.4,
                                textinfo="label+percent",
                                marker=dict(colors=px.colors.qualitative.Plotly)
                            )
                        ])
                        fig_doughnut.update_layout(
                            title="",
                            showlegend=True,
                            margin=dict(l=20, r=20, t=20, b=20),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                        st.plotly_chart(fig_doughnut, use_container_width=True)
                    else:
                        st.markdown("<div class='error-card'>No recent tracks data available.</div>", unsafe_allow_html=True)

            # Tab 3: Albums
            with tab3:
                st.markdown("<h2>Albums</h2>", unsafe_allow_html=True)
                st.markdown("<h3>Top Albums</h3>", unsafe_allow_html=True)
                if not top_albums_df.empty:
                    st.dataframe(top_albums_df, use_container_width=True)
                    fig_albums = px.bar(
                        top_albums_df,
                        x="Album",
                        y="Playcount",
                        title="",
                        color="Playcount",
                        color_continuous_scale=theme_colors[theme],
                        hover_data=["Artist"]
                    )
                    fig_albums.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_albums, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No top albums data available.</div>", unsafe_allow_html=True)

            # Tab 4: Artists
            with tab4:
                st.markdown("<h2>Artists</h2>", unsafe_allow_html=True)
                st.markdown("<h3>Top Artists</h3>", unsafe_allow_html=True)
                if not top_artists_df.empty:
                    st.dataframe(top_artists_df, use_container_width=True)
                    fig_artists = px.bar(
                        top_artists_df,
                        x="Artist",
                        y="Playcount",
                        title="",
                        color="Playcount",
                        color_continuous_scale=theme_colors[theme]
                    )
                    fig_artists.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_artists, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No top artists data available.</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; padding: 16px; color: var(--text); opacity: 0.7;'>
        Built with ❤️ using Streamlit & Last.fm API
    </div>
""", unsafe_allow_html=True)