import streamlit as st
from utils import load_data, get_teams

st.title("🏏 Team Analysis")

matches, _ = load_data()
teams = get_teams(matches)

team = st.selectbox("Select Team", teams)

team_matches = matches[
    (matches['team1'] == team) | (matches['team2'] == team)
]

wins = team_matches[team_matches['winner'] == team]

st.metric("Matches Played", len(team_matches))
st.metric("Wins", len(wins))