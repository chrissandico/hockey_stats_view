import pandas as pd
from hockey_stats.sheets_service import get_game_roster_data, get_players_data, get_games_data

# Load data
print("Loading GameRoster data...")
game_roster_df = get_game_roster_data()
print(f"GameRoster shape: {game_roster_df.shape}")
print("\nGameRoster columns:", game_roster_df.columns.tolist())
print("\nFirst few rows:")
print(game_roster_df.head())

# Check unique values
if not game_roster_df.empty:
    print("\nUnique GameIDs:", game_roster_df['GameID'].unique())
    print("\nUnique PlayerIDs:", game_roster_df['PlayerID'].unique())
    print("\nUnique Status values:", game_roster_df['Status'].unique())
    
    # Count present vs absent
    if 'Status' in game_roster_df.columns:
        status_counts = game_roster_df['Status'].value_counts()
        print("\nStatus counts:")
        print(status_counts)
    
    # Check for a specific game
    games_df = get_games_data()
    if not games_df.empty:
        first_game_id = games_df.iloc[0]['ID']
        print(f"\nChecking roster for game {first_game_id}:")
        game_roster = game_roster_df[game_roster_df['GameID'] == str(first_game_id)]
        print(f"Players in this game: {len(game_roster)}")
        print(game_roster)
        
        # Check how many are present
        present_players = game_roster[game_roster['Status'] == 'Present']
        print(f"\nPresent players: {len(present_players)}")
        
    # Check player ID format
    players_df = get_players_data()
    if not players_df.empty:
        print("\nPlayer IDs from Players sheet:", players_df['ID'].unique()[:5])
        print("Player IDs from GameRoster sheet:", game_roster_df['PlayerID'].unique()[:5])
