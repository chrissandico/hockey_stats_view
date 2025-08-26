import streamlit as st
import pandas as pd
from hockey_stats.utils import display_metric, calculate_team_stats, get_top_players

def team_stats_view(players_df, games_df, events_df, game_roster_df):
    """
    Display the team stats view with season summary and leaderboards
    
    Args:
        players_df: DataFrame containing player information
        games_df: DataFrame containing game information
        events_df: DataFrame containing game events
        game_roster_df: DataFrame containing game roster information
    """
    # Use both native Streamlit heading and a custom div for Android compatibility
    st.subheader("Team Stats & Leaderboards")
    st.markdown('<div class="android-heading-fallback">Team Stats & Leaderboards</div>', unsafe_allow_html=True)
    
    # Check if data is available
    if games_df.empty or players_df.empty:
        st.warning("No team data available. Please check your data source.")
        return
    
    # Calculate team stats
    team_stats = calculate_team_stats(games_df)
    
    # Display team season summary using both native Streamlit heading and a custom div for Android compatibility
    st.markdown("### Season Summary")
    st.markdown('<div class="android-heading-fallback">Season Summary</div>', unsafe_allow_html=True)
    
    # Calculate win percentage
    win_pct = team_stats['wins'] / (team_stats['wins'] + team_stats['losses'] + team_stats['ties']) * 100 if (team_stats['wins'] + team_stats['losses'] + team_stats['ties']) > 0 else 0
    goal_diff = team_stats['goals_for'] - team_stats['goals_against']
    
    # Create a DataFrame with the stats
    stats_df = pd.DataFrame({
        'Metric': ['Record', 'Points', 'Goals For', 'Goals Against', 'Goal Differential', 'Win %'],
        'Value': [
            f"{team_stats['wins']}-{team_stats['losses']}-{team_stats['ties']}",
            team_stats['points'],
            team_stats['goals_for'],
            team_stats['goals_against'],
            goal_diff,
            f"{win_pct:.1f}%"
        ]
    })

    # Display as a styled table
    st.dataframe(
        stats_df,
        column_config={
            'Metric': st.column_config.TextColumn("Stat"),
            'Value': st.column_config.TextColumn("Value")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Calculate player season stats
    player_stats = []
    
    for _, player in players_df.iterrows():
        player_id = str(player.get('ID', ''))
        player_events = events_df[events_df['PrimaryPlayerID'] == player_id]
        
        # Calculate games played from GameRoster
        games_played = 0
        if not game_roster_df.empty:
            player_games = game_roster_df[(game_roster_df['PlayerID'] == player_id) & 
                                          (game_roster_df['Status'] == 'Present')]
            games_played = len(player_games)
        
        # Goals
        goals = player_events['IsGoal'].sum() if 'IsGoal' in player_events.columns else 0
        
        # Assists
        assists = 0
        for _, event in events_df[events_df['IsGoal'] == True].iterrows():
            if event.get('AssistPlayer1ID') == player_id or event.get('AssistPlayer2ID') == player_id:
                assists += 1
        
        # Plus/minus
        plus_minus = 0
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
                    
                    if player_id in players_on_ice:
                        if event.get('Team') == 'your_team':  # Adjust based on your team ID
                            plus_minus += 1
                        else:
                            plus_minus -= 1
        
        # Shots
        shots = len(player_events[player_events['EventType'] == 'Shot']) if 'EventType' in player_events.columns else 0
        
        # Add to player stats
        jersey = player.get('JerseyNumber', '')
        player_stats.append({
            'PlayerID': player_id,
            'FirstName': player.get('FirstName', 'Player'),
            'LastName': player.get('LastName', f"#{jersey}"),
            'JerseyNumber': jersey,
            'Position': player.get('Position', ''),
            'GP': games_played,
            'Goals': goals,
            'Assists': assists,
            'Points': goals + assists,
            '+/-': plus_minus,
            'Shots': shots
        })
    
    # Create dataframe
    player_stats_df = pd.DataFrame(player_stats)
    
    # Display leaderboards
    st.markdown("---")
    # Use both native Streamlit heading and a custom div for Android compatibility
    st.markdown("## Leaderboards")
    st.markdown('<div class="android-heading-fallback">Leaderboards</div>', unsafe_allow_html=True)
    
    # Forward Leaderboards - Wrap in collapsible section for mobile
    st.markdown('<div class="collapsible-section">', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-header">', unsafe_allow_html=True)
    st.markdown("### Forward Leaderboards")
    st.markdown('<div class="android-heading-fallback">Forward Leaderboards</div>', unsafe_allow_html=True)
    st.markdown('<span class="collapsible-arrow">▼</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-content">', unsafe_allow_html=True)
    
    # Check if we have forwards
    forwards_df = player_stats_df[player_stats_df['Position'] == 'F'].copy() if not player_stats_df.empty else pd.DataFrame()
    
    if not forwards_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 5 Forward Goal Scorers")
            top_goals = get_top_players(forwards_df, 'Goals', position='F', limit=5)
            if not top_goals.empty:
                st.dataframe(
                    top_goals[['JerseyNumber', 'FirstName', 'LastName', 'GP', 'Goals', 'Points']],
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'GP': st.column_config.NumberColumn('GP'),
                        'Goals': st.column_config.NumberColumn('Goals'),
                        'Points': st.column_config.NumberColumn('Points')
                    },
                    hide_index=True
                )
            else:
                st.info("No data available for forward goal scorers.")
        
        with col2:
            st.markdown("#### Top 5 Forward Assists")
            top_assists = get_top_players(forwards_df, 'Assists', position='F', limit=5)
            if not top_assists.empty:
                st.dataframe(
                    top_assists[['JerseyNumber', 'FirstName', 'LastName', 'GP', 'Assists', 'Points']],
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'GP': st.column_config.NumberColumn('GP'),
                        'Assists': st.column_config.NumberColumn('Assists'),
                        'Points': st.column_config.NumberColumn('Points')
                    },
                    hide_index=True
                )
            else:
                st.info("No data available for forward assists.")
        
        st.markdown("#### Top 5 Forward Points")
        top_points = get_top_players(forwards_df, 'Points', position='F', limit=5)
        if not top_points.empty:
            st.dataframe(
                top_points[['JerseyNumber', 'FirstName', 'LastName', 'GP', 'Goals', 'Assists', 'Points']],
                column_config={
                    'JerseyNumber': st.column_config.TextColumn('#'),
                    'FirstName': st.column_config.TextColumn('First'),
                    'LastName': st.column_config.TextColumn('Last'),
                    'GP': st.column_config.NumberColumn('GP'),
                    'Goals': st.column_config.NumberColumn('Goals'),
                    'Assists': st.column_config.NumberColumn('Assists'),
                    'Points': st.column_config.NumberColumn('Points')
                },
                hide_index=True
            )
        else:
            st.info("No data available for forward points.")
    else:
        st.info("No forward data available.")
    
    # Close the forward leaderboards collapsible section
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Defensemen Leaderboards - Wrap in collapsible section for mobile
    st.markdown('<div class="collapsible-section">', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-header">', unsafe_allow_html=True)
    st.markdown("### Defensemen Leaderboards")
    st.markdown('<div class="android-heading-fallback">Defensemen Leaderboards</div>', unsafe_allow_html=True)
    st.markdown('<span class="collapsible-arrow">▼</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-content">', unsafe_allow_html=True)
    
    # Check if we have defensemen
    defensemen_df = player_stats_df[player_stats_df['Position'] == 'D'].copy() if not player_stats_df.empty else pd.DataFrame()
    
    if not defensemen_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 5 Defensemen Goal Scorers")
            top_goals = get_top_players(defensemen_df, 'Goals', position='D', limit=5)
            if not top_goals.empty:
                st.dataframe(
                    top_goals[['JerseyNumber', 'FirstName', 'LastName', 'GP', 'Goals', 'Points']],
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'GP': st.column_config.NumberColumn('GP'),
                        'Goals': st.column_config.NumberColumn('Goals'),
                        'Points': st.column_config.NumberColumn('Points')
                    },
                    hide_index=True
                )
            else:
                st.info("No data available for defensemen goal scorers.")
        
        with col2:
            st.markdown("#### Top 5 Defensemen Assists")
            top_assists = get_top_players(defensemen_df, 'Assists', position='D', limit=5)
            if not top_assists.empty:
                st.dataframe(
                    top_assists[['JerseyNumber', 'FirstName', 'LastName', 'GP', 'Assists', 'Points']],
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'GP': st.column_config.NumberColumn('GP'),
                        'Assists': st.column_config.NumberColumn('Assists'),
                        'Points': st.column_config.NumberColumn('Points')
                    },
                    hide_index=True
                )
            else:
                st.info("No data available for defensemen assists.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 5 Defensemen Points")
            top_points = get_top_players(defensemen_df, 'Points', position='D', limit=5)
            if not top_points.empty:
                st.dataframe(
                    top_points[['JerseyNumber', 'FirstName', 'LastName', 'GP', 'Goals', 'Assists', 'Points']],
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'GP': st.column_config.NumberColumn('GP'),
                        'Goals': st.column_config.NumberColumn('Goals'),
                        'Assists': st.column_config.NumberColumn('Assists'),
                        'Points': st.column_config.NumberColumn('Points')
                    },
                    hide_index=True
                )
            else:
                st.info("No data available for defensemen points.")
        
        with col2:
            st.markdown("#### Top 5 Defensemen Plus/Minus")
            top_plus_minus = get_top_players(defensemen_df, '+/-', position='D', limit=5)
            if not top_plus_minus.empty:
                st.dataframe(
                    top_plus_minus[['JerseyNumber', 'FirstName', 'LastName', 'GP', '+/-']],
                    column_config={
                        'JerseyNumber': st.column_config.TextColumn('#'),
                        'FirstName': st.column_config.TextColumn('First'),
                        'LastName': st.column_config.TextColumn('Last'),
                        'GP': st.column_config.NumberColumn('GP'),
                        '+/-': st.column_config.NumberColumn('+/-')
                    },
                    hide_index=True
                )
            else:
                st.info("No data available for defensemen plus/minus.")
    else:
        st.info("No defensemen data available.")
    
    # Close the defensemen leaderboards collapsible section
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Goalie Leaderboards - Wrap in collapsible section for mobile
    st.markdown('<div class="collapsible-section">', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-header">', unsafe_allow_html=True)
    st.markdown("### Goalie Statistics")
    st.markdown('<div class="android-heading-fallback">Goalie Statistics</div>', unsafe_allow_html=True)
    st.markdown('<span class="collapsible-arrow">▼</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-content">', unsafe_allow_html=True)
    
    # Check if we have goalies
    goalies_df = player_stats_df[player_stats_df['Position'] == 'G'].copy() if not player_stats_df.empty else pd.DataFrame()
    
    if not goalies_df.empty:
        # For goalies, we need to calculate additional stats
        goalie_stats = []
        
        for _, goalie in goalies_df.iterrows():
            goalie_id = goalie['PlayerID']
            
            # Calculate games played
            games_played = 0
            goals_against = 0
            shots_faced = 0
            wins = 0
            shutouts = 0
            
            # Process each game
            for game_id in games_df['GameID'].unique():
                game_events = events_df[events_df['GameID'] == game_id]
                
                # Check if goalie played in this game
                if goalie_id in game_events['PrimaryPlayerID'].values:
                    games_played += 1
                    
                    # Calculate goals against
                    goals_against_game = len(game_events[(game_events['IsGoal'] == True) & 
                                                       (game_events['Team'] != 'your_team')])
                    goals_against += goals_against_game
                    
                    # Calculate shots faced
                    shots_faced_game = len(game_events[(game_events['EventType'].isin(['Shot', 'Goal'])) & 
                                                     (game_events['Team'] != 'your_team')])
                    shots_faced += shots_faced_game
                    
                    # Check if win
                    game_info = games_df[games_df['GameID'] == game_id]
                    if not game_info.empty and game_info.iloc[0].get('Result') == 'W':
                        wins += 1
                    
                    # Check if shutout
                    if goals_against_game == 0:
                        shutouts += 1
            
            # Calculate GAA and save percentage
            gaa = goals_against / games_played if games_played > 0 else 0
            save_pct = (shots_faced - goals_against) / shots_faced if shots_faced > 0 else 0
            
            goalie_stats.append({
                'JerseyNumber': goalie['JerseyNumber'],
                'FirstName': goalie['FirstName'],
                'LastName': goalie['LastName'],
                'GP': games_played,
                'GAA': gaa,
                'SV%': save_pct,
                'W': wins,
                'SO': shutouts
            })
        
        # Create dataframe and display
        if goalie_stats:
            goalie_stats_df = pd.DataFrame(goalie_stats)
            st.dataframe(
                goalie_stats_df,
                column_config={
                    'JerseyNumber': st.column_config.TextColumn('#'),
                    'FirstName': st.column_config.TextColumn('First'),
                    'LastName': st.column_config.TextColumn('Last'),
                    'GP': st.column_config.NumberColumn('Games'),
                    'GAA': st.column_config.NumberColumn('GAA', format="%.2f"),
                    'SV%': st.column_config.NumberColumn('Save %', format="%.3f"),
                    'W': st.column_config.NumberColumn('Wins'),
                    'SO': st.column_config.NumberColumn('Shutouts')
                },
                hide_index=True
            )
        else:
            st.info("No goalie statistics available.")
    else:
        st.info("No goalie data available.")
    
    # Close the goalie statistics collapsible section
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Game Log - Wrap in collapsible section for mobile
    st.markdown("---")
    st.markdown('<div class="collapsible-section">', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-header">', unsafe_allow_html=True)
    st.markdown("## Team Game Log")
    st.markdown('<div class="android-heading-fallback">Team Game Log</div>', unsafe_allow_html=True)
    st.markdown('<span class="collapsible-arrow">▼</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="collapsible-content">', unsafe_allow_html=True)
    
    # Create game log
    if not games_df.empty:
        # Sort games by date (most recent first)
        sorted_games = games_df.sort_values(by='Date', ascending=False)
        
        # Display game log
        st.dataframe(
            sorted_games[['Date', 'Opponent', 'Result', 'GoalsFor', 'GoalsAgainst']],
            column_config={
                'Date': st.column_config.TextColumn('Date'),
                'Opponent': st.column_config.TextColumn('Opponent'),
                'Result': st.column_config.TextColumn('Result'),
                'GoalsFor': st.column_config.NumberColumn('GF'),
                'GoalsAgainst': st.column_config.NumberColumn('GA')
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No game log data available.")
    
    # Close the game log collapsible section
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
