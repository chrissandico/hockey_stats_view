# **Design Document: Youth Hockey Statistics Web Application**

### **Project Overview**

This document outlines the design for a simple, intuitive web application built with Streamlit to display hockey statistics for a youth team. The primary audience is hockey parents who want quick and easy access to key player and team data. The application's design will prioritize a clean user interface and a user experience that is familiar and not overwhelming, inspired by the professional look of NHL.com.

### **Key Features**

The application will provide the following core functionalities, accessible through a straightforward navigation system:

1. **Player Game Stats:** Display individual stats for a selected player for a specific game.  
2. **Player Season Stats & Game Log:** Show a player's cumulative season totals and a detailed, chronological list of their performance in each game.  
3. **Team Summary Stats:** Present an overview of the team's overall season performance.  
4. **Leaderboards:** Show the top 5 players for three key categories: Goals, Assists, and Plus/Minus (filtered for defensemen).

### **User Interface (UI) Mockup & Navigation**

The application will be a single-page application with a sidebar for navigation to maintain simplicity.

#### **Main Navigation**

A simple sidebar on the left will contain the following links or buttons:

* **My Player's Stats:** This section will house the player-specific features.  
* **Team Stats & Leaderboards:** This section will display team-wide data and the leaderboards.

#### **My Player's Stats View**

This view is designed to answer "How did my son do during game x?" and "What are his season stats and game log?".

* **Player Selection:** At the top of the page, there will be a dropdown menu to select a player. The rest of the content will dynamically update based on this selection.  
* **Game-by-Game Section:** A second dropdown will allow users to select a specific game by date or opponent. When a game is selected, a "player card" will appear with key metrics for that game.  
  * **Metrics:** `st.metric` will be used to prominently display:  
    * Goals (G)  
    * Assists (A)  
    * Points (P)  
    * Plus/Minus (+/-)  
    * Shots on Goal (SOG)  
    * Penalty Minutes (PIM)  
* **Season Stats & Game Log:** Below the game-specific data, a new section will display the player's cumulative season statistics, followed by a detailed game log.  
  * **Season Totals:** Use `st.metric` or a simple table to show total G, A, P, and \+/- for the season.  
  * **Game Log Table:** A sortable `st.dataframe` or `st.table` will display the game log with columns for `Date`, `Opponent`, `Goals`, `Assists`, `Points`, and `+/-`.

#### **Team Stats & Leaderboards View**

This view is designed to answer "What are the team's season stats?" and display the requested leaderboards.

* **Team Summary:** A prominent section at the top will use `st.metric` to showcase team-wide stats:  
  * Wins (W), Losses (L), Ties (T)  
  * Points (PTS)  
  * Goals For (GF), Goals Against (GA)  
* **Leaderboards:** Below the summary, separate sections will display the requested leaderboards. Each leaderboard will be a simple, clean table listing the top 5 players.  
  * **Top 5 Goal Scorers:** `Player Name`, `Goals`, `Points`.  
  * **Top 5 Assists:** `Player Name`, `Assists`, `Points`.  
  * **Top 5 Plus/Minus (Defensemen):** `Player Name`, `Position`, `+/-`. This list will be explicitly filtered to only include players with the position "D".

### **Technical Architecture**

* **Frontend:** The entire application will be built using the Streamlit framework in Python.  
* **Data Source:** The data will be read directly from the shared Google Sheet.  
* **Data Processing:** The pandas library will be used for all data manipulation, including filtering, sorting, and aggregation to generate the stats and leaderboards.  
* **Google Sheet Integration:** The `gspread` library or a similar API wrapper will be used to securely access and read the data from the Google Sheet. Authentication will be configured to ensure the application has read-only access to the data.

### **Data Structure**

The application will rely on the following data structure from the provided Google Sheet URL, with each sheet serving a specific purpose:

* **`Roster` Sheet:**  
  * `Player Name` (string)  
  * `Jersey Number` (integer)  
  * `Position` (string: "D", "F", "G")  
* **`Game Log` Sheet:**  
  * `Game ID` (integer or string)  
  * `Player Name` (string)  
  * `Goals` (integer)  
  * `Assists` (integer)  
  * `Plus/Minus` (integer)  
  * `Shots` (integer)  
  * `PIM` (integer)  
  * `Opponent` (string)  
  * `Date` (date)

