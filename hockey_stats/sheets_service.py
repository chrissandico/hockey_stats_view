import gspread
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from collections import defaultdict

def connect_to_sheets():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=3600, show_spinner="Loading games data...")
def get_games_data():
    try:
        client = connect_to_sheets()
        sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("Games")
        games_df = pd.DataFrame(sheet.get_all_records())
        
        # Debug: Show what columns we actually have (commented out)
        # st.write(f"DEBUG: Games sheet columns: {games_df.columns.tolist()}")
        # st.write(f"DEBUG: Number of games loaded: {len(games_df)}")
        
        # Use the actual ID column from the Games sheet as GameID
        if 'ID' in games_df.columns:
            games_df['GameID'] = games_df['ID'].astype(str)
        else:
            # Fallback: generate GameID if no ID column exists
            games_df['GameID'] = (
                pd.to_datetime(games_df['Date']).dt.strftime('%Y-%m-%d') + '_' + 
                games_df['Opponent'].str.strip().str.lower().str.replace(' ', '-')
            )
        
        # These will be calculated from Events data later
        games_df['Result'] = 'T'  # Default to tie, will be calculated
        games_df['GoalsFor'] = 0  # Will be calculated from events
        games_df['GoalsAgainst'] = 0  # Will be calculated from events
        
        return games_df
    except Exception as e:
        st.error(f"Failed to load games data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner="Loading game events...")
def get_events_data():
    try:
        client = connect_to_sheets()
        sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("Events")
        df = pd.DataFrame(sheet.get_all_records())
        
        # Debug: Show what columns we actually have (commented out)
        # st.write(f"DEBUG: Events sheet columns: {df.columns.tolist()}")
        # st.write(f"DEBUG: Number of events loaded: {len(df)}")
        # if len(df) > 0:
        #     st.write(f"DEBUG: Sample event data: {df.iloc[0].to_dict()}")
        
        # Clean IDs - handle if columns exist
        id_cols = ['PrimaryPlayerID', 'AssistPlayer1ID', 'AssistPlayer2ID']
        for col in id_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.replace('player_', '')
        
        # Standardize fields if they exist
        if 'EventType' in df.columns:
            df['EventType'] = df['EventType'].astype(str).str.strip().str.title()
        
        if 'Team' in df.columns:
            df['Team'] = df['Team'].astype(str).str.strip().str.lower()
        
        if 'IsGoal' in df.columns:
            # Handle various boolean representations
            df['IsGoal'] = df['IsGoal'].astype(str).str.strip().str.lower().map({
                'yes': True, 'true': True, '1': True, 'y': True,
                'no': False, 'false': False, '0': False, 'n': False,
                '': False
            }).fillna(False)
        
        # GameID should already exist in the Events sheet
        if 'GameID' not in df.columns:
            st.error("GameID column not found in Events sheet!")
            df['GameID'] = 'unknown'
        else:
            df['GameID'] = df['GameID'].astype(str)
        
        # Handle Time column - use Timestamp to extract time if Time doesn't exist
        if 'Time' not in df.columns and 'Timestamp' in df.columns:
            # Extract time from timestamp
            df['Time'] = pd.to_datetime(df['Timestamp']).dt.strftime('%H:%M')
        
        # Special teams fallbacks
        if 'IsPowerPlay' not in df.columns:
            df['IsPowerPlay'] = False
        if 'IsShortHanded' not in df.columns:
            df['IsShortHanded'] = False
        
        return df
    except Exception as e:
        st.error(f"Failed to load events data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner="Loading game roster...")
def get_game_roster_data():
    try:
        client = connect_to_sheets()
        sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("GameRoster")
        df = pd.DataFrame(sheet.get_all_records())
        
        # Clean player IDs - remove 'player_' prefix
        if 'PlayerID' in df.columns:
            df['PlayerID'] = df['PlayerID'].astype(str).str.replace('player_', '').str.strip()
        
        # Ensure GameID is string for consistency
        if 'GameID' in df.columns:
            df['GameID'] = df['GameID'].astype(str)
            
        return df
    except Exception as e:
        st.error(f"Failed to load game roster data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner="Loading players...")
def get_players_data():
    try:
        client = connect_to_sheets()
        sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("Players")
        df = pd.DataFrame(sheet.get_all_records())
        
        # Debug: Show what columns we actually have (commented out)
        # st.write(f"DEBUG: Players sheet columns: {df.columns.tolist()}")
        # st.write(f"DEBUG: Number of players loaded: {len(df)}")
        # if len(df) > 0:
        #     st.write(f"DEBUG: Sample player data: {df.iloc[0].to_dict()}")
        
        # Clean player IDs
        if 'ID' in df.columns:
            df['ID'] = df['ID'].astype(str).str.replace('player_', '').str.strip()
        
        # Add missing FirstName and LastName columns if they don't exist
        if 'FirstName' not in df.columns:
            df['FirstName'] = 'Player'  # Default first name
            
        if 'LastName' not in df.columns:
            # Use jersey number as last name if available
            if 'JerseyNumber' in df.columns:
                df['LastName'] = '#' + df['JerseyNumber'].astype(str)
            else:
                df['LastName'] = 'Unknown'
        
        return df
    except Exception as e:
        st.error(f"Failed to load players data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame()

def calculate_game_results(games_df, events_df, our_team_id="your_team"):
    """Calculate game results (W/L/T) and goals for/against from events data"""
    if games_df.empty or events_df.empty:
        return games_df
    
    # Normalize team ID
    our_team_id = str(our_team_id).strip().lower()
    
    for idx, game in games_df.iterrows():
        game_id = str(game['GameID'])
        
        # Get all goal events for this game
        game_goals = events_df[(events_df['GameID'] == game_id) & (events_df['IsGoal'] == True)]
        
        if len(game_goals) > 0:
            # Count goals for each team
            our_goals = len(game_goals[game_goals['Team'] == our_team_id])
            opponent_goals = len(game_goals[game_goals['Team'] != our_team_id])
            
            # Update the game record
            games_df.at[idx, 'GoalsFor'] = our_goals
            games_df.at[idx, 'GoalsAgainst'] = opponent_goals
            
            # Determine result
            if our_goals > opponent_goals:
                games_df.at[idx, 'Result'] = 'W'
            elif our_goals < opponent_goals:
                games_df.at[idx, 'Result'] = 'L'
            else:
                games_df.at[idx, 'Result'] = 'T'
    
    return games_df

def calculate_season_stats(events_df, players_df, our_team_id="your_team"):
    # Normalize team IDs
    players_df['TeamID'] = players_df['TeamID'].astype(str).str.strip().str.lower()
    events_df['Team'] = events_df['Team'].astype(str).str.strip().str.lower()
    our_team_id = str(our_team_id).strip().lower()
    
    # Filter players
    our_players = players_df[players_df['TeamID'] == our_team_id]
    our_players['ID'] = our_players['ID'].astype(str).str.strip()
    
    stats_df = our_players[['ID', 'JerseyNumber', 'Position']].copy()
    stats_df.columns = ['PlayerID', 'Jersey #', 'Position']
    stats_df['PlayerID'] = stats_df['PlayerID'].astype(str)

    # Calculate goals
    our_goals = events_df[events_df['IsGoal'] & (events_df['Team'] == our_team_id)]
    goals = our_goals.groupby('PrimaryPlayerID').size()
    stats_df['Goals'] = stats_df['PlayerID'].map(goals).fillna(0).astype(int)

    # Calculate assists
    assists = defaultdict(int)
    our_player_ids = set(stats_df['PlayerID'])
    for _, row in our_goals.iterrows():
        for assist_col in ['AssistPlayer1ID', 'AssistPlayer2ID']:
            assist_id = str(row[assist_col]).strip()
            if assist_id in our_player_ids:
                assists[assist_id] += 1
    stats_df['Assists'] = stats_df['PlayerID'].map(assists).fillna(0).astype(int)
    stats_df['Points'] = stats_df['Goals'] + stats_df['Assists']
    
    # Calculate plus/minus
    pm = defaultdict(int)
    our_player_ids = set(our_players['ID'].astype(str))
    for _, event in events_df[events_df['IsGoal']].iterrows():
        # More robust parsing of YourTeamPlayersOnIce field
        if 'YourTeamPlayersOnIce' in event and pd.notna(event['YourTeamPlayersOnIce']):
            # First replace player_ prefix, then split by comma, then strip whitespace
            raw_players = str(event['YourTeamPlayersOnIce'])
            players_on_ice_raw = raw_players.split(',')
            players_on_ice = []
            for p in players_on_ice_raw:
                p_clean = p.strip().replace('player_', '')
                if p_clean in our_player_ids:
                    players_on_ice.append(p_clean)
            
            event_team = str(event['Team']).strip().lower()
            modifier = 1 if event_team == our_team_id else -1
            for player_id in players_on_ice:
                pm[player_id] += modifier
    stats_df['+/-'] = stats_df['PlayerID'].map(pm).fillna(0)
    
    return stats_df[['Jersey #', 'Position', 'Goals', 'Assists', 'Points', '+/-']]
