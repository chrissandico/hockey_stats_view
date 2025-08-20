import pandas as pd
from hockey_stats.sheets_service import get_players_data

# Load players data
print("Loading players data...")
players_df = get_players_data()

print(f"\nPlayers DataFrame shape: {players_df.shape}")
print(f"Columns: {players_df.columns.tolist()}")

print("\nFirst 5 players:")
print(players_df.head())

# Check if FirstName and LastName columns exist
if 'FirstName' in players_df.columns:
    print("\nFirstName column exists")
    print("Sample FirstNames:", players_df['FirstName'].head().tolist())
else:
    print("\nWARNING: FirstName column does not exist!")

if 'LastName' in players_df.columns:
    print("\nLastName column exists")
    print("Sample LastNames:", players_df['LastName'].head().tolist())
else:
    print("\nWARNING: LastName column does not exist!")
