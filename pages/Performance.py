import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import load_data
import pandas as pd

st.title("📊 Performance Analysis")

matches, deliveries = load_data()

# Batting Performance
st.header("🏏 Batting Performance")

# Calculate batting stats
batting_runs = deliveries.groupby('batter')['batsman_runs'].sum()
batting_balls = deliveries.groupby('batter').size()
batting_dismissals = deliveries[deliveries['player_dismissed'] == deliveries['batter']].groupby('batter').size()

batting_stats = pd.DataFrame({
    'Runs': batting_runs,
    'Balls Faced': batting_balls,
    'Dismissals': batting_dismissals
}).fillna(0)

batting_stats['Average'] = batting_stats['Runs'] / batting_stats['Dismissals'].replace(0, 1)
batting_stats['Strike Rate'] = (batting_stats['Runs'] / batting_stats['Balls Faced']) * 100

# Filter players with minimum balls faced
min_balls = st.slider("Minimum Balls Faced", 50, 500, 100)
batting_filtered = batting_stats[batting_stats['Balls Faced'] >= min_balls].sort_values('Runs', ascending=False).head(20)

st.dataframe(batting_filtered[['Runs', 'Balls Faced', 'Dismissals', 'Average', 'Strike Rate']])

# Bowling Performance
st.header("🎯 Bowling Performance")

# Calculate bowling stats
bowling_wickets = deliveries[deliveries['is_wicket'] == 1].groupby('bowler').size()
bowling_runs = deliveries.groupby('bowler')['total_runs'].sum()
bowling_balls = deliveries.groupby('bowler').size()

bowling_stats = pd.DataFrame({
    'Wickets': bowling_wickets,
    'Runs Conceded': bowling_runs,
    'Balls Bowled': bowling_balls
}).fillna(0)

bowling_stats['Average'] = bowling_stats['Runs Conceded'] / bowling_stats['Wickets'].replace(0, 1)
bowling_stats['Economy'] = (bowling_stats['Runs Conceded'] / (bowling_stats['Balls Bowled'] / 6))

# Filter bowlers with minimum balls
min_balls_bowl = st.slider("Minimum Balls Bowled", 50, 500, 100)
bowling_filtered = bowling_stats[bowling_stats['Balls Bowled'] >= min_balls_bowl].sort_values('Wickets', ascending=False).head(20)

st.dataframe(bowling_filtered[['Wickets', 'Runs Conceded', 'Balls Bowled', 'Average', 'Economy']])