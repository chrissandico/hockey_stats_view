import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import streamlit as st
import pandas as pd
import gspread
from pathlib import Path
from hockey_stats.sheets_service import get_games_data, get_events_data, get_players_data

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Hockey Stats Login")
    if st.button("Login with Google"):
        # This will be handled by Streamlit's Google OAuth in production
        st.session_state.authenticated = True
        st.rerun()
else:
    st.title("Hockey Statistics Dashboard")
    
    # Load data
    games_df = get_games_data()
    events_df = get_events_data()
    players_df = get_players_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    view_option = st.sidebar.radio("Select View", ["Game Logs", "Player Stats", "Season Stats"])
    
    # Common filters
    selected_season = st.sidebar.selectbox("Season", ["2024-2025"])
    
    if view_option == "Game Logs":
        st.subheader("Game Logs")
        selected_opponent = st.sidebar.selectbox("Opponent", ["All"] + list(games_df['Opponent'].unique()))
        filtered_games = games_df if selected_opponent == "All" else games_df[games_df['Opponent'] == selected_opponent]
        st.dataframe(filtered_games)
        
    elif view_option == "Player Stats":
        st.subheader("Player Statistics")
        jersey_number = st.sidebar.selectbox("Jersey Number", ["All"] + sorted(players_df['JerseyNumber'].unique()))
        st.metric("Total Goals", events_df[events_df['EventType'] == 'Goal'].shape[0])
        st.metric("Total Shots", events_df[events_df['EventType'] == 'Shot'].shape[0])
        
    else:
        st.subheader("Season Statistics")
        from hockey_stats.sheets_service import calculate_season_stats
        season_stats = calculate_season_stats(events_df, players_df)
        st.dataframe(season_stats)
