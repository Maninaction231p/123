import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
import base64
import time

# Last.fm API credentials
API_KEY = "753fc4d46f7cca298471985943b54e4a"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# Fetch scrobbles from Last.fm
def fetch_scrobbles(username, limit=1000):
    page = 1
    total_pages = 1
    all_scrobbles = []

    progress_bar = st.progress(0)
    progress_text = st.empty()

    while page <= total_pages:
        data = requests.get(
            BASE_URL,
            params={
                "method": "user.getrecenttracks",
                "user": username,
                "api_key": API_KEY,
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