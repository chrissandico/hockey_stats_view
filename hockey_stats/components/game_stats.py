import streamlit as st
import pandas as pd
from hockey_stats.utils import display_metric, format_player_name

def game_stats_view(players_df, games_df, events_df, game_roster_df):
    """
    Display the game stats view with all players' performance in a specific game
    
    Args:
        players_df: DataFrame containing player information
        games_df: DataFrame containing game information
        events_df: DataFrame containing game events
        game_roster_df: DataFrame containing game roster information
    """
    st.subheader("Game Stats")
    
    # Check if data is available
    if games_df.empty:
        st.warning("No game data available. Please check your data source.")
        return
    
    # Game selection
    game_options = []
    for _, game in games_df.iterrows():
        game_date = game.get('Date', 'Unknown Date')
        opponent = game.get('Opponent', 'Unknown')
        game_options.append((f"{game_date} vs {opponent}", game.get('GameID', '')))
    
    # Sort games by date (most recent first)
    game_options.sort(key=lambda x: x[0], reverse=True)
    
    if not game_options:
        st.warning("No games found in the database.")
        return
    
    game_labels = [label for label, _ in game_options]
    game_ids = [id for _, id in game_options]
    
    selected_game_index = st.selectbox(
        "Select Game", 
        range(len(game_labels)),
        format_func=lambda i: game_labels[i]
    )
    
    selected_game_id = game_ids[selected_game_index]
    selected_game = games_df[games_df['GameID'] == selected_game_id].iloc[0]
    
    # Display game details
    st.markdown(f"### {selected_game.get('Date', '')} vs {selected_game.get('Opponent', '')}")
    
    # Get game result and score
    result = selected_game.get('Result', '')
    goals_for = selected_game.get('GoalsFor', 0)
    goals_against = selected_game.get('GoalsAgainst', 0)
    
    result_color = "normal"
    if result == 'W':
        result_color = "normal"  # Green color for wins
    elif result == 'L':
        result_color = "inverse"  # Red color for losses
    
    # Display game summary with horizontal scrolling on mobile
    st.markdown('<div class="scroll-indicator">Swipe horizontally to see more stats →</div>', unsafe_allow_html=True)
    st.markdown('<div class="stats-scroll-container">', unsafe_allow_html=True)
    
    # Display result with appropriate styling
    if result == 'W':
        display_metric("Result", result, delta="Win", delta_color="normal")
    elif result == 'L':
        display_metric("Result", result, delta="Loss", delta_color="inverse")
    else:
        display_metric("Result", result)
    
    display_metric("Score", f"{goals_for}-{goals_against}")
    
    # Get game events
    game_events = events_df[events_df['GameID'] == selected_game_id]
    
    # Calculate team stats for this game
    shots = len(game_events[game_events['EventType'] == 'Shot']) if 'EventType' in game_events.columns else 0
    penalty_minutes = game_events['PenaltyDuration'].sum() if 'PenaltyDuration' in game_events.columns else 0
    
    # Calculate power play stats
    power_play_goals = game_events['IsPowerPlay'].sum() if 'IsPowerPlay' in game_events.columns else 0
    power_play_opportunities = len(game_events[game_events['EventType'] == 'PowerPlay']) if 'EventType' in game_events.columns else 0
    power_play_pct = (power_play_goals / power_play_opportunities * 100) if power_play_opportunities > 0 else 0
    
    display_metric("Shots", shots)
    display_metric("Penalty Minutes", penalty_minutes)
    display_metric("Power Play", f"{power_play_goals}/{power_play_opportunities}")
    display_metric("Power Play %", f"{power_play_pct:.1f}%")
    
    # Close the container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Player performance table - Wrap in collapsible section for mobile
    st.markdown("---")
    st.markdown('<div class="collapsible-section">', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-header">', unsafe_allow_html=True)
    st.markdown("### Player Performance")
    st.markdown('<span class="collapsible-arrow">▼</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-content">', unsafe_allow_html=True)
    
    # Create filter for position
    position_filter = st.radio(
        "Filter by Position",
        options=["All", "Forward", "Defense", "Goalie"],
        horizontal=True
    )
    
    # Calculate player stats for this game
    player_game_stats = []
    
    # Get roster for this game
    game_roster = game_roster_df[game_roster_df['GameID'] == selected_game_id] if not game_roster_df.empty else pd.DataFrame()
    
    for _, player in players_df.iterrows():
        player_id = str(player.get('ID', ''))
        position = player.get('Position', '')
        
        # Apply position filter
        if position_filter == "Forward" and position != "F":
            continue
        elif position_filter == "Defense" and position != "D":
            continue
        elif position_filter == "Goalie" and position != "G":
            continue
        
        # Check if player was present for this game
        if not game_roster.empty:
            player_roster_entry = game_roster[game_roster['PlayerID'] == player_id]
            if player_roster_entry.empty or player_roster_entry.iloc[0].get('Status', '') != 'Present':
                continue
        
        # Get player events for this game
        player_game_events = game_events[game_events['PrimaryPlayerID'] == player_id]
        
        # Calculate stats
        goals = player_game_events['IsGoal'].sum() if 'IsGoal' in player_game_events.columns else 0
        
        # Calculate assists
        assists = 0
        for _, event in game_events[game_events['IsGoal'] == True].iterrows():
            if event.get('AssistPlayer1ID') == player_id or event.get('AssistPlayer2ID') == player_id:
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
                    
                    if player_id in players_on_ice:
                        if event.get('Team') == 'your_team':  # Adjust based on your team ID
                            plus_minus += 1
                        else:
                            plus_minus -= 1
        
        # Calculate shots
        shots = len(player_game_events[player_game_events['EventType'] == 'Shot']) if 'EventType' in player_game_events.columns else 0
        
        # Calculate penalty minutes
        penalty_minutes = player_game_events['PenaltyDuration'].sum() if 'PenaltyDuration' in player_game_events.columns else 0
        
        # For goalies, calculate additional stats
        if position == "G":
            # Check if goalie played in this game
            if player_id in game_events['PrimaryPlayerID'].values:
                # Calculate goals against
                goals_against = len(game_events[(game_events['IsGoal'] == True) & 
                                             (game_events['Team'] != 'your_team')])
                
                # Calculate shots faced
                shots_faced = len(game_events[(game_events['EventType'].isin(['Shot', 'Goal'])) & 
                                           (game_events['Team'] != 'your_team')])
                
                # Calculate save percentage
                saves = shots_faced - goals_against
                save_pct = saves / shots_faced if shots_faced > 0 else 0
                
                jersey = player.get('JerseyNumber', '')
                player_game_stats.append({
                    'JerseyNumber': jersey,
                    'FirstName': player.get('FirstName', 'Player'),
                    'LastName': player.get('LastName', f"#{jersey}"),
                    'Position': position,
                    'GA': goals_against,
                    'Saves': saves,
                    'SV%': save_pct
                })
        else:
            # Add to player stats
            jersey = player.get('JerseyNumber', '')
            player_game_stats.append({
                'JerseyNumber': jersey,
                'FirstName': player.get('FirstName', 'Player'),
                'LastName': player.get('LastName', f"#{jersey}"),
                'Position': position,
                'Goals': goals,
                'Assists': assists,
                'Points': goals + assists,
                '+/-': plus_minus,
                'Shots': shots,
                'PIM': penalty_minutes
            })
    
    # Create dataframe and display
    if player_game_stats:
        player_game_stats_df = pd.DataFrame(player_game_stats)
        
        # Sort by jersey number
        player_game_stats_df = player_game_stats_df.sort_values(by=['Position', 'JerseyNumber'])
        
        # Display different tables based on position filter
        if position_filter == "Goalie":
            if 'GA' in player_game_stats_df.columns:
                st.dataframe(
                    player_game_stats_df,
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'Position': st.column_config.TextColumn('Pos'),
                        'GA': st.column_config.NumberColumn('GA'),
                        'Saves': st.column_config.NumberColumn('Saves'),
                        'SV%': st.column_config.NumberColumn('SV%', format="%.3f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No goalie statistics available for this game.")
        else:
            if 'Goals' in player_game_stats_df.columns:
                st.dataframe(
                    player_game_stats_df,
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'Position': st.column_config.TextColumn('Pos'),
                        'Goals': st.column_config.NumberColumn('G'),
                        'Assists': st.column_config.NumberColumn('A'),
                        'Points': st.column_config.NumberColumn('P'),
                        '+/-': st.column_config.NumberColumn('+/-'),
                        'Shots': st.column_config.NumberColumn('SOG'),
                        'PIM': st.column_config.NumberColumn('PIM')
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No player statistics available for this game.")
    else:
        st.info("No player statistics available for this game.")
    
    # Close the player performance collapsible section
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Game Timeline - Wrap in collapsible section for mobile
    st.markdown("---")
    st.markdown('<div class="collapsible-section">', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-header">', unsafe_allow_html=True)
    st.markdown("### Game Timeline")
    st.markdown('<span class="collapsible-arrow">▼</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-content">', unsafe_allow_html=True)
    
    if not game_events.empty:
        # Create timeline events
        timeline_events = []
        
        for _, event in game_events.iterrows():
            event_type = event.get('EventType', '')
            period = event.get('Period', '')
            time = event.get('Time', '')
            
            # Skip events without period or time
            if not period or not time:
                continue
            
            # Get player name
            player_id = event.get('PrimaryPlayerID', '')
            player_info = players_df[players_df['ID'] == player_id]
            player_name = ""
            
            if not player_info.empty:
                jersey = player_info.iloc[0].get('JerseyNumber', '')
                first_name = player_info.iloc[0].get('FirstName', 'Player')
                last_name = player_info.iloc[0].get('LastName', f"#{jersey}")
                player_name = f"{first_name} {last_name}"
            
            # Create description based on event type
            description = ""
            
            if event_type == "Goal":
                # Get assist players
                assist1_id = event.get('AssistPlayer1ID', '')
                assist2_id = event.get('AssistPlayer2ID', '')
                
                assist1_name = ""
                assist2_name = ""
                
                if assist1_id:
                    assist1_info = players_df[players_df['ID'] == assist1_id]
                    if not assist1_info.empty:
                        jersey = assist1_info.iloc[0].get('JerseyNumber', '')
                        first_name = assist1_info.iloc[0].get('FirstName', 'Player')
                        last_name = assist1_info.iloc[0].get('LastName', f"#{jersey}")
                        assist1_name = f"{first_name} {last_name}"
                
                if assist2_id:
                    assist2_info = players_df[players_df['ID'] == assist2_id]
                    if not assist2_info.empty:
                        jersey = assist2_info.iloc[0].get('JerseyNumber', '')
                        first_name = assist2_info.iloc[0].get('FirstName', 'Player')
                        last_name = assist2_info.iloc[0].get('LastName', f"#{jersey}")
                        assist2_name = f"{first_name} {last_name}"
                
                # Create goal description
                description = f"Goal: {player_name}"
                
                if assist1_name and assist2_name:
                    description += f" (Assists: {assist1_name}, {assist2_name})"
                elif assist1_name:
                    description += f" (Assist: {assist1_name})"
                
                # Add power play or shorthanded indicator
                if event.get('IsPowerPlay'):
                    description += " (PP)"
                elif event.get('IsShortHanded'):
                    description += " (SH)"
            
            elif event_type == "Penalty":
                penalty_type = event.get('PenaltyType', '')
                duration = event.get('PenaltyDuration', '')
                
                description = f"Penalty: {player_name}, {penalty_type} ({duration} min)"
            
            elif event_type == "Shot":
                description = f"Shot: {player_name}"
            
            elif event_type == "Hit":
                description = f"Hit: {player_name}"
            
            elif event_type == "Faceoff":
                description = f"Faceoff won by: {player_name}"
            
            # Add to timeline
            timeline_events.append({
                'Period': period,
                'Time': time,
                'Event': event_type,
                'Description': description,
                'Team': event.get('Team', '')
            })
        
        # Create dataframe and display
        if timeline_events:
            timeline_df = pd.DataFrame(timeline_events)
            
            # Sort by period and time
            timeline_df['SortTime'] = timeline_df['Time'].apply(lambda x: x.replace(':', '.'))
            timeline_df['SortTime'] = pd.to_numeric(timeline_df['SortTime'], errors='coerce')
            timeline_df = timeline_df.sort_values(by=['Period', 'SortTime'])
            
            # Display timeline
            st.dataframe(
                timeline_df[['Period', 'Time', 'Event', 'Description', 'Team']],
                column_config={
                    'Period': st.column_config.TextColumn('Period'),
                    'Time': st.column_config.TextColumn('Time'),
                    'Event': st.column_config.TextColumn('Event'),
                    'Description': st.column_config.TextColumn('Description'),
                    'Team': st.column_config.TextColumn('Team')
                },
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("No timeline events available for this game.")
    
    # Close the game timeline collapsible section
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
