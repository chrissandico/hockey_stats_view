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

def get_games_data():
    client = connect_to_sheets()
    sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("Games")
    return pd.DataFrame(sheet.get_all_records())

def get_events_data():
    client = connect_to_sheets()
    sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("Events")
    df = pd.DataFrame(sheet.get_all_records())
    
    # Clean and convert all ID fields to match player format
    id_cols = ['PrimaryPlayerID', 'AssistPlayer1ID', 'AssistPlayer2ID']
    for col in id_cols:
        df[col] = df[col].astype(str).str.strip().str.replace('player_', '')
    
    # Clean and standardize other fields
    df['EventType'] = df['EventType'].astype(str).str.strip().str.title()
    df['Team'] = df['Team'].astype(str).str.strip().str.lower()
    df['IsGoal'] = df['IsGoal'].astype(str).str.strip().str.lower().map(
        {'yes': True, 'true': True, '1': True}).fillna(False)
    
    print("Loaded events sample:\n", df[['EventType', 'Team', 'PrimaryPlayerID', 'IsGoal']].head())
    return df

def get_players_data():
    client = connect_to_sheets()
    sheet = client.open_by_key("1u4olfiYFjXW0Z88U3Q1wOxI7gz04KYbg6LNn8h-rfno").worksheet("Players")
    df = pd.DataFrame(sheet.get_all_records())
    df['ID'] = df['ID'].str.replace('player_', '').astype(str).str.strip()
    return df

def calculate_season_stats(events_df, players_df, our_team_id="your_team"):
    # Normalize team IDs
    players_df['TeamID'] = players_df['TeamID'].astype(str).str.strip().str.lower()
    events_df['Team'] = events_df['Team'].astype(str).str.strip().str.lower()
    our_team_id = str(our_team_id).strip().lower()
    
    # Filter players and clean IDs
    our_players = players_df[players_df['TeamID'] == our_team_id]
    our_players['ID'] = our_players['ID'].astype(str).str.strip()
    
    stats_df = our_players[['ID', 'JerseyNumber', 'Position']].copy()
    stats_df.columns = ['PlayerID', 'Jersey #', 'Position']
    stats_df['PlayerID'] = stats_df['PlayerID'].astype(str)

    # Debug player IDs
    print(f"Player IDs in Roster: {stats_df['PlayerID'].tolist()}")
    
    # Calculate goals using IsGoal boolean
    our_goals = events_df[events_df['IsGoal'] & (events_df['Team'] == our_team_id)]
    print(f"Goal Events:\n{our_goals[['PrimaryPlayerID', 'Team', 'IsGoal']]}")
    
    goals = our_goals.groupby('PrimaryPlayerID').size()
    stats_df['Goals'] = stats_df['PlayerID'].map(goals).fillna(0).astype(int)
    print(f"Goals Mapping: {stats_df[['PlayerID', 'Goals']].to_dict()}")

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
    pm_df = calculate_plus_minus(events_df, our_players, our_team_id).reset_index()
    pm_df.columns = ['PlayerID', '+/-']
    stats_df = stats_df.merge(pm_df, on='PlayerID', how='left').fillna(0)
    
    # Penalty minutes
    our_penalties = events_df[(events_df['EventType'] == 'Penalty') & (events_df['Team'] == our_team_id)]
    pim = our_penalties.groupby('PrimaryPlayerID')['PenaltyDuration'].sum()
    stats_df['Penalty Minutes'] = stats_df['PlayerID'].map(pim).fillna(0).astype(int)
    
    # Shots on goal
    our_shots = events_df[(events_df['EventType'] == 'Shot') & (events_df['Team'] == our_team_id)]
    shots = our_shots.groupby('PrimaryPlayerID').size()
    stats_df['Shots on Goal'] = stats_df['PlayerID'].map(shots).fillna(0).astype(int)
    
    return stats_df[['Jersey #', 'Position', 'Goals', 'Assists', 
                   'Points', '+/-', 'Penalty Minutes', 'Shots on Goal']]

def calculate_plus_minus(events_df, our_players_df, our_team_id="your_team"):
    pm = defaultdict(int)
    our_team_id = str(our_team_id).strip().lower()
    our_player_ids = set(our_players_df['ID'].astype(str))
    
    for _, event in events_df[events_df['IsGoal']].iterrows():
        # Clean and parse players on ice
        players_on_ice = str(event['YourTeamPlayersOnIce']).replace('player_', '').split(',')
        players_on_ice = [pid.strip() for pid in players_on_ice if pid.strip() in our_player_ids]
        event_team = str(event['Team']).strip().lower()
        
        if event_team == our_team_id:
            for player_id in players_on_ice:
                pm[player_id] += 1
        else:
            for player_id in players_on_ice:
                pm[player_id] -= 1
    return pd.DataFrame.from_dict(pm, orient='index', columns=['+/-'])
