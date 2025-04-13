import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import datetime
import calendar
import base64

# Set page configuration
st.set_page_config(
    page_title="Last.fm Insights",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API constants
API_KEY = "5fa9b4f47365a06fc995f1c83fb0d621"  # You need to get this from Last.fm
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# App styling
def set_theme():
    # Set up light/dark mode
    theme = st.sidebar.selectbox("Select Theme", ["Light", "Dark"], index=1)
    
    if theme == "Dark":
        # Apply dark theme
        st.markdown("""
        <style>
        .main {
            background-color: #121212;
            color: #ffffff;
        }
        .stApp {
            background-color: #121212;
        }
        .st-bw {
            background-color: #1e1e1e;
        }
        .st-c0 {
            color: #ffffff;
        }
        .stTextInput, .stSelectbox, .stDateInput {
            background-color: #2a2a2a;
            color: #ffffff;
        }
        .stMarkdown {
            color: #ffffff;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Apply light theme
        st.markdown("""
        <style>
        .main {
            background-color: #ffffff;
            color: #000000;
        }
        .stApp {
            background-color: #ffffff;
        }
        .st-bw {
            background-color: #f0f2f6;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    return theme

# Helper functions
def fetch_user_info(username):
    """Fetch basic user info from Last.fm API"""
    params = {
        'method': 'user.getinfo',
        'user': username,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching user info: {response.status_code}")
        return None

def fetch_top_artists(username, period='overall', limit=10):
    """Fetch top artists from Last.fm API"""
    params = {
        'method': 'user.gettopartists',
        'user': username,
        'period': period,
        'limit': limit,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching top artists: {response.status_code}")
        return None

def fetch_top_tracks(username, period='overall', limit=10):
    """Fetch top tracks from Last.fm API"""
    params = {
        'method': 'user.gettoptracks',
        'user': username,
        'period': period,
        'limit': limit,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching top tracks: {response.status_code}")
        return None

def fetch_top_albums(username, period='overall', limit=10):
    """Fetch top albums from Last.fm API"""
    params = {
        'method': 'user.gettopalbums',
        'user': username,
        'period': period,
        'limit': limit,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching top albums: {response.status_code}")
        return None

def fetch_recent_tracks(username, limit=50):
    """Fetch recent tracks from Last.fm API"""
    params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'limit': limit,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching recent tracks: {response.status_code}")
        return None

def fetch_weekly_chart_list(username):
    """Fetch available charts for a user"""
    params = {
        'method': 'user.getweeklychartlist',
        'user': username,
        'api_key': API_KEY,
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching weekly chart list: {response.status_code}")
        return None

def fetch_all_scrobbles(username):
    """Fetch all scrobbles for a user (this will take time for large libraries)"""
    all_tracks = []
    page = 1
    total_pages = 1
    
    with st.spinner('Fetching your listening history... This may take a while for large libraries.'):
        progress_bar = st.progress(0)
        
        while page <= total_pages:
            params = {
                'method': 'user.getrecenttracks',
                'user': username,
                'page': page,
                'limit': 200,  # Max allowed by API
                'api_key': API_KEY,
                'format': 'json'
            }
            
            response = requests.get(BASE_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if page == 1:
                    total_pages = int(data['recenttracks']['@attr']['totalPages'])
                    st.info(f"Found {data['recenttracks']['@attr']['total']} tracks across {total_pages} pages")
                
                # Add tracks from this page
                if 'track' in data['recenttracks']:
                    for track in data['recenttracks']['track']:
                        # Skip now playing track
                        if '@attr' in track and 'nowplaying' in track['@attr']:
                            continue
                            
                        track_data = {
                            'artist': track['artist']['#text'],
                            'album': track['album']['#text'],
                            'track': track['name'],
                            'timestamp': int(track['date']['uts']),
                            'date': track['date']['#text']
                        }
                        all_tracks.append(track_data)
                
                # Update progress
                progress = min(page / total_pages, 1.0)
                progress_bar.progress(progress)
                
                # To avoid hitting rate limits
                if page < total_pages:
                    time.sleep(0.25)
                
                page += 1
            else:
                st.error(f"Error fetching page {page}: {response.status_code}")
                break
    
    return pd.DataFrame(all_tracks)

def get_download_link(df, file_format="csv", filename="lastfm_data"):
    """Generate a download link for the data"""
    if file_format == "csv":
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download {filename}.csv</a>'
        return href
    elif file_format == "xlsx":
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.close()
        processed_data = output.getvalue()
        b64 = base64.b64encode(processed_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Download {filename}.xlsx</a>'
        return href
    elif file_format == "txt":
        txt = df.to_csv(index=False, sep='\t')
        b64 = base64.b64encode(txt.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">Download {filename}.txt</a>'
        return href

# Dashboard components
def create_profile_section(username, user_info):
    """Create the profile overview section"""
    st.header("📊 Last.fm Insights Dashboard")
    
    if user_info:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if 'image' in user_info['user']:
                img_url = user_info['user']['image'][-1]['#text']
                if img_url:
                    st.image(img_url, width=150)
                else:
                    st.image("https://lastfm.freetls.fastly.net/i/u/300x300/818148bf682d429dc215c1705eb27b98.jpg", width=150)
        
        with col2:
            st.subheader(f"{user_info['user']['name']}'s Profile")
            st.write(f"**Real Name:** {user_info['user'].get('realname', 'Not specified')}")
            st.write(f"**Country:** {user_info['user'].get('country', 'Not specified')}")
            st.write(f"**Scrobbles:** {user_info['user']['playcount']}")
            st.write(f"**Registered:** {user_info['user']['registered']['#text']}")
            profile_url = user_info['user']['url']
            st.markdown(f"[Visit Last.fm Profile]({profile_url})")

def create_listening_trend_chart(df):
    """Create listening trend over time chart"""
    st.subheader("🕒 Listening Trends Over Time")
    
    # Add date columns for easier filtering
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['month'] = df['datetime'].dt.month
    df['year'] = df['datetime'].dt.year
    
    # Create tabs for different timeframes
    tab1, tab2, tab3, tab4 = st.tabs(["Daily", "Weekly", "Monthly", "Yearly"])
    
    with tab1:
        # Daily listening count
        daily_counts = df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        daily_counts = daily_counts.sort_values('date')
        
        fig = px.line(daily_counts, x='date', y='count', 
                     title='Daily Listening Activity',
                     labels={'count': 'Tracks Played', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Weekly pattern
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_counts = df.groupby('day_of_week').size().reset_index(name='count')
        weekly_counts['day_name'] = weekly_counts['day_of_week'].apply(lambda x: day_names[x])
        weekly_counts = weekly_counts.sort_values('day_of_week')
        
        fig = px.bar(weekly_counts, x='day_name', y='count',
                    title='Listening Activity by Day of Week',
                    labels={'count': 'Tracks Played', 'day_name': 'Day'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Monthly pattern
        month_names = [calendar.month_name[i] for i in range(1, 13)]
        monthly_counts = df.groupby('month').size().reset_index(name='count')
        monthly_counts['month_name'] = monthly_counts['month'].apply(lambda x: month_names[x-1])
        monthly_counts = monthly_counts.sort_values('month')
        
        fig = px.bar(monthly_counts, x='month_name', y='count',
                    title='Listening Activity by Month',
                    labels={'count': 'Tracks Played', 'month_name': 'Month'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Yearly pattern
        yearly_counts = df.groupby('year').size().reset_index(name='count')
        yearly_counts = yearly_counts.sort_values('year')
        
        fig = px.bar(yearly_counts, x='year', y='count',
                    title='Listening Activity by Year',
                    labels={'count': 'Tracks Played', 'year': 'Year'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily activity pattern by hour
    st.subheader("⏰ Daily Activity Pattern")
    hourly_counts = df.groupby('hour').size().reset_index(name='count')
    fig = px.bar(hourly_counts, x='hour', y='count',
                title='Listening Activity by Hour of Day',
                labels={'count': 'Tracks Played', 'hour': 'Hour of Day (24h format)'})
    st.plotly_chart(fig, use_container_width=True)

def create_top_artists_section(top_artists_data, period_name):
    """Create the top artists section"""
    st.subheader(f"🎤 Top Artists ({period_name})")
    
    if top_artists_data and 'topartists' in top_artists_data and 'artist' in top_artists_data['topartists']:
        artists = top_artists_data['topartists']['artist']
        
        if not artists:
            st.info("No top artists data available for this period.")
            return
            
        # Prepare data for chart
        artist_names = []
        play_counts = []
        
        for artist in artists:
            artist_names.append(artist['name'])
            play_counts.append(int(artist['playcount']))
        
        # Reverse lists to display highest count at the top
        artist_names.reverse()
        play_counts.reverse()
        
        # Create horizontal bar chart
        fig = go.Figure(go.Bar(
            x=play_counts,
            y=artist_names,
            orientation='h',
            marker=dict(
                color='rgba(50, 171, 96, 0.7)',
                line=dict(color='rgba(50, 171, 96, 1.0)', width=2)
            )
        ))
        
        fig.update_layout(
            title=f"Top {len(artist_names)} Artists",
            xaxis_title="Scrobbles",
            yaxis_title="Artist",
            height=400 + (len(artist_names) * 25)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create grid of artists with images (if available)
        col_count = 5
        rows = [artists[i:i+col_count] for i in range(0, len(artists), col_count)]
        
        for row in rows:
            cols = st.columns(col_count)
            for i, artist in enumerate(row):
                with cols[i]:
                    # Get the largest image available
                    img_url = artist['image'][-1]['#text'] if artist['image'] else None
                    
                    if img_url:
                        st.image(img_url, width=120)
                    else:
                        st.image("https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png", width=120)
                    
                    st.write(f"**{artist['name']}**")
                    st.write(f"{artist['playcount']} plays")
    else:
        st.info("No top artists data available.")

def create_top_tracks_section(top_tracks_data, period_name):
    """Create the top tracks section"""
    st.subheader(f"🎵 Top Tracks ({period_name})")
    
    if top_tracks_data and 'toptracks' in top_tracks_data and 'track' in top_tracks_data['toptracks']:
        tracks = top_tracks_data['toptracks']['track']
        
        if not tracks:
            st.info("No top tracks data available for this period.")
            return
            
        # Prepare data for chart
        track_names = []
        play_counts = []
        
        for track in tracks:
            # Create a label with artist name
            label = f"{track['name']} - {track['artist']['name']}"
            track_names.append(label)
            play_counts.append(int(track['playcount']))
        
        # Reverse lists to display highest count at the top
        track_names.reverse()
        play_counts.reverse()
        
        # Create horizontal bar chart
        fig = go.Figure(go.Bar(
            x=play_counts,
            y=track_names,
            orientation='h',
            marker=dict(
                color='rgba(71, 58, 131, 0.7)',
                line=dict(color='rgba(71, 58, 131, 1.0)', width=2)
            )
        ))
        
        fig.update_layout(
            title=f"Top {len(track_names)} Tracks",
            xaxis_title="Scrobbles",
            yaxis_title="Track",
            height=400 + (len(track_names) * 25)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a table of tracks
        track_data = []
        for i, track in enumerate(tracks):
            track_data.append({
                "Rank": i+1,
                "Track": track['name'],
                "Artist": track['artist']['name'],
                "Scrobbles": track['playcount'],
                "URL": track['url']
            })
        
        track_df = pd.DataFrame(track_data)
        
        # Add clickable links
        def make_clickable(url, text):
            return f'<a href="{url}" target="_blank">{text}</a>'
        
        track_df['Track'] = track_df.apply(lambda x: make_clickable(x['URL'], x['Track']), axis=1)
        track_df = track_df.drop(columns=['URL'])
        
        st.write(track_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No top tracks data available.")

def create_top_albums_section(top_albums_data, period_name):
    """Create the top albums section"""
    st.subheader(f"💿 Top Albums ({period_name})")
    
    if top_albums_data and 'topalbums' in top_albums_data and 'album' in top_albums_data['topalbums']:
        albums = top_albums_data['topalbums']['album']
        
        if not albums:
            st.info("No top albums data available for this period.")
            return
            
        # Prepare data for chart
        album_names = []
        play_counts = []
        
        for album in albums:
            # Create a label with artist name
            label = f"{album['name']} - {album['artist']['name']}"
            album_names.append(label)
            play_counts.append(int(album['playcount']))
        
        # Reverse lists to display highest count at the top
        album_names.reverse()
        play_counts.reverse()
        
        # Create horizontal bar chart
        fig = go.Figure(go.Bar(
            x=play_counts,
            y=album_names,
            orientation='h',
            marker=dict(
                color='rgba(214, 39, 40, 0.7)',
                line=dict(color='rgba(214, 39, 40, 1.0)', width=2)
            )
        ))
        
        fig.update_layout(
            title=f"Top {len(album_names)} Albums",
            xaxis_title="Scrobbles",
            yaxis_title="Album",
            height=400 + (len(album_names) * 25)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create grid of albums with images
        col_count = 5
        rows = [albums[i:i+col_count] for i in range(0, len(albums), col_count)]
        
        for row in rows:
            cols = st.columns(col_count)
            for i, album in enumerate(row):
                with cols[i]:
                    # Get the largest image available
                    img_url = album['image'][-1]['#text'] if album['image'] else None
                    
                    if img_url:
                        st.image(img_url, width=120)
                    else:
                        st.image("https://lastfm.freetls.fastly.net/i/u/300x300/c6f59c1e5e7240a4c0d427abd71f3dbb.png", width=120)
                    
                    st.write(f"**{album['name']}**")
                    st.write(f"{album['artist']['name']}")
                    st.write(f"{album['playcount']} plays")
    else:
        st.info("No top albums data available.")

def create_listening_clock(df):
    """Create a 24-hour listening clock visualization"""
    st.subheader("🕰️ Listening Clock")
    
    # Group by hour and count
    hourly_data = df.groupby('hour').size().reset_index(name='count')
    
    # Create a 24-hour clock
    fig = go.Figure()
    
    # Create a polar bar chart
    fig.add_trace(go.Barpolar(
        r=hourly_data['count'],
        theta=[i*15 for i in hourly_data['hour']],  # Convert hour to degrees (360/24 = 15 degrees per hour)
        width=15,  # Width of each bar in degrees
        marker_color=hourly_data['count'],
        marker_colorscale='Viridis',
        hoverinfo='text',
        hovertext=[f'{h}:00 - {h+1}:00: {c} tracks' for h, c in zip(hourly_data['hour'], hourly_data['count'])]
    ))
    
    # Update layout for a clock-like appearance
    fig.update_layout(
        title="24-Hour Listening Activity",
        polar=dict(
            radialaxis=dict(
                visible=True,
                type='linear',
                showticklabels=False,
                ticks='',
                range=[0, max(hourly_data['count']) * 1.1]
            ),
            angularaxis=dict(
                tickvals=[i*15 for i in range(24)],
                ticktext=[f"{i}" for i in range(24)],
                direction='clockwise',
                rotation=90
            )
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_listening_heatmap(df):
    """Create a heatmap showing listening patterns by day of week and hour"""
    st.subheader("📅 Listening Heatmap")
    
    # Group by day of week and hour
    heatmap_data = df.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
    
    # Create a pivot table for the heatmap
    pivot_data = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
    
    # Reindex to ensure all hours are present
    pivot_data = pivot_data.reindex(columns=range(24), fill_value=0)
    
    # Reindex to ensure all days are present and in correct order
    pivot_data = pivot_data.reindex(range(7), fill_value=0)
    
    # Create day labels
    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Create hour labels
    hour_labels = [f"{h}:00" for h in range(24)]
    
    # Create heatmap
    fig = px.imshow(
        pivot_data.values,
        labels=dict(x="Hour of Day", y="Day of Week", color="Tracks Played"),
        x=hour_labels,
        y=day_labels,
        title="Listening Activity by Day and Hour",
        color_continuous_scale="Viridis"
    )
    
    # Update layout for better readability
    fig.update_layout(
        xaxis=dict(
            tickangle=-45,
            title_font=dict(size=14),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_artist_diversity_chart(df):
    """Create charts showing diversity of listening"""
    st.subheader("🎭 Artist & Track Diversity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Count unique artists vs total plays
        unique_artists = df['artist'].nunique()
        total_scrobbles = len(df)
        
        # Create donut chart showing repeat vs new artists
        artist_counts = df['artist'].value_counts()
        single_play_artists = sum(artist_counts == 1)
        repeat_artists = unique_artists - single_play_artists
        
        artist_diversity = [
            {'category': 'Artists played once', 'count': single_play_artists},
            {'category': 'Artists played multiple times', 'count': repeat_artists}
        ]
        
        fig = px.pie(
            artist_diversity, 
            values='count', 
            names='category',
            title=f"Artist Diversity: {unique_artists} unique artists out of {total_scrobbles} scrobbles",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show some statistics
        st.metric("Artist Variety Ratio", f"{(unique_artists / total_scrobbles * 100):.2f}%", 
                 help="Percentage of scrobbles that are unique artists")
    
    with col2:
        # Count unique tracks vs total plays
        unique_tracks = df.groupby(['artist', 'track']).size().reset_index().shape[0]
        
        # Create donut chart showing repeat vs new tracks
        track_counts = df.groupby(['artist', 'track']).size()
        single_play_tracks = sum(track_counts == 1)
        repeat_tracks = unique_tracks - single_play_tracks
        
        track_diversity = [
            {'category': 'Tracks played once', 'count': single_play_tracks},
            {'category': 'Tracks played multiple times', 'count': repeat_tracks}
        ]
        
        fig = px.pie(
            track_diversity, 
            values='count', 
            names='category',
            title=f"Track Diversity: {unique_tracks} unique tracks out of {total_scrobbles} scrobbles",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show some statistics
        st.metric("Track Variety Ratio", f"{(unique_tracks / total_scrobbles * 100):.2f}%", 
                 help="Percentage of scrobbles that are unique tracks")

def create_export_section(df):
    """Create section for exporting data"""
    st.subheader("📤 Export Your Data")
    
    export_format = st.selectbox("Choose export format:", ["csv", "xlsx", "txt"])
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"Your data contains {len(df)} scrobbles that will be exported.")
    
    with col2:
        if st.button("Generate Download Link"):
            st.markdown(get_download_link(df, export_format, f"lastfm_scrobbles_{int(time.time())}"), unsafe_allow_html=True)

def main():
    # Set theme
    theme = set_theme()
    
    st.sidebar.image("https://www.last.fm/static/images/logo_static.png", width=200)
    st.sidebar.title("Last.fm Insights")
    
    # Username input
    username = st.sidebar.text_input("Enter Last.fm Username:", "Boogeyman231p")
    
    if st.sidebar.button("Load Data") or 'user_data' in st.session_state:
        with st.spinner("Fetching data from Last.fm..."):
            # Fetch user info
            user_info = fetch_user_info(username)
            
            if user_info:
                # Store data in session state
                if 'user_data' not in st.session_state:
                    st.session_state.user_data = {
                        'user_info': user_info,
                        'username': username
                    }
                
                create_profile_section(username, user_info)
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 Overview", 
                    "👑 Top Charts", 
                    "📈 Listening Patterns", 
                    "📊 Advanced Insights", 
                    "📤 Export Data"
                ])
                
                with tab1:
                    st.subheader("✨ Quick Overview")
                    
                    # Get recent tracks for a quick overview
                    recent_tracks = fetch_recent_tracks(username, 10)
                    
                    if recent_tracks and 'recenttracks' in recent_tracks and 'track' in recent_tracks['recenttracks']:
                        tracks = recent_tracks['recenttracks']['track']                        
                        # Check if currently playing
                        now_playing = None
                        recent_list = []
                        
                        for track in tracks:
                            if '@attr' in track and 'nowplaying' in track['@attr'] and track['@attr']['nowplaying'] == 'true':
                                now_playing = {
                                    'artist': track['artist']['#text'],
                                    'album': track['album']['#text'],
                                    'track': track['name'],
                                    'image': track['image'][-1]['#text'] if track['image'] else None
                                }
                            else:
                                recent_list.append({
                                    'artist': track['artist']['#text'],
                                    'album': track['album']['#text'],
                                    'track': track['name'],
                                    'date': track['date']['#text'] if 'date' in track else 'Unknown',
                                    'image': track['image'][-1]['#text'] if track['image'] else None
                                })
                        
                        # Display now playing if available
                        if now_playing:
                            st.subheader("🎧 Now Playing")
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                if now_playing['image']:
                                    st.image(now_playing['image'], width=150)
                                else:
                                    st.image("https://lastfm.freetls.fastly.net/i/u/300x300/c6f59c1e5e7240a4c0d427abd71f3dbb.png", width=150)
                            
                            with col2:
                                st.write(f"**Track:** {now_playing['track']}")
                                st.write(f"**Artist:** {now_playing['artist']}")
                                st.write(f"**Album:** {now_playing['album']}")
                        
                        # Display recent tracks
                        st.subheader("🕰️ Recently Played")
                        
                        # Create columns for each track
                        cols = st.columns(5)
                        
                        for i, track in enumerate(recent_list[:5]):  # Show only first 5
                            with cols[i]:
                                if track['image']:
                                    st.image(track['image'], width=100)
                                else:
                                    st.image("https://lastfm.freetls.fastly.net/i/u/300x300/c6f59c1e5e7240a4c0d427abd71f3dbb.png", width=100)
                                st.write(f"**{track['track']}**")
                                st.write(f"{track['artist']}")
                                st.write(f"*{track['date']}*")
                    
                    # Show listening milestones
                    if user_info and 'user' in user_info and 'playcount' in user_info['user']:
                        st.subheader("🏆 Listening Milestones")
                        
                        play_count = int(user_info['user']['playcount'])
                        
                        # Determine next milestone
                        milestones = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
                        next_milestone = next((m for m in milestones if m > play_count), play_count * 2)
                        
                        # Calculate progress to next milestone
                        progress = min(play_count / next_milestone, 1.0)
                        
                        # Display milestone progress
                        st.write(f"**Next milestone:** {next_milestone:,} scrobbles")
                        st.progress(progress)
                        st.write(f"You need {next_milestone - play_count:,} more scrobbles to reach your next milestone!")
                
                with tab2:
                    # Period selector for top charts
                    period_options = {
                        'overall': 'All Time',
                        '7day': 'Last 7 Days',
                        '1month': 'Last Month',
                        '3month': 'Last 3 Months',
                        '6month': 'Last 6 Months',
                        '12month': 'Last Year'
                    }
                    
                    period = st.selectbox("Select Time Period:", 
                                          list(period_options.keys()),
                                          format_func=lambda x: period_options[x])
                    
                    # Fetch top artists, tracks, and albums for the selected period
                    top_artists = fetch_top_artists(username, period, 20)
                    top_tracks = fetch_top_tracks(username, period, 20)
                    top_albums = fetch_top_albums(username, period, 20)
                    
                    # Display the top charts
                    create_top_artists_section(top_artists, period_options[period])
                    create_top_tracks_section(top_tracks, period_options[period])
                    create_top_albums_section(top_albums, period_options[period])
                
                with tab3:
                    # This tab shows listening patterns over time
                    st.info("Loading your complete scrobble history for detailed analysis... This might take a while depending on your library size.")
                    
                    if 'scrobble_data' not in st.session_state:
                        with st.spinner("Fetching your complete scrobble history..."):
                            df = fetch_all_scrobbles(username)
                            st.session_state.scrobble_data = df
                    else:
                        df = st.session_state.scrobble_data
                    
                    # Create listening trend chart
                    create_listening_trend_chart(df)
                    
                    # Create listening clock
                    create_listening_clock(df)
                    
                    # Create listening heatmap
                    create_listening_heatmap(df)
                
                with tab4:
                    # This tab shows advanced insights
                    if 'scrobble_data' not in st.session_state:
                        with st.spinner("Fetching your complete scrobble history..."):
                            df = fetch_all_scrobbles(username)
                            st.session_state.scrobble_data = df
                    else:
                        df = st.session_state.scrobble_data
                    
                    # Artist and track diversity
                    create_artist_diversity_chart(df)
                    
                    # Top artists by month/year
                    st.subheader("📅 Top Artists by Month/Year")
                    
                    # Add date columns if not already added
                    if 'datetime' not in df.columns:
                        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                        df['date'] = df['datetime'].dt.date
                        df['month'] = df['datetime'].dt.month
                        df['year'] = df['datetime'].dt.year
                        df['month_year'] = df['datetime'].dt.strftime('%Y-%m')
                    
                    # Get all available years
                    years = sorted(df['year'].unique())
                    
                    if years:
                        selected_year = st.selectbox("Select Year:", years, index=len(years)-1)
                        
                        # Filter data for the selected year
                        year_data = df[df['year'] == selected_year]
                        
                        # Group by month and artist, count plays
                        monthly_artists = year_data.groupby(['month', 'artist']).size().reset_index(name='count')
                        
                        # For each month, get the top artist
                        top_monthly_artists = []
                        for month in range(1, 13):
                            month_data = monthly_artists[monthly_artists['month'] == month]
                            if not month_data.empty:
                                top_artist = month_data.sort_values('count', ascending=False).iloc[0]
                                top_monthly_artists.append({
                                    'month': month,
                                    'month_name': calendar.month_name[month],
                                    'artist': top_artist['artist'],
                                    'count': top_artist['count']
                                })
                        
                        # Create a DataFrame for visualization
                        top_monthly_df = pd.DataFrame(top_monthly_artists)
                        
                        if not top_monthly_df.empty:
                            # Create bar chart
                            fig = px.bar(
                                top_monthly_df,
                                x='month_name',
                                y='count',
                                color='artist',
                                title=f'Top Artist by Month in {selected_year}',
                                labels={'month_name': 'Month', 'count': 'Plays', 'artist': 'Artist'}
                            )
                            
                            # Update layout for better readability
                            fig.update_layout(xaxis_tickangle=-45)
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show as a table as well
                            st.write(top_monthly_df[['month_name', 'artist', 'count']].sort_values('month'))
                    
                    # Listening streak analysis
                    st.subheader("🔥 Listening Streaks")
                    
                    # Convert timestamp to date for streak analysis
                    listening_dates = pd.to_datetime(df['date']).dt.date.unique()
                    listening_dates = sorted(listening_dates)
                    
                    # Calculate streaks
                    streaks = []
                    current_streak = 1
                    max_streak = 1
                    max_streak_end = listening_dates[0] if listening_dates else None
                    
                    for i in range(1, len(listening_dates)):
                        # Check if consecutive days
                        if (listening_dates[i] - listening_dates[i-1]).days == 1:
                            current_streak += 1
                            if current_streak > max_streak:
                                max_streak = current_streak
                                max_streak_end = listening_dates[i]
                        else:
                            # Streak broken
                            streaks.append({
                                'start': listening_dates[i-current_streak],
                                'end': listening_dates[i-1],
                                'length': current_streak
                            })
                            current_streak = 1
                    
                    # Add the last streak
                    if listening_dates:
                        streaks.append({
                            'start': listening_dates[-current_streak],
                            'end': listening_dates[-1],
                            'length': current_streak
                        })
                    
                    # Sort streaks by length (descending)
                    streaks = sorted(streaks, key=lambda x: x['length'], reverse=True)
                    
                    # Display top streaks
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Longest Streak", f"{streaks[0]['length']} days" if streaks else "0 days")
                        if streaks:
                            st.write(f"From {streaks[0]['start']} to {streaks[0]['end']}")
                    
                    with col2:
                        # Calculate current streak (if any)
                        if listening_dates:
                            today = datetime.date.today()
                            yesterday = today - datetime.timedelta(days=1)
                            
                            if listening_dates[-1] == today:
                                # Count backwards from today
                                current = len(listening_dates) - 1
                                current_streak = 1
                                while current > 0 and (listening_dates[current] - listening_dates[current-1]).days == 1:
                                    current_streak += 1
                                    current -= 1
                                st.metric("Current Streak", f"{current_streak} days")
                            elif listening_dates[-1] == yesterday:
                                # Count backwards from yesterday
                                current = len(listening_dates) - 1
                                current_streak = 1
                                while current > 0 and (listening_dates[current] - listening_dates[current-1]).days == 1:
                                    current_streak += 1
                                    current -= 1
                                st.metric("Current Streak", f"{current_streak} days (last: yesterday)")
                            else:
                                st.metric("Current Streak", "0 days")
                                st.write(f"Last scrobble: {listening_dates[-1]}")
                    
                    # Show top 5 streaks
                    if streaks:
                        st.subheader("Top Listening Streaks")
                        
                        streak_data = []
                        for i, streak in enumerate(streaks[:5]):
                            streak_data.append({
                                "Rank": i+1,
                                "Start Date": streak['start'],
                                "End Date": streak['end'],
                                "Length (days)": streak['length']
                            })
                        
                        st.table(pd.DataFrame(streak_data))
                    
                    # Artist evolution over time
                    st.subheader("🔄 Artist Evolution Over Time")
                    
                    # Group by year and get top 5 artists for each year
                    yearly_artists = df.groupby(['year', 'artist']).size().reset_index(name='count')
                    
                    top_yearly_artists = []
                    for year in years:
                        year_data = yearly_artists[yearly_artists['year'] == year]
                        top_5 = year_data.sort_values('count', ascending=False).head(5)
                        
                        for _, row in top_5.iterrows():
                            top_yearly_artists.append({
                                'year': year,
                                'artist': row['artist'],
                                'count': row['count'],
                                'rank': top_5.index.get_loc(_) + 1
                            })
                    
                    # Create a DataFrame for visualization
                    top_yearly_df = pd.DataFrame(top_yearly_artists)
                    
                    if not top_yearly_df.empty:
                        # Create a stacked bar chart
                        fig = px.bar(
                            top_yearly_df,
                            x='year',
                            y='count',
                            color='artist',
                            title='Top 5 Artists by Year',
                            labels={'year': 'Year', 'count': 'Plays', 'artist': 'Artist'}
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab5:
                    # This tab allows users to export their data
                    if 'scrobble_data' not in st.session_state:
                        with st.spinner("Fetching your complete scrobble history..."):
                            df = fetch_all_scrobbles(username)
                            st.session_state.scrobble_data = df
                    else:
                        df = st.session_state.scrobble_data
                    
                    create_export_section(df)
            else:
                st.error("Failed to fetch user data. Please check the username and try again.")
    else:
        st.title("Last.fm Insights Dashboard")
        st.write("Enter your Last.fm username in the sidebar and click 'Load Data' to get started.")
        
        st.image("https://www.last.fm/static/images/lastfm_logo_facebook.15d8133be114.png", width=600)
        
        st.markdown("""
        ## Features
        
        - 📊 **Complete Listening Overview**: View your entire Last.fm history visualized in interactive charts
        - 🎤 **Top Artists, Albums & Tracks**: Discover your most played music across different time periods
        - 📈 **Listening Patterns**: See when you listen to music the most with time-based visualizations
        - 📅 **Artist Evolution**: Track how your music taste has changed over the years
        - 🔍 **Advanced Insights**: Analyze your listening diversity, streaks, and patterns
        - 📤 **Data Export**: Download your complete listening history in various formats
        - 🌓 **Light/Dark Mode**: Choose your preferred visual theme
        
        Enter your Last.fm username to get started!
        """)

if __name__ == "__main__":
    main()