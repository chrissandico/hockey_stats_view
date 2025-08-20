# Hockey Stats Web Application

A modern, responsive web application for tracking and displaying youth hockey statistics.

## Features

- **Player Statistics**: View individual player stats for specific games and season totals
- **Team Statistics**: Track team performance with season summaries and game logs
- **Game Statistics**: Analyze detailed game data with player performance and game timeline
- **Leaderboards**: View top performers in various categories, separated by position
- **Mobile Responsive**: Optimized for both desktop and mobile viewing

## Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **Data Storage**: Google Sheets integration
- **Authentication**: Google OAuth

## Getting Started

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your Google Sheets credentials in `.streamlit/secrets.toml`

3. Run the application:
   ```
   streamlit run app.py
   ```

## Project Structure

- `app.py`: Main application entry point
- `hockey_stats/`: Core package directory
  - `sheets_service.py`: Google Sheets integration
  - `utils.py`: Utility functions
  - `static/css/`: Custom styling
  - `components/`: UI components
    - `player_stats.py`: Player statistics view
    - `team_stats.py`: Team statistics and leaderboards view
    - `game_stats.py`: Game statistics view

## Data Structure

The application uses Google Sheets with the following structure:

- **Players Sheet**: Player information (ID, Name, Jersey Number, Position)
- **Games Sheet**: Game information (Date, Opponent, Result, Score)
- **Events Sheet**: Game events (Goals, Assists, Penalties, etc.)

## Customization

The application uses a blue and white color scheme inspired by the Toronto Maple Leafs. You can customize the colors and styling by modifying the CSS in `hockey_stats/static/css/style.css`.
