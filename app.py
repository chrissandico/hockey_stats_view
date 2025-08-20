import streamlit as st
import pandas as pd
from pathlib import Path
from hockey_stats.sheets_service import get_games_data, get_events_data, get_players_data, get_game_roster_data, calculate_game_results
from hockey_stats.utils import load_css
from hockey_stats.components.player_stats import player_stats_view
from hockey_stats.components.team_stats import team_stats_view
from hockey_stats.components.game_stats import game_stats_view

# Page configuration
st.set_page_config(
    page_title="Hockey Statistics Dashboard",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-container">
        <h1 class="login-title">Hockey Stats Login</h1>
        <p>Please log in to access the hockey statistics dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Login with Google", key="login_button"):
        # This will be handled by Streamlit's Google OAuth in production
        st.session_state.authenticated = True
        st.rerun()
else:
    # Main application
    st.title("Hockey Statistics Dashboard")
    
    # Navigation
    st.sidebar.markdown('<h2 style="color: white; font-weight: bold;">Navigation</h2>', unsafe_allow_html=True)
    
    # Navigation options
    nav_options = ["My Player's Stats", "Team Stats & Leaderboards", "Game Stats"]
    
    # Default to the first option if not set
    if 'nav_selection' not in st.session_state:
        st.session_state.nav_selection = nav_options[0]
    
    # Create navigation buttons
    for option in nav_options:
        is_active = st.session_state.nav_selection == option
        button_type = "primary" if is_active else "secondary"
        
        # Use Streamlit's button with custom styling
        if st.sidebar.button(option, key=f"nav_{option}", type=button_type, use_container_width=True):
            st.session_state.nav_selection = option
            st.rerun()
    
    # Add logout option
    st.sidebar.markdown("---")
    
    # Use Streamlit's button with custom styling
    if st.sidebar.button("Logout", key="logout_button", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    # Load data
    with st.spinner("Loading data..."):
        games_df = get_games_data()
        events_df = get_events_data()
        players_df = get_players_data()
        game_roster_df = get_game_roster_data()
        
        # Calculate game results from events data
        if not games_df.empty and not events_df.empty:
            games_df = calculate_game_results(games_df, events_df)
    
    # Display selected view
    if st.session_state.nav_selection == "My Player's Stats":
        player_stats_view(players_df, games_df, events_df, game_roster_df)
    
    elif st.session_state.nav_selection == "Team Stats & Leaderboards":
        team_stats_view(players_df, games_df, events_df, game_roster_df)
    
    elif st.session_state.nav_selection == "Game Stats":
        game_stats_view(players_df, games_df, events_df, game_roster_df)
