import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
import base64
import time
from PIL import Image
from io import BytesIO

# Last.fm and Discogs API credentials
LASTFM_API_KEY = "753fc4d46f7cca298471985943b54e4a"
DISCOGS_API_KEY = "TcITSWbkmvuHBAcFznWn"

BASE_URL_LASTFM = "http://ws.audioscrobbler.com/2.0/"
BASE_URL_DISCOGS = "https://api.discogs.com/database/search"

# Fetch scrobbles from Last.fm
def fetch_scrobbles(username, limit=1000):
    page = 1
    total_pages = 1
    all_scrobbles = []

    progress_bar = st.progress(0)
    progress_text = st.empty()

    while page <= total_pages:
        data = requests.get(
            BASE_URL_LASTFM,
            params={
                "method": "user.getrecenttracks",
                "user": username,
                "api_key": LASTFM_API_KEY,
                "format": "json",
                "limit": 200,
                "page": page,
            },
        ).json()

        if "error" in data:
            st.error(f"Error: {data['message']}")
            return None

        scrobbles = data["recenttracks"]["track"]
        total_pages = int(data["recenttracks"]["@attr"]["totalPages"])

        all_scrobbles.extend(scrobbles)
        progress = page / total_pages
        progress_bar.progress(progress)
        progress_text.text(f"Fetching page {page}/{total_pages} ({progress:.1%})")
        page += 1
        time.sleep(0.5)  # Avoid hitting rate limits

    progress_text.empty()
    return all_scrobbles


# Process raw scrobble data into a DataFrame
def process_scrobbles(raw_scrobbles):
    processed = []
    for track in raw_scrobbles:
        if not track.get("date"):  # Skip currently playing track
            continue

        processed.append(
            {
                "artist": track["artist"]["#text"],
                "track": track["name"],
                "album": track["album"]["#text"],
                "timestamp": datetime.utcfromtimestamp(int(track["date"]["uts"])),
                "image_url": track["image"][-1]["#text"] if track["image"] else None,
            }
        )
    return pd.DataFrame(processed)


# Fetch album art from Discogs API
def fetch_album_art(artist, album):
    response = requests.get(
        BASE_URL_DISCOGS,
        params={
            "artist": artist,
            "release_title": album,
            "key": DISCOGS_API_KEY,
            "format": "json",
        },
    ).json()

    if response.get("results"):
        return response["results"][0]["cover_image"]
    return None


# Generate recommendations using cosine similarity
def get_recommendations(df):
    top_artists = df["artist"].value_counts().head(10).index
    artist_matrix = pd.get_dummies(df["artist"]).groupby(df["track"]).sum()
    similarities = cosine_similarity(artist_matrix)
    sim_df = pd.DataFrame(similarities, index=artist_matrix.index, columns=artist_matrix.index)

    recommendations = {}
    for track in df["track"].unique():
        if track in sim_df:
            recommendations[track] = sim_df[track].sort_values(ascending=False).index[1:4].tolist()
    return recommendations


# Find forgotten tracks (tracks not listened to in a long time)
def find_forgotten_tracks(df, threshold_days=365):
    latest_listen = df.groupby("track")["timestamp"].max()
    forgotten_tracks = latest_listen[
        (datetime.utcnow() - latest_listen).dt.days > threshold_days
    ]
    return forgotten_tracks.sort_values()


# Display a mini-game during loading
def display_mini_game():
    html_content = """
    <div style="text-align:center; margin-top:20px;">
        <canvas id="dinoGame" width="400" height="200"></canvas>
        <script>
            const canvas = document.getElementById('dinoGame');
            const ctx = canvas.getContext('2d');

            let dino = { x: 50, y: 150, width: 20, height: 20, dy: 0, jumping: false };
            let obstacles = [];
            let score = 0;
            let gameOver = false;

            function drawDino() {
                ctx.fillStyle = 'green';
                ctx.fillRect(dino.x, dino.y, dino.width, dino.height);
            }

            function updateDino() {
                if (dino.jumping) {
                    dino.y += dino.dy;
                    dino.dy += 0.5;
                    if (dino.y >= 150) {
                        dino.y = 150;
                        dino.jumping = false;
                        dino.dy = 0;
                    }
                }
            }

            function spawnObstacle() {
                if (Math.random() < 0.02) {
                    obstacles.push({ x: 400, y: 150, width: 20, height: 20 });
                }
            }

            function drawObstacles() {
                ctx.fillStyle = 'red';
                obstacles.forEach(obstacle => {
                    obstacle.x -= 2;
                    ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
                });
            }

            function checkCollision() {
                obstacles.forEach(obstacle => {
                    if (dino.x < obstacle.x + obstacle.width &&
                        dino.x + dino.width > obstacle.x &&
                        dino.y < obstacle.y + obstacle.height &&
                        dino.y + dino.height > obstacle.y) {
                        gameOver = true;
                    }
                });
            }

            function updateScore() {
                score++;
                document.getElementById('score').innerText = `Score: ${score}`;
            }

            function gameLoop() {
                if (gameOver) return;
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawDino();
                updateDino();
                spawnObstacle();
                drawObstacles();
                checkCollision();
                updateScore();
                requestAnimationFrame(gameLoop);
            }

            document.addEventListener('keydown', () => {
                if (!dino.jumping) {
                    dino.jumping = true;
                    dino.dy = -7;
                }
            });

            gameLoop();
        </script>
        <p id="score">Score: 0</p>
    </div>
    """
    st.components.v1.html(html_content, height=300)


# Main app
def main():
    st.title("Last.fm Listening Insights")
    st.sidebar.header("User Input")

    # User inputs
    username = st.sidebar.text_input("Last.fm Username", "Boogeyman231p")
    theme = st.sidebar.selectbox("Theme", ["Light", "Dark", "System"])
    export_format = st.sidebar.selectbox("Export Format", ["CSV", "Excel", "TXT"])

    # Theme configuration
    if theme == "Dark":
        st.markdown(
            """
            <style>
            body { color: white; background-color: #1a1a1a; }
            .sidebar .sidebar-content { background-color: #2a2a2a; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    elif theme == "Light":
        st.markdown(
            """
            <style>
            body { color: black; background-color: white; }
            .sidebar .sidebar-content { background-color: #f0f0f0; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Generate insights button
    if st.sidebar.button("Generate Insights"):
        with st.spinner("Fetching scrobble data..."):
            raw_scrobbles = fetch_scrobbles(username)
            if not raw_scrobbles:
                return
            df = process_scrobbles(raw_scrobbles)

        # Show mini-game while processing
        display_mini_game()

        # Fill missing images
        st.write("Filling missing album art...")
        for idx, row in df.iterrows():
            if pd.isna(row["image_url"]) or not row["image_url"]:
                image_url = fetch_album_art(row["artist"], row["album"])
                df.at[idx, "image_url"] = image_url

        # Overview metrics
        st.header("Listening Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Scrobbles", len(df))
        col2.metric("Unique Artists", df["artist"].nunique())
        col3.metric("Unique Tracks", df["track"].nunique())

        # Listening activity by hour
        df["hour"] = df["timestamp"].dt.hour
        fig_hour = px.histogram(
            df,
            x="hour",
            title="Listening Activity by Hour",
            labels={"hour": "Hour of Day"},
            nbins=24,
        )
        st.plotly_chart(fig_hour, use_container_width=True)

        # Top artists
        top_artists = df["artist"].value_counts().head(10)
        fig_artist = go.Figure(go.Bar(x=top_artists.index, y=top_artists.values))
        fig_artist.update_layout(title="Top 10 Artists", xaxis_title="Artist", yaxis_title="Scrobbles")
        st.plotly_chart(fig_artist, use_container_width=True)

        # Listening trends over time
        df["date"] = df["timestamp"].dt.date
        listening_trends = df.groupby("date").size().reset_index(name="scrobbles")
        fig_trends = px.line(
            listening_trends,
            x="date",
            y="scrobbles",
            title="Daily Listening Trends",
            labels={"scrobbles": "Scrobbles", "date": "Date"},
        )
        st.plotly_chart(fig_trends, use_container_width=True)

        # Recommendations
        st.header("Track Recommendations")
        recommendations = get_recommendations(df)
        for track, recs in list(recommendations.items())[:5]:
            st.write(f"**{track}** might like: {', '.join(recs)}")

        # Forgotten tracks
        st.header("Forgotten Tracks")
        forgotten_tracks = find_forgotten_tracks(df)
        if forgotten_tracks.empty:
            st.write("No forgotten tracks found!")
        else:
            st.write(forgotten_tracks.reset_index().rename(columns={"index": "Track", "timestamp": "Last Listened"}))

        # Export options
        st.sidebar.header("Export Data")
        if export_format == "CSV":
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="scrobbles.csv">Download CSV</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
        elif export_format == "Excel":
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False)
            excel_data = output.getvalue()
            b64 = base64.b64encode(excel_data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="scrobbles.xlsx">Download Excel</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)
        elif export_format == "TXT":
            txt = df.to_string(index=False)
            b64 = base64.b64encode(txt.encode()).decode()
            href = f'<a href="data:text/plain;base64,{b64}" download="scrobbles.txt">Download TXT</a>'
            st.sidebar.markdown(href, unsafe_allow_html=True)


if __name__ == "__main__":
    main()