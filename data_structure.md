# Google Sheets Data Structure

## "Players" Sheet/Table
- **ID**: Unique Player ID (e.g., "1", "2", "3")
- **JerseyNumber**: The Player's Jersey Number (e.g., "10", "17", "99")
- **FirstName**: Player's first name
- **LastName**: Player's last name
- **TeamID**: The team they play on
- **Position**: The position they play ("F" for Forward, "D" for Defense, "G" for Goalie)

## "Games" Sheet/Table
- **ID**: Unique Game ID (used as GameID in the application)
- **Date**: Date of the game (e.g., "2024-01-15")
- **Opponent**: Name of the opposing team
- **Location**: Where the game was played
- **Result**: Game result ("W" for Win, "L" for Loss, "T" for Tie) - calculated from Events
- **GoalsFor**: Goals scored by your team - calculated from Events
- **GoalsAgainst**: Goals scored by opponent - calculated from Events

## "Events" Sheet/Table
- **GameID**: References the Game ID
- **EventType**: Type of event (e.g., "Goal", "Shot", "Penalty", "Hit", "Faceoff")
- **Period**: Period when event occurred (e.g., "1", "2", "3", "OT")
- **Time**: Time in period when event occurred (e.g., "12:34")
- **PrimaryPlayerID**: ID of the player who performed the event
- **AssistPlayer1ID**: ID of first assist player (for goals)
- **AssistPlayer2ID**: ID of second assist player (for goals)
- **Team**: Which team performed the event ("your_team" or opponent name)
- **IsGoal**: Boolean indicating if this event was a goal
- **IsPowerPlay**: Boolean indicating if goal was on power play
- **IsShortHanded**: Boolean indicating if goal was short-handed
- **PenaltyType**: Type of penalty (if EventType is "Penalty")
- **PenaltyDuration**: Duration of penalty in minutes
- **YourTeamPlayersOnIce**: Comma-separated list of player IDs on ice (e.g., "player_1,player_2,player_3")

## "GameRoster" Sheet/Table
- **GameID**: References the Game ID
- **PlayerID**: References the Player ID (stored with "player_" prefix, e.g., "player_1", "player_2")
- **Status**: Player's status for the game ("Present" or "Absent")

This sheet tracks which players were present or absent for each game, allowing for accurate "Games Played" statistics and proper roster display in game stats views.
