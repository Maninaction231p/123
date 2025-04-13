import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Last.fm API configuration
API_KEY = "5fa9b4f47365a06fc995f1c83fb0d621"  # Replace with your Last.fm API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Custom CSS with reduced navbar-content gap
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@300;400;700&display=swap');

div[data-testid="stToolbar"] {
    display: none;
}

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
    --card-bg: rgba(255, 255, 255, 0.9);
    --hover: #E2E8F0;
}
.theme-dark {
    --bg: #1A202C;
    --text: #E2E8F0;
    --accent: #A0AEC0;
    --card-bg: rgba(45, 55, 72, 0.9);
    --hover: #4A5568;
}
.theme-black {
    --bg: #000000;
    --text: #FFFFFF;
    --accent: #CBD5E0;
    --card-bg: rgba(26, 32, 44, 0.9);
    --hover: #2D3748;
}
.theme-blue {
    --bg: #0E1B3D;
    --text: #E6F3FF;
    --accent: #90CDF4;
    --card-bg: rgba(44, 82, 130, 0.9);
    --hover: #2B6CB0;
}
.theme-orange {
    --bg: #3C1A00;
    --text: #FFE8D6;
    --accent: #F6AD55;
    --card-bg: rgba(124, 45, 18, 0.9);
    --hover: #DD6B20;
}
.theme-graffiti {
    --bg: linear-gradient(135deg, #FF0066, #00FFCC, #FFCC00, #FF0066) !important;
    --text: #000000;
    --accent: #FFFFFF;
    --card-bg: rgba(255, 255, 255, 0.85);
    --hover: rgba(0, 0, 0, 0.2);
    background-size: 200% 200%;
    animation: gradientShift 8s ease infinite;
}

/* Global Styles */
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    transition: all 0.3s ease;
    animation: fadeIn 0.5s ease-out;
}
.stMarkdown, .stDataFrame, h1, h2, h3, p, div {
    color: var(--text) !important;
}

/* Navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    padding: 4px 8px;
    display: inline-flex;
    align-items: center;
    z-index: 1000;
    border-bottom: 1px solid var(--hover);
    width: 100%;
    height: 32px;
    overflow-x: auto;
    white-space: nowrap;
}
.navbar-controls {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    flex: 1;
}
.navbar-item {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    flex: 0 0 auto;
}
.navbar-item svg {
    stroke: var(--accent);
    width: 10px;
    height: 10px;
}
.navbar-item input, .navbar-item select {
    background: var(--hover);
    border: none;
    border-radius: 2px;
    padding: 2px 4px;
    color: var(--text);
    font-size: 0.7rem;
    max-width: 80px;
    min-width: 50px;
}
.navbar-item input:focus, .navbar-item select:focus {
    outline: none;
    box-shadow: 0 0 2px var(--accent);
}
/* Ensure columns stay inline */
div[data-testid="stHorizontalBlock"] {
    display: inline-flex !important;
    gap: 4px;
    align-items: center;
}
div[data-testid="column"] {
    display: inline-flex;
    align-items: center;
    flex: 0 0 auto;
    min-width: 0;
}

/* Cards */
.quick-facts-card, .error-card {
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
    animation: fadeIn 0.6s ease-out;
}
.quick-facts-card:hover, .error-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
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
    font-weight: 700;
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
    height: 3px;
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
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.stDataFrame tr:nth-child(even) {
    background: rgba(0, 0, 0, 0.05);
}
.stDataFrame tr:hover {
    background: var(--hover);
}

/* Graffiti Theme */
.theme-graffiti h2 {
    animation: bounce 2s infinite;
}

/* Content Padding for Fixed Navbar */
.content {
    padding-top: 36px; /* Reduced from 44px */
}
</style>
"""

# Function to apply theme
def apply_theme(theme):
    st.markdown(f"""
        <style>
            [data-testid="stAppViewContainer"] {{ 
                background: {'#F5F7FA' if theme == 'light' else 
                            '#1A202C' if theme == 'dark' else 
                            '#000000' if theme == 'black' else 
                            '#0E1B3D' if theme == 'blue' else 
                            '#3C1A00' if theme == 'orange' else 
                            'linear-gradient(135deg, #FF0066, #00FFCC, #FFCC00, #FF0066)'} !important;
                background-size: {'200% 200%' if theme == 'graffiti' else 'auto'};
                animation: {'gradientShift 8s ease infinite' if theme == 'graffiti' else 'none'};
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
                background: {'rgba(255, 255, 255, 0.9)' if theme == 'light' or theme == 'graffiti' else 
                            'rgba(45, 55, 72, 0.9)' if theme == 'dark' else 
                            'rgba(26, 32, 44, 0.9)' if theme == 'black' else 
                            'rgba(44, 82, 130, 0.9)' if theme == 'blue' else 
                            'rgba(124, 45, 18, 0.9)'};
            }}
            .navbar {{
                background: {'rgba(255, 255, 255, 0.9)' if theme == 'light' else 
                            'rgba(45, 55, 72, 0.9)' if theme == 'dark' else 
                            'rgba(26, 32, 44, 0.9)' if theme == 'black' else 
                            'rgba(44, 82, 130, 0.9)' if theme == 'blue' else 
                            'rgba(124, 45, 18, 0.9)' if theme == 'orange' else 
                            'rgba(255, 255, 255, 0.85)'};
            }}
            .theme-{theme} {{ --accent: {'#4A5568' if theme == 'light' else '#A0AEC0' if theme == 'dark' else '#CBD5E0' if theme == 'black' else '#90CDF4' if theme == 'blue' else '#F6AD55' if theme == 'orange' else '#FFFFFF'}; }}
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

def get_leaderboard_data(username):
    user_tracks = get_top_tracks(username, limit=50)
    user_albums = get_top_albums(username, limit=50)
    user_artists = get_top_artists(username, limit=50)
    
    if user_tracks.empty and user_albums.empty and user_artists.empty:
        return None, None, None
    
    user_scrobbles = {
        "tracks": user_tracks["Playcount"].sum() if not user_tracks.empty else 0,
        "albums": user_albums["Playcount"].sum() if not user_albums.empty else 0,
        "artists": user_artists["Playcount"].sum() if not user_artists.empty else 0
    }
    total_user_scrobbles = sum(user_scrobbles.values())

    friends_data = pd.DataFrame({
        "User": ["Friend1", "Friend2", "Friend3", username],
        "Tracks": [int(user_scrobbles["tracks"] * 0.8), int(user_scrobbles["tracks"] * 0.6), 
                   int(user_scrobbles["tracks"] * 1.2), user_scrobbles["tracks"]],
        "Albums": [int(user_scrobbles["albums"] * 0.9), int(user_scrobbles["albums"] * 0.7), 
                   int(user_scrobbles["albums"] * 1.1), user_scrobbles["albums"]],
        "Artists": [int(user_scrobbles["artists"] * 0.85), int(user_scrobbles["artists"] * 0.65), 
                    int(user_scrobbles["artists"] * 1.15), user_scrobbles["artists"]],
        "Total": [0, 0, 0, total_user_scrobbles]
    })
    friends_data["Total"] = friends_data[["Tracks", "Albums", "Artists"]].sum(axis=1)

    world_data = pd.DataFrame({
        "Entity": user_artists["Artist"].tolist()[:5] + ["Global Average"],
        "Tracks": [user_scrobbles["tracks"]] * 5 + [user_scrobbles["tracks"] * 2],
        "Albums": [user_scrobbles["albums"]] * 5 + [user_scrobbles["albums"] * 1.8],
        "Artists": [user_scrobbles["artists"]] * 5 + [user_scrobbles["artists"] * 2.2],
        "Total": [total_user_scrobbles] * 5 + [total_user_scrobbles * 2]
    })

    now = datetime.utcnow()
    current_week_start = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second)
    last_month_start = current_week_start - timedelta(days=30)
    last_month_end = current_week_start - timedelta(seconds=1)

    current_data = fetch_lastfm_data("user.getRecentTracks", username, limit=200, 
                                    from_ts=int(current_week_start.timestamp()), 
                                    to_ts=int(now.timestamp()))
    past_data = fetch_lastfm_data("user.getRecentTracks", username, limit=200, 
                                 from_ts=int(last_month_start.timestamp()), 
                                 to_ts=int(last_month_end.timestamp()))

    past_df = []
    if current_data and "recenttracks" in current_data:
        tracks = current_data["recenttracks"]["track"]
        artists = len(set(t["artist"]["#text"] for t in tracks if "artist" in t))
        albums = len(set(t.get("album", {}).get("#text", "Unknown") for t in tracks if t.get("album")))
        track_count = len(tracks)
        past_df.append({
            "Period": "This Week",
            "Tracks": track_count,
            "Albums": albums,
            "Artists": artists,
            "Total": track_count
        })
    else:
        past_df.append({"Period": "This Week", "Tracks": 0, "Albums": 0, "Artists": 0, "Total": 0})
    
    if past_data and "recenttracks" in past_data:
        tracks = past_data["recenttracks"]["track"]
        artists = len(set(t["artist"]["#text"] for t in tracks if "artist" in t))
        albums = len(set(t.get("album", {}).get("#text", "Unknown") for t in tracks if t.get("album")))
        track_count = len(tracks)
        past_df.append({
            "Period": "Last Month",
            "Tracks": track_count,
            "Albums": albums,
            "Artists": artists,
            "Total": track_count
        })
    else:
        past_df.append({"Period": "Last Month", "Tracks": 0, "Albums": 0, "Artists": 0, "Total": 0})

    return friends_data, world_data, pd.DataFrame(past_df)

# Streamlit app
st.set_page_config(page_title="Last.fm Dashboard", layout="wide")
st.markdown(custom_css, unsafe_allow_html=True)

# Session state
if "username" not in st.session_state:
    st.session_state.username = ""
if "period" not in st.session_state:
    st.session_state.period = "overall"
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Navbar with columns for username, period, theme
st.markdown("<div class='navbar'>", unsafe_allow_html=True)
st.markdown("<div class='navbar-controls'>", unsafe_allow_html=True)

# Use columns for layout
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("""
        <div class='navbar-item'>
            <svg width='10' height='10' viewBox='0 0 24 24' fill='none' title='Username'>
                <path d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/>
            </svg>
        </div>
    """, unsafe_allow_html=True)
    username = st.text_input("Username", value=st.session_state.username, placeholder="Username", label_visibility="collapsed", key="nav_username")
    if username != st.session_state.username:
        st.session_state.username = username

with col2:
    st.markdown("""
        <div class='navbar-item'>
            <svg width='10' height='10' viewBox='0 0 24 24' fill='none' title='Time Range'>
                <path d='M12 2a10 10 0 100 20 10 10 0 000-20zm0 2c4.41 0 8 3.59 8 8s-3.59 8-8 8-8-3.59-8-8 3.59-8 8-8zm-.5 3v5h1V7h-1zm0 6h1v1h-1v-1z'/>
            </svg>
        </div>
    """, unsafe_allow_html=True)
    period = st.selectbox("Time Range", ["overall", "7day", "1month", "3month", "6month", "12month"], index=["overall", "7day", "1month", "3month", "6month", "12month"].index(st.session_state.period), label_visibility="collapsed", key="nav_period")
    if period != st.session_state.period:
        st.session_state.period = period

with col3:
    st.markdown("""
        <div class='navbar-item'>
            <svg width='10' height='10' viewBox='0 0 24 24' fill='none' title='Theme'>
                <path d='M12 4a8 8 0 100 16 8 8 0 000-16zm0 2a6 6 0 110 12 6 6 0 010-12zm-1 2h2v6h-2V8zm0 7h2v2h-2v-2z'/>
            </svg>
        </div>
    """, unsafe_allow_html=True)
    theme = st.selectbox("Theme", ["light", "dark", "black", "blue", "orange", "graffiti"], index=["light", "dark", "black", "blue", "orange", "graffiti"].index(st.session_state.theme), label_visibility="collapsed", key="nav_theme")
    if theme != st.session_state.theme:
        st.session_state.theme = theme

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Apply theme
apply_theme(st.session_state.theme)

# Main content
st.markdown("<div class='content'>", unsafe_allow_html=True)

if not st.session_state.username:
    st.markdown("<div class='error-card'>Please enter a Last.fm username in the navbar.</div>", unsafe_allow_html=True)
else:
    if not check_user_exists(st.session_state.username):
        st.markdown("<div class='error-card'>No user exists with that username.</div>", unsafe_allow_html=True)
    else:
        with st.spinner("Fetching data..."):
            # Fetch data
            top_artists_df = get_top_artists(st.session_state.username, limit=10, period=st.session_state.period)
            top_tracks_df = get_top_tracks(st.session_state.username, limit=10, period=st.session_state.period)
            top_albums_df = get_top_albums(st.session_state.username, limit=10, period=st.session_state.period)
            recent_tracks_df = get_recent_tracks(st.session_state.username, limit=10)
            heatmap_df = get_listening_heatmap(st.session_state.username)
            weekly_comparison = get_weekly_comparison(st.session_state.username)
            decades_df = get_top_decades(st.session_state.username)
            friends_df, world_df, past_df = get_leaderboard_data(st.session_state.username)

            # Theme-specific chart colors
            theme_colors = {
                "light": "Blues",
                "dark": "Viridis",
                "black": "Inferno",
                "blue": "Cividis",
                "orange": "Oranges",
                "graffiti": "viridis"  # Changed from ["#FF0066", "#00FFCC", "#FFCC00"] to valid colorscale
            }

            # Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Tracks", "Albums", "Artists", "Leaderboard"])

            # Tab 1: Home
            with tab1:
                st.markdown("<h2>Welcome</h2>", unsafe_allow_html=True)
                st.markdown(f"Exploring <b>{st.session_state.username}</b>'s music taste", unsafe_allow_html=True)

                # Quick Facts
                st.markdown("<h3>Quick Facts</h3>", unsafe_allow_html=True)
                current = weekly_comparison["current"]
                previous = weekly_comparison["previous"]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                    st.write(f"**This Week ({weekly_comparison['current_period']})**")
                    st.write(f"🎧 Listening Time: {current['listening_time']} hours")
                    st.write(f"📊 Avg. Scrobbles/Day: {current['avg_scrobbles']}")
                    st.write(f"📅 Most Active: {current['most_active_day']['day']} ({current['most_active_day']['scrobbles']})")
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div class='quick-facts-card'>", unsafe_allow_html=True)
                    st.write(f"**Last Week ({weekly_comparison['previous_period']})**")
                    st.write(f"🎧 Listening Time: {previous['listening_time']} hours")
                    st.write(f"📊 Avg. Scrobbles/Day: {previous['avg_scrobbles']}")
                    st.write(f"📅 Most Active: {previous['most_active_day']['day']} ({previous['most_active_day']['scrobbles']})")
                    st.markdown("</div>", unsafe_allow_html=True)

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

                # Top Decades
                st.markdown("<h3>Top Decades</h3>", unsafe_allow_html=True)
                if not decades_df.empty:
                    fig_sunburst = px.sunburst(
                        decades_df,
                        path=["Decade"],
                        values="Playcount",
                        title="",
                        color="Playcount",
                        color_continuous_scale=theme_colors[st.session_state.theme]
                    )
                    fig_sunburst.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_sunburst, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No decade data available (release years may be missing).</div>", unsafe_allow_html=True)

                # Listening Activity
                if not heatmap_df.empty:
                    st.markdown("<h3>Listening Activity</h3>", unsafe_allow_html=True)
                    fig_3d = go.Figure(data=[go.Scatter3d(
                        x=heatmap_df["Hour"],
                        y=heatmap_df["Day"],
                        z=heatmap_df["Plays"],
                        mode="markers",
                        marker=dict(
                            size=8,
                            color=heatmap_df["Plays"],
                            colorscale=theme_colors[st.session_state.theme],
                            opacity=0.8
                        )
                    )])
                    fig_3d.update_layout(
                        scene=dict(
                            xaxis_title="Hour",
                            yaxis_title="Day",
                            zaxis_title="Plays"
                        ),
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_3d, use_container_width=True)

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
                            color_continuous_scale=theme_colors[st.session_state.theme],
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
                                marker=dict(colors=theme_colors[st.session_state.theme] if st.session_state.theme == "graffiti" else px.colors.qualitative.Plotly)
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
                        color_continuous_scale=theme_colors[st.session_state.theme],
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
                        color_continuous_scale=theme_colors[st.session_state.theme]
                    )
                    fig_artists.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_artists, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No top artists data available.</div>", unsafe_allow_html=True)

            # Tab 5: Leaderboard
            with tab5:
                st.markdown("<h2>Leaderboard</h2>", unsafe_allow_html=True)

                # Friends Comparison
                st.markdown("<h3>Vs. Friends</h3>", unsafe_allow_html=True)
                if friends_df is not None and not friends_df.empty:
                    st.dataframe(friends_df[["User", "Tracks", "Albums", "Artists", "Total"]], use_container_width=True)
                    fig_friends = go.Figure(data=[
                        go.Bar(name="Tracks", x=friends_df["User"], y=friends_df["Tracks"]),
                        go.Bar(name="Albums", x=friends_df["User"], y=friends_df["Albums"]),
                        go.Bar(name="Artists", x=friends_df["User"], y=friends_df["Artists"])
                    ])
                    fig_friends.update_layout(
                        barmode="group",
                        title="",
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_friends, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No friends data available.</div>", unsafe_allow_html=True)

                # World Comparison
                st.markdown("<h3>Vs. World</h3>", unsafe_allow_html=True)
                if world_df is not None and not world_df.empty:
                    fig_world = px.treemap(
                        world_df,
                        path=["Entity"],
                        values="Total",
                        title="",
                        color="Total",
                        color_continuous_scale=theme_colors[st.session_state.theme]
                    )
                    fig_world.update_layout(
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_world, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No global data available.</div>", unsafe_allow_html=True)

                # Past Comparison
                st.markdown("<h3>Vs. Your Past</h3>", unsafe_allow_html=True)
                if past_df is not None and not past_df.empty:
                    st.dataframe(past_df, use_container_width=True)
                    fig_past = go.Figure(data=[
                        go.Scatter(
                            x=past_df["Period"],
                            y=past_df["Tracks"],
                            mode="lines+markers",
                            name="Tracks",
                            line=dict(color="#FF0066" if st.session_state.theme == "graffiti" else "#1f77b4")
                        ),
                        go.Scatter(
                            x=past_df["Period"],
                            y=past_df["Albums"],
                            mode="lines+markers",
                            name="Albums",
                            line=dict(color="#00FFCC" if st.session_state.theme == "graffiti" else "#ff7f0e")
                        ),
                        go.Scatter(
                            x=past_df["Period"],
                            y=past_df["Artists"],
                            mode="lines+markers",
                            name="Artists",
                            line=dict(color="#FFCC00" if st.session_state.theme == "graffiti" else "#2ca02c")
                        )
                    ])
                    fig_past.update_layout(
                        title="",
                        margin=dict(l=20, r=20, t=20, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_past, use_container_width=True)
                else:
                    st.markdown("<div class='error-card'>No past data available.</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; padding: 16px; color: var(--text); opacity: 0.7;'>
        Built with ❤️ using Streamlit & Last.fm API
    </div>
""", unsafe_allow_html=True)