import streamlit as st
from utils import load_data, get_teams

st.title("⚔️ Head-to-Head")

matches, _ = load_data()
teams = get_teams(matches)

team1 = st.selectbox("Team 1", teams)
team2 = st.selectbox("Team 2", teams)

h2h = matches[
    ((matches['team1'] == team1) & (matches['team2'] == team2)) |
    ((matches['team1'] == team2) & (matches['team2'] == team1))
]

st.write(h2h[['team1', 'team2', 'winner']])