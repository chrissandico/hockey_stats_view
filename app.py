import streamlit as st
import pandas as pd
import hashlib
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
    initial_sidebar_state="auto"  # Auto will collapse on mobile, expand on desktop
)

# Load custom CSS
load_css()

# Authentication functions
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password():
    """Returns `True` if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        entered_hash = hash_password(st.session_state["password"])
        stored_hash = st.secrets.get("TEAM_PASSWORD_HASH", "")
        
        # Debug logging
        print(f"DEBUG: Entered password hash: {entered_hash}")
        print(f"DEBUG: Stored hash from secrets: {stored_hash}")
        print(f"DEBUG: Hashes match: {entered_hash == stored_hash}")
        
        if entered_hash == stored_hash:
            st.session_state["authenticated"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["authenticated"] = False

    # First run or not authenticated
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        # Show login form
        st.markdown("""
        <div class="login-container">
            <h1 class="login-title">🏒 Hockey Stats Dashboard</h1>
            <p style="text-align: center; color: #666;">Team Members Only</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create centered columns for better mobile appearance
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.text_input(
                "Team Password", 
                type="password", 
                on_change=password_entered, 
                key="password",
                placeholder="Enter team password"
            )
            
            # Add some spacing
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Show error if password was incorrect
            if st.session_state.get("authenticated") == False:
                st.error("❌ Incorrect password. Please try again.")
                
            # Add helpful text
            st.markdown("""
            <div style='text-align: center; color: #888; font-size: 0.9em; margin-top: 2rem;'>
                <p>Contact your coach if you need the password.</p>
            </div>
            """, unsafe_allow_html=True)
        
        return False
    
    return True

# Check authentication
if not check_password():
    st.stop()

# Main application (only runs if authenticated)
st.title("🏒 Hockey Statistics Dashboard")

# Navigation options
nav_options = ["My Player's Stats", "Team Stats & Leaderboards", "Game Stats"]

# Default to Team Stats & Leaderboards
if 'nav_selection' not in st.session_state:
    st.session_state.nav_selection = "Team Stats & Leaderboards"

# Sidebar navigation (for desktop)
st.sidebar.markdown('<h2 style="color: white; font-weight: bold;">Navigation</h2>', unsafe_allow_html=True)

# Create navigation buttons in sidebar (for desktop)
for option in nav_options:
    is_active = st.session_state.nav_selection == option
    button_type = "primary" if is_active else "secondary"
    
    # Use Streamlit's button with custom styling
    if st.sidebar.button(option, key=f"nav_{option}", type=button_type, use_container_width=True):
        st.session_state.nav_selection = option
        st.rerun()

# Add logout option in sidebar
st.sidebar.markdown("---")

# Use Streamlit's button with custom styling
if st.sidebar.button("Logout", key="logout_button", type="primary", use_container_width=True):
    st.session_state["authenticated"] = False
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
