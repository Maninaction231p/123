from flask import Flask, render_template, request, session, send_file, Response
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import io

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Replace with a secure key

# Last.fm API configuration
API_KEY = "5fa9b4f47365a06fc995f1c83fb0d621"  # Replace with your Last.fm API key
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Theme classes
theme_classes = {
    'light': {
        'bg': 'bg-gradient-to-br from-gray-100 to-gray-200',
        'text': 'text-gray-800',
        'card': 'glass bg-white/85',
        'accent': 'text-indigo-600',
        'hover': 'hover:bg-indigo-50',
        'border': 'border-indigo-200',
        'btn': 'bg-indigo-600 text-white hover:bg-indigo-700',
        'progress': 'bg-indigo-600',
        'chart_bg': 'rgba(255, 255, 255, 0.9)',
        'chart_text': 'rgba(55, 65, 81, 1)',
        'chart_accent': 'rgba(79, 70, 229, 1)'
    },
    'dark': {
        'bg': 'bg-gradient-to-br from-gray-800 to-gray-900',
        'text': 'text-gray-100',
        'card': 'glass bg-gray-800/75',
        'accent': 'text-teal-300',
        'hover': 'hover:bg-teal-900',
        'border': 'border-teal-600',
        'btn': 'bg-teal-500 text-white hover:bg-teal-600',
        'progress': 'bg-teal-500',
        'chart_bg': 'rgba(31, 41, 55, 0.9)',
        'chart_text': 'rgba(229, 231, 235, 1)',
        'chart_accent': 'rgba(45, 212, 191, 1)'
    },
    'black': {
        'bg': 'bg-gradient-to-br from-black to-gray-950',
        'text': 'text-white',
        'card': 'glass bg-gray-900/80',
        'accent': 'text-purple-300',
        'hover': 'hover:bg-purple-900',
        'border': 'border-purple-600',
        'btn': 'bg-purple-500 text-white hover:bg-purple-600',
        'progress': 'bg-purple-500',
        'chart_bg': 'rgba(17, 24, 39, 0.9)',
        'chart_text': 'rgba(255, 255, 255, 1)',
        'chart_accent': 'rgba(168, 85, 247, 1)'
    },
    'blue': {
        'bg': 'bg-gradient-to-br from-blue-900 to-blue-950',
        'text': 'text-blue-100',
        'card': 'glass bg-blue-800/75',
        'accent': 'text-cyan-300',
        'hover': 'hover:bg-cyan-900',
        'border': 'border-cyan-600',
        'btn': 'bg-cyan-500 text-white hover:bg-cyan-600',
        'progress': 'bg-cyan-500',
        'chart_bg': 'rgba(30, 58, 138, 0.9)',
        'chart_text': 'rgba(224, 231, 255, 1)',
        'chart_accent': 'rgba(6, 182, 212, 1)'
    },
    'orange': {
        'bg': 'bg-gradient-to-br from-orange-900 to-orange-950',
        'text': 'text-orange-100',
        'card': 'glass bg-orange-800/75',
        'accent': 'text-amber-300',
        'hover': 'hover:bg-amber-900',
        'border': 'border-amber-600',
        'btn': 'bg-amber-500 text-white hover:bg-amber-600',
        'progress': 'bg-amber-500',
        'chart_bg': 'rgba(124, 45, 18, 0.9)',
        'chart_text': 'rgba(255, 237, 213, 1)',
        'chart_accent': 'rgba(251, 191, 36, 1)'
    },
    'graffiti': {
        'bg': 'bg-gradient-to-r from-pink-600 via-cyan-400 to-yellow-400 animate-gradient',
        'text': 'text-gray-900',
        'card': 'glass bg-white/85',
        'accent': 'text-gray-800',
        'hover': 'hover:bg-gray-200',
        'border': 'border-gray-300',
        'btn': 'bg-gray-800 text-white hover:bg-gray-900',
        'progress': 'bg-gray-800',
        'chart_bg': 'rgba(255, 255, 255, 0.9)',
        'chart_text': 'rgba(17, 24, 39, 1)',
        'chart_accent': 'rgba(31, 41, 55, 1)'
    }
}

# Data fetching functions
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

def get_recent_tracks(username, limit=10, export_all=False):
    if export_all:
        all_tracks = []
        page = 1
        limit_per_page = 200
        while True:
            data = fetch_lastfm_data("user.getRecentTracks", username, limit=limit_per_page, page=page)
            if not data or "recenttracks" not in data:
                break
            tracks = data["recenttracks"]["track"]
            all_tracks.extend(tracks)
            if len(tracks) < limit_per_page:
                break
            page += 1
            time.sleep(0.5)
        if all_tracks:
            return pd.DataFrame([
                {
                    "Track": track["name"],
                    "Artist": track["artist"]["#text"],
                    "Album": track.get("album", {}).get("#text", "Unknown"),
                    "Date": track.get("date", {}).get("#text", "Now Playing") if "date" in track else "Now Playing"
                }
                for track in all_tracks
            ])
        return pd.DataFrame()
    else:
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

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize session
    if "username" not in session:
        session["username"] = ""
    if "period" not in session:
        session["period"] = "overall"
    if "theme" not in session:
        session["theme"] = "black"  # Default to black

    # Handle form submissions
    loading = False
    if request.method == "POST":
        session["username"] = request.form.get("username", "")
        session["period"] = request.form.get("period", "overall")
        session["theme"] = request.form.get("theme", "black")
        loading = True

    username = session["username"]
    period = session["period"]
    theme = session["theme"]

    error = None
    data = {
        "top_artists_df": [],
        "top_tracks_df": [],
        "top_albums_df": [],
        "recent_tracks_df": [],
        "heatmap_df": [],
        "weekly_comparison": {"current": {}, "previous": {}, "current_period": "", "previous_period": ""},
        "decades_df": [],
        "friends_df": [],
        "world_df": [],
        "past_df": [],
        "now_playing": None,
        "chart_data": {}
    }

    if username:
        if not check_user_exists(username):
            error = "No user exists with that username."
            loading = False
        else:
            # Fetch data
            top_artists_df = get_top_artists(username, limit=10, period=period)
            top_tracks_df = get_top_tracks(username, limit=10, period=period)
            top_albums_df = get_top_albums(username, limit=10, period=period)
            recent_tracks_df = get_recent_tracks(username, limit=10)
            heatmap_df = get_listening_heatmap(username)
            weekly_comparison = get_weekly_comparison(username)
            decades_df = get_top_decades(username)
            friends_df, world_df, past_df = get_leaderboard_data(username)

            # Convert DataFrames to lists for template
            data["top_artists_df"] = top_artists_df.to_dict("records") if not top_artists_df.empty else []
            data["top_tracks_df"] = top_tracks_df.to_dict("records") if not top_tracks_df.empty else []
            data["top_albums_df"] = top_albums_df.to_dict("records") if not top_albums_df.empty else []
            data["recent_tracks_df"] = recent_tracks_df.to_dict("records") if not recent_tracks_df.empty else []
            data["heatmap_df"] = heatmap_df.to_dict("records") if not heatmap_df.empty else []
            data["weekly_comparison"] = weekly_comparison
            data["decades_df"] = decades_df.to_dict("records") if not decades_df.empty else []
            data["friends_df"] = friends_df.to_dict("records") if friends_df is not None and not friends_df.empty else []
            data["world_df"] = world_df.to_dict("records") if world_df is not None and not world_df.empty else []
            data["past_df"] = past_df.to_dict("records") if past_df is not None and not past_df.empty else []

            # Now Playing
            if not recent_tracks_df.empty and "Now Playing" in recent_tracks_df["Date"].values:
                data["now_playing"] = recent_tracks_df[recent_tracks_df["Date"] == "Now Playing"].iloc[0].to_dict()

            # Chart data for Chart.js and ApexCharts
            chart_data = {}
            if not top_tracks_df.empty:
                chart_data["tracks"] = {
                    "labels": top_tracks_df["Track"].tolist(),
                    "data": top_tracks_df["Playcount"].tolist(),
                    "artists": top_tracks_df["Artist"].tolist()
                }
            if not top_albums_df.empty:
                chart_data["albums"] = {
                    "labels": top_albums_df["Album"].tolist(),
                    "data": top_albums_df["Playcount"].tolist(),
                    "artists": top_albums_df["Artist"].tolist()
                }
            if not top_artists_df.empty:
                chart_data["artists"] = {
                    "labels": top_artists_df["Artist"].tolist(),
                    "data": top_artists_df["Playcount"].tolist()
                }
            if not recent_tracks_df.empty:
                artist_counts = recent_tracks_df["Artist"].value_counts().reset_index()
                artist_counts.columns = ["Artist", "Count"]
                chart_data["recent"] = {
                    "labels": artist_counts["Artist"].tolist(),
                    "data": artist_counts["Count"].tolist()
                }
            if not decades_df.empty:
                chart_data["decades"] = {
                    "labels": decades_df["Decade"].tolist(),
                    "data": decades_df["Playcount"].tolist()
                }
            if not heatmap_df.empty:
                chart_data["heatmap"] = {
                    "days": heatmap_df["Day"].tolist(),
                    "hours": heatmap_df["Hour"].tolist(),
                    "plays": heatmap_df["Plays"].tolist()
                }
            if friends_df is not None and not friends_df.empty:
                chart_data["friends"] = {
                    "users": friends_df["User"].tolist(),
                    "tracks": friends_df["Tracks"].tolist(),
                    "albums": friends_df["Albums"].tolist(),
                    "artists": friends_df["Artists"].tolist()
                }
            if world_df is not None and not world_df.empty:
                chart_data["world"] = {
                    "entities": world_df["Entity"].tolist(),
                    "total": world_df["Total"].tolist()
                }
            if past_df is not None and not past_df.empty:
                chart_data["past"] = {
                    "periods": past_df["Period"].tolist(),
                    "tracks": past_df["Tracks"].tolist(),
                    "albums": past_df["Albums"].tolist(),
                    "artists": past_df["Artists"].tolist()
                }
            data["chart_data"] = chart_data
            loading = False

    return render_template(
        "index.html",
        username=username,
        period=period,
        theme=theme,
        error=error,
        data=data,
        theme_classes=theme_classes,
        loading=loading
    )

@app.route("/export")
def export():
    username = session.get("username", "")
    if not username or not check_user_exists(username):
        return Response("No valid username provided.", status=400)
    
    export_df = get_recent_tracks(username, export_all=True)
    if export_df.empty:
        return Response("No scrobbles available to export.", status=400)
    
    csv_buffer = io.StringIO()
    export_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    return send_file(
        io.BytesIO(csv_data.encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{username}_scrobbles.csv"
    )

if __name__ == "__main__":
    app.run(debug=True)