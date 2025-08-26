import streamlit as st
import pandas as pd
from hockey_stats.utils import display_metric, format_player_name

def player_stats_view(players_df, games_df, events_df, game_roster_df):
    """
    Display the player stats view with game selection and statistics
    
    Args:
        players_df: DataFrame containing player information
        games_df: DataFrame containing game information
        events_df: DataFrame containing game events
        game_roster_df: DataFrame containing game roster information
    """
    st.subheader("My Player's Stats")
    
    # Check if data is available
    if players_df.empty:
        st.warning("No player data available. Please check your data source.")
        return
    
    # Player selection - show only jersey numbers
    player_options = []
    for _, player in players_df.iterrows():
        jersey_number = player.get('JerseyNumber', '')
        player_id = player.get('ID', '')
        player_options.append((f"#{jersey_number}", player_id))
    
    if not player_options:
        st.warning("No players found in the database.")
        return
    
    # Sort players by jersey number
    player_options.sort(key=lambda x: x[0])
    
    # Create a list of player names for the selectbox
    player_names = [name for name, _ in player_options]
    player_ids = [id for _, id in player_options]
    
    selected_player_index = st.selectbox(
        "Select Player", 
        range(len(player_names)),
        format_func=lambda i: player_names[i]
    )
    
    selected_player_id = player_ids[selected_player_index]
    selected_player = players_df[players_df['ID'] == selected_player_id].iloc[0]
    
    # Display player info
    col1, col2 = st.columns([1, 3])
    
    with col1:
        jersey = selected_player.get('JerseyNumber', '')
        first_name = selected_player.get('FirstName', f"Player")
        last_name = selected_player.get('LastName', f"#{jersey}")
        st.markdown(f"### #{jersey} {first_name} {last_name}")
        st.markdown(f"**Position:** {selected_player.get('Position', '')}")
    
    # Game selection section
    st.markdown("---")
    st.subheader("Game Statistics")
    
    # Filter games where this player was present using game roster
    if not game_roster_df.empty:
        player_roster_entries = game_roster_df[
            (game_roster_df['PlayerID'] == selected_player_id) & 
            (game_roster_df['Status'] == 'Present')
        ]
        player_game_ids = player_roster_entries['GameID'].unique() if not player_roster_entries.empty else []
    else:
        # Fallback to old method if no roster data
        player_events = events_df[events_df['PrimaryPlayerID'] == selected_player_id]
        assist1_events = events_df[events_df['AssistPlayer1ID'] == selected_player_id]
        assist2_events = events_df[events_df['AssistPlayer2ID'] == selected_player_id]
        all_player_events = pd.concat([player_events, assist1_events, assist2_events]).drop_duplicates()
        player_game_ids = all_player_events['GameID'].unique() if not all_player_events.empty else []
    
    if not len(player_game_ids):
        first_name = selected_player.get('FirstName', 'Player')
        last_name = selected_player.get('LastName', f"#{selected_player.get('JerseyNumber', '')}")
        st.info(f"No game data available for {first_name} {last_name}.")
        return
    
    # Filter games to only those where the player was present
    player_games = games_df[games_df['GameID'].isin(player_game_ids)]
    
    if player_games.empty:
        st.info("No game data available for this player.")
        return
    
    # Create game options for selection
    game_options = []
    for _, game in player_games.iterrows():
        game_date = game.get('Date', 'Unknown Date')
        opponent = game.get('Opponent', 'Unknown')
        game_options.append((f"{game_date} vs {opponent}", game.get('GameID', '')))
    
    # Sort games by date (most recent first)
    game_options.sort(key=lambda x: x[0], reverse=True)
    
    game_labels = [label for label, _ in game_options]
    game_ids = [id for _, id in game_options]
    
    selected_game_index = st.selectbox(
        "Select Game", 
        range(len(game_labels)),
        format_func=lambda i: game_labels[i]
    )
    
    selected_game_id = game_ids[selected_game_index]
    selected_game = games_df[games_df['GameID'] == selected_game_id].iloc[0]
    
    # Get player stats for the selected game
    game_events = events_df[events_df['GameID'] == selected_game_id]
    player_game_events = game_events[game_events['PrimaryPlayerID'] == selected_player_id]
    
    # Calculate player stats for this game
    goals = player_game_events['IsGoal'].sum() if 'IsGoal' in player_game_events.columns else 0
    
    # Calculate assists (player is in assist columns)
    assists = 0
    for _, event in game_events[game_events['IsGoal'] == True].iterrows():
        if event.get('AssistPlayer1ID') == selected_player_id or event.get('AssistPlayer2ID') == selected_player_id:
            assists += 1
    
    # Calculate other stats
    shots = len(player_game_events[player_game_events['EventType'] == 'Shot']) if 'EventType' in player_game_events.columns else 0
    penalty_minutes = player_game_events['PenaltyDuration'].sum() if 'PenaltyDuration' in player_game_events.columns else 0
    
    # Calculate plus/minus
    plus_minus = 0
    if 'YourTeamPlayersOnIce' in game_events.columns:
        for _, event in game_events[game_events['IsGoal'] == True].iterrows():
            if pd.notna(event.get('YourTeamPlayersOnIce')):
                # More robust parsing of YourTeamPlayersOnIce field
                raw_players = str(event.get('YourTeamPlayersOnIce', ''))
                players_on_ice_raw = raw_players.split(',')
                players_on_ice = []
                for p in players_on_ice_raw:
                    p_clean = p.strip().replace('player_', '')
                    players_on_ice.append(p_clean)
                
                if selected_player_id in players_on_ice:
                    if event.get('Team') == 'your_team':  # Adjust based on your team ID
                        plus_minus += 1
                    else:
                        plus_minus -= 1
    
    # Display game stats with direct HTML styling for heading
    st.markdown(f"""
        <h3 style="color: #00205B; background-color: #F0F2F5; padding: 8px; 
        border-bottom: 2px solid #00A0E3; text-shadow: 1px 1px 2px rgba(255,255,255,0.8); 
        font-weight: 700; margin-bottom: 15px;">Game: {selected_game.get('Date', '')} vs {selected_game.get('Opponent', '')}</h3>
    """, unsafe_allow_html=True)
    
    # Create a DataFrame with the game stats
    game_stats_df = pd.DataFrame({
        'Metric': ['Goals', 'Assists', 'Points', 'Plus/Minus', 'Shots', 'PIM'],
        'Value': [
            goals,
            assists,
            goals + assists,
            plus_minus,
            shots,
            penalty_minutes
        ]
    })

    # Display as a styled table
    st.dataframe(
        game_stats_df,
        column_config={
            'Metric': st.column_config.TextColumn("Stat"),
            'Value': st.column_config.TextColumn("Value")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Season stats section
    st.markdown("---")
    st.subheader("Season Statistics")
    
    # Calculate games played
    games_played = len(player_game_ids)
    
    # Calculate season totals (only for games where player was present)
    season_events = events_df[
        (events_df['PrimaryPlayerID'] == selected_player_id) & 
        (events_df['GameID'].isin(player_game_ids))
    ]
    
    # Goals
    season_goals = season_events['IsGoal'].sum() if 'IsGoal' in season_events.columns else 0
    
    # Assists
    season_assists = 0
    for game_id in player_game_ids:
        game_events = events_df[events_df['GameID'] == game_id]
        for _, event in game_events[game_events['IsGoal'] == True].iterrows():
            if event.get('AssistPlayer1ID') == selected_player_id or event.get('AssistPlayer2ID') == selected_player_id:
                season_assists += 1
    
    # Other stats
    season_shots = len(season_events[season_events['EventType'] == 'Shot']) if 'EventType' in season_events.columns else 0
    season_pim = season_events['PenaltyDuration'].sum() if 'PenaltyDuration' in season_events.columns else 0
    
    # Calculate season plus/minus
    season_plus_minus = 0
    if 'YourTeamPlayersOnIce' in events_df.columns:
        for _, event in events_df[events_df['IsGoal'] == True].iterrows():
            if pd.notna(event.get('YourTeamPlayersOnIce')):
                # More robust parsing of YourTeamPlayersOnIce field
                raw_players = str(event.get('YourTeamPlayersOnIce', ''))
                players_on_ice_raw = raw_players.split(',')
                players_on_ice = []
                for p in players_on_ice_raw:
                    p_clean = p.strip().replace('player_', '')
                    players_on_ice.append(p_clean)
                
                if selected_player_id in players_on_ice:
                    if event.get('Team') == 'your_team':  # Adjust based on your team ID
                        season_plus_minus += 1
                    else:
                        season_plus_minus -= 1
    
    # Display season stats with direct HTML styling for heading
    st.markdown("""
        <h3 style="color: #00205B; background-color: #F0F2F5; padding: 8px; 
        border-bottom: 2px solid #00A0E3; text-shadow: 1px 1px 2px rgba(255,255,255,0.8); 
        font-weight: 700; margin-bottom: 15px;">Season Statistics</h3>
    """, unsafe_allow_html=True)
    
    # Calculate goals per game
    gpg = season_goals / games_played if games_played > 0 else 0
    
    # Create a DataFrame with the season stats
    season_stats_df = pd.DataFrame({
        'Metric': ['Games Played', 'Goals', 'Assists', 'Points', 'Shots', '+/-', 'PIM', 'Goals/Game'],
        'Value': [
            games_played,
            season_goals,
            season_assists,
            season_goals + season_assists,
            season_shots,
            season_plus_minus,
            season_pim,
            f"{gpg:.2f}"
        ]
    })

    # Display as a styled table
    st.dataframe(
        season_stats_df,
        column_config={
            'Metric': st.column_config.TextColumn("Stat"),
            'Value': st.column_config.TextColumn("Value")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Game log
    st.markdown("---")
    st.subheader("Game Log")
    
    # Create game log dataframe
    game_log = []
    
    for game_id in player_game_ids:
        game_info = games_df[games_df['GameID'] == game_id]
        if game_info.empty:
            continue
            
        game_date = game_info.iloc[0].get('Date', 'Unknown')
        opponent = game_info.iloc[0].get('Opponent', 'Unknown')
        
        # Get events for this game
        game_events = events_df[events_df['GameID'] == game_id]
        player_game_events = game_events[game_events['PrimaryPlayerID'] == selected_player_id]
        
        # Calculate stats
        goals = player_game_events['IsGoal'].sum() if 'IsGoal' in player_game_events.columns else 0
        
        # Calculate assists
        assists = 0
        for _, event in game_events[game_events['IsGoal'] == True].iterrows():
            if event.get('AssistPlayer1ID') == selected_player_id or event.get('AssistPlayer2ID') == selected_player_id:
                assists += 1
        
        # Calculate plus/minus
        plus_minus = 0
        if 'YourTeamPlayersOnIce' in game_events.columns:
            for _, event in game_events[game_events['IsGoal'] == True].iterrows():
                if pd.notna(event.get('YourTeamPlayersOnIce')):
                    # More robust parsing of YourTeamPlayersOnIce field
                    raw_players = str(event.get('YourTeamPlayersOnIce', ''))
                    players_on_ice_raw = raw_players.split(',')
                    players_on_ice = []
                    for p in players_on_ice_raw:
                        p_clean = p.strip().replace('player_', '')
                        players_on_ice.append(p_clean)
                    
                    if selected_player_id in players_on_ice:
                        if event.get('Team') == 'your_team':  # Adjust based on your team ID
                            plus_minus += 1
                        else:
                            plus_minus -= 1
        
        # Add to game log
        game_log.append({
            'Date': game_date,
            'Opponent': opponent,
            'Goals': goals,
            'Assists': assists,
            'Points': goals + assists,
            '+/-': plus_minus
        })
    
    # Create dataframe and display
    if game_log:
        game_log_df = pd.DataFrame(game_log)
        st.dataframe(
            game_log_df,
            column_config={
                'Date': st.column_config.TextColumn('Date'),
                'Opponent': st.column_config.TextColumn('Opponent'),
                'Goals': st.column_config.NumberColumn('Goals'),
                'Assists': st.column_config.NumberColumn('Assists'),
                'Points': st.column_config.NumberColumn('Points'),
                '+/-': st.column_config.NumberColumn('+/-')
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No game log data available for this player.")
