import pandas as pd
from hockey_stats.sheets_service import get_game_roster_data, get_players_data, get_games_data, get_events_data

# Load all data
print("Loading all data...")
games_df = get_games_data()
players_df = get_players_data()
events_df = get_events_data()
game_roster_df = get_game_roster_data()

print(f"\nTotal games: {len(games_df)}")
print(f"Total players: {len(players_df)}")
print(f"Total events: {len(events_df)}")
print(f"Total roster entries: {len(game_roster_df)}")

# Test for a specific game
if not games_df.empty:
    # Get the first game
    test_game = games_df.iloc[0]
    test_game_id = str(test_game['ID'])
    print(f"\n\nTesting Game ID: {test_game_id}")
    print(f"Date: {test_game.get('Date', 'N/A')}")
    print(f"Opponent: {test_game.get('Opponent', 'N/A')}")
    
    # Get roster for this game
    game_roster = game_roster_df[game_roster_df['GameID'] == test_game_id]
    print(f"\nRoster entries for this game: {len(game_roster)}")
    
    # Get present players
    present_players = game_roster[game_roster['Status'] == 'Present']
    print(f"Present players: {len(present_players)}")
    
    # Get events for this game
    game_events = events_df[events_df['GameID'] == test_game_id]
    print(f"\nEvents in this game: {len(game_events)}")
    
    # Show which players were present
    print("\nPlayers present in this game:")
    for _, roster_entry in present_players.iterrows():
        player_id = roster_entry['PlayerID']
        player_info = players_df[players_df['ID'] == player_id]
        if not player_info.empty:
            player = player_info.iloc[0]
            jersey = player.get('JerseyNumber', 'N/A')
            first_name = player.get('FirstName', 'Unknown')
            last_name = player.get('LastName', 'Player')
            position = player.get('Position', 'N/A')
            
            # Check if player had any events
            player_events = game_events[game_events['PrimaryPlayerID'] == player_id]
            event_count = len(player_events)
            
            print(f"  #{jersey} - {first_name} {last_name} ({position}) - {event_count} events")
    
    # Check for absent players
    absent_players = game_roster[game_roster['Status'] == 'Absent']
    if len(absent_players) > 0:
        print(f"\nPlayers absent from this game: {len(absent_players)}")
        for _, roster_entry in absent_players.iterrows():
            player_id = roster_entry['PlayerID']
            player_info = players_df[players_df['ID'] == player_id]
            if not player_info.empty:
                player = player_info.iloc[0]
                jersey = player.get('JerseyNumber', 'N/A')
                first_name = player.get('FirstName', 'Unknown')
                last_name = player.get('LastName', 'Player')
                print(f"  #{jersey} - {first_name} {last_name}")
