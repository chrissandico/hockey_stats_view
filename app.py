import streamlit as st
import pandas as pd
import hashlib
from pathlib import Path
from hockey_stats.sheets_service import get_games_data, get_events_data, get_players_data, get_game_roster_data, calculate_game_results
from hockey_stats.utils import load_css, load_js, local_image
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

# Load custom CSS and JavaScript
load_css()
load_js()

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
            # Track that a login attempt was made
            st.session_state["password_attempt"] = True

    # First run or not authenticated
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        # Initialize password_attempt to track if a login attempt was made
        st.session_state["password_attempt"] = False

    if not st.session_state["authenticated"]:
        # Show login form with enhanced styling and direct HTML styling for Android compatibility
        logo_html = local_image("hockey_stats/static/images/markham_waxers_logo.png", width="100px")
        st.markdown(f"""
        <div class="login-container" style="background-color: #FFFFFF; border-radius: 15px; box-shadow: 0 8px 25px rgba(0, 32, 91, 0.15); padding: 2rem; text-align: center; margin: 0 auto; max-width: 450px; border-top: 5px solid #00205B;">
            <div class="login-header" style="margin-bottom: 1.5rem;">
                <div class="login-logo" style="width: 100px; margin: 0 auto 1.5rem auto;">{logo_html}</div>
                <h1 style="color: #00205B !important; background-color: #F0F2F5 !important; padding: 8px !important; 
                margin-bottom: 15px !important; border: 1px solid #00A0E3 !important; border-radius: 4px !important;
                font-weight: 700 !important; display: block !important; visibility: visible !important; opacity: 1 !important; font-size: 1.8rem !important;">Hockey Stats Dashboard</h1>
                <div class="android-heading-fallback">Hockey Stats Dashboard</div>
                <p style="color: #00A0E3 !important; font-size: 1.1rem !important; margin-bottom: 1rem !important; font-weight: bold !important;">Team Members Access Portal</p>
            </div>
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
            
            # Show error only if a password attempt was made and failed
            if st.session_state.get("password_attempt") == True and st.session_state.get("authenticated") == False:
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
# Use both native Streamlit heading and a custom div for Android compatibility
st.markdown("""
    <h1 style="color: #00205B !important; background-color: #F0F2F5 !important; padding: 8px !important; 
    margin-bottom: 15px !important; border: 1px solid #00A0E3 !important; border-radius: 4px !important;
    font-weight: 700 !important; display: block !important; visibility: visible !important; opacity: 1 !important;">🏒 Hockey Statistics Dashboard</h1>
""", unsafe_allow_html=True)
st.markdown('<div class="android-heading-fallback">🏒 Hockey Statistics Dashboard</div>', unsafe_allow_html=True)

# Navigation options
nav_options = ["My Player's Stats", "Team Stats & Leaderboards", "Game Stats"]

# Default to Team Stats & Leaderboards
if 'nav_selection' not in st.session_state:
    st.session_state.nav_selection = "Team Stats & Leaderboards"

# Create a container for top navigation
nav_container = st.container()

# Create a row of buttons for navigation
with nav_container:
    cols = st.columns(3)
    
    # Style each button as a box
    for i, option in enumerate(nav_options):
        is_active = st.session_state.nav_selection == option
        button_style = "primary" if is_active else "secondary"
        
        # Each button in its own column
        if cols[i].button(option, key=f"nav_{option}", type=button_style, use_container_width=True):
            st.session_state.nav_selection = option
            st.rerun()

# Add logout button at the top right
logout_col1, logout_col2 = st.columns([4, 1])
with logout_col2:
    if st.button("Logout", key="logout_button", type="primary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# Add a separator
st.markdown("<hr>", unsafe_allow_html=True)

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
