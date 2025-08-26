import streamlit as st
import pandas as pd
import base64
from pathlib import Path

def load_css():
    """Load custom CSS"""
    css_file = Path(__file__).parent / "static/css/style.css"
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
def load_js():
    """Load custom JavaScript for mobile optimizations"""
    # Load mobile helpers
    mobile_helpers_file = Path(__file__).parent / "static/js/mobile_helpers.js"
    with open(mobile_helpers_file) as f:
        st.markdown(f'<script>{f.read()}</script>', unsafe_allow_html=True)
    
    # Load Android heading fix
    android_fix_file = Path(__file__).parent / "static/js/android_heading_fix.js"
    with open(android_fix_file) as f:
        st.markdown(f'<script>{f.read()}</script>', unsafe_allow_html=True)

def local_image(image_path, width=None):
    """Display a local image with optional width"""
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()
    
    width_style = f"width: {width};" if width else ""
    return f'<img src="data:image/png;base64,{img_data}" style="{width_style}">'

def create_nav_link(label, icon, is_active=False):
    """Create a styled navigation link"""
    active_class = "active" if is_active else ""
    return f"""
    <div class="nav-link {active_class}">
        {icon} {label}
    </div>
    """

def display_metric(label, value, delta=None, delta_color="normal"):
    """Display a metric with custom styling"""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)

def format_player_name(first_name, last_name, jersey_number=None):
    """Format player name with optional jersey number"""
    if jersey_number:
        return f"#{jersey_number} {first_name} {last_name}"
    return f"{first_name} {last_name}"

def calculate_team_stats(games_df):
    """Calculate team statistics from games data"""
    if games_df.empty:
        return {
            "wins": 0,
            "losses": 0,
            "ties": 0,
            "points": 0,
            "goals_for": 0,
            "goals_against": 0
        }
    
    # Ensure required columns exist
    required_cols = ['Result', 'GoalsFor', 'GoalsAgainst']
    for col in required_cols:
        if col not in games_df.columns:
            games_df[col] = 0
    
    # Calculate stats
    wins = (games_df['Result'] == 'W').sum()
    losses = (games_df['Result'] == 'L').sum()
    ties = (games_df['Result'] == 'T').sum()
    points = wins * 2 + ties
    goals_for = games_df['GoalsFor'].sum()
    goals_against = games_df['GoalsAgainst'].sum()
    
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "points": points,
        "goals_for": goals_for,
        "goals_against": goals_against
    }

def get_top_players(stats_df, category, position=None, limit=5):
    """Get top players in a specific category with optional position filter"""
    if stats_df.empty:
        return pd.DataFrame()
    
    # Filter by position if specified
    if position:
        filtered_df = stats_df[stats_df['Position'] == position].copy()
    else:
        filtered_df = stats_df.copy()
    
    # Sort by category and return top players
    if category in filtered_df.columns:
        return filtered_df.sort_values(by=category, ascending=False).head(limit)
    
    return pd.DataFrame()

def create_game_card(game):
    """Create HTML for a game card"""
    game_date = game.get('Date', 'Unknown Date')
    opponent = game.get('Opponent', 'Unknown Opponent')
    result = game.get('Result', '')
    score = f"{game.get('GoalsFor', 0)}-{game.get('GoalsAgainst', 0)}"
    
    result_class = ''
    if result == 'W':
        result_class = 'win'
    elif result == 'L':
        result_class = 'loss'
    elif result == 'T':
        result_class = 'tie'
    
    return f"""
    <div class="game-card">
        <div class="game-date">{game_date}</div>
        <div class="game-opponent">vs {opponent}</div>
        <div class="game-result {result_class}">{result} {score}</div>
    </div>
    """
