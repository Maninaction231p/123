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
API_KEY = "5fa9b4f47365a06fc995f1c83fb0d621"  # Replace with your Last.fm API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Theme application
def apply_theme(theme, custom_accent, card_opacity, font_size, animation_speed):
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
            .controls {{
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

# Data fetching functions
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

def check_user_exists(username):
    data = fetch_lastfm_data("user.getInfo", username)
    return data and "user" in data

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
        return buffer, f"{username}_data_{timestamp}.zip", "application/zip"

    elif format_type == "json":
        export_data = {name: df.to_dict(orient="records") for name, df in datasets.items() if not df.empty}
        buffer = io.BytesIO()
        buffer.write(json.dumps(export_data, indent=2).encode("utf-8"))
        buffer.seek(0)
        return buffer, f"{username}_data_{timestamp}.json", "application/json"

    elif format_type == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for name, df in datasets.items():
                if not df.empty:
                    df.to_excel(writer, sheet_name=name[:31], index=False)
        buffer.seek(0)
        return buffer, f"{username}_data_{timestamp}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    elif format_type == "pbix":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, df in datasets.items():
                if not df.empty:
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    zf.writestr(f"{name}.csv", csv_buffer.getvalue())
        buffer.seek(0)
        return buffer, f"{username}_powerbi_{timestamp}.zip", "application/zip"

    elif format_type == "twb":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, df in datasets.items():
                if not df.empty:
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    zf.writestr(f"{name}.csv", csv_buffer.getvalue())
            twb_content = f"""
                <?xml version='1.0' encoding='utf-8' ?>
                <workbook>
                    <datasources>
                        {''.join([f'<datasource name="{name}"><connection class="csv" file="{name}.csv"/></datasource>' for name in datasets if not datasets[name].empty])}
                    </datasources>
                </workbook>
            """
            zf.writestr(f"{username}_tableau.twb", twb_content)
        buffer.seek(0)
        return buffer, f"{username}_tableau_{timestamp}.zip", "application/zip"

    elif format_type == "txt":
        buffer = io.StringIO()
        for name, df in datasets.items():
            if not df.empty:
                buffer.write(f"\nDataset: {name}\n")
                buffer.write(df.to_string(index=False))
                buffer.write("\n" + "="*50 + "\n")
        txt_buffer = io.BytesIO(buffer.getvalue().encode("utf-8"))
        return txt_buffer, f"{username}_data_{timestamp}.txt", "text/plain"

    return None, None, None