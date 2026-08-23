import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data, get_teams

st.set_page_config(page_title="Team Analysis", page_icon="🏏", layout="wide")
st.title("🏏 Team Analysis Dashboard")
st.caption("Explore results, scoring patterns, opponents, venues, and key players.")

matches, deliveries = load_data()
teams = sorted(pd.concat([matches['team1'], matches['team2']]).dropna().unique())

team = st.selectbox("Select Team", teams, key="team_analysis_team")

team_matches = matches[
    (matches['team1'] == team) | (matches['team2'] == team)
].copy()
team_matches['Result'] = team_matches['winner'].apply(
    lambda winner: 'Won' if winner == team else 'Lost'
    if pd.notna(winner) and winner != '' else 'No Result'
)

team_batting = deliveries[deliveries['batting_team'] == team].copy()
team_bowling = deliveries[deliveries['bowling_team'] == team].copy()

wins = int((team_matches['Result'] == 'Won').sum())
losses = int((team_matches['Result'] == 'Lost').sum())
no_results = int((team_matches['Result'] == 'No Result').sum())
total_matches = len(team_matches)
win_rate = wins / total_matches * 100 if total_matches else 0
total_runs = int(team_batting['total_runs'].sum())
runs_conceded = int(team_bowling['total_runs'].sum())
avg_runs = total_runs / total_matches if total_matches else 0
avg_conceded = runs_conceded / total_matches if total_matches else 0

metric_cols = st.columns(6)
metric_cols[0].metric("Matches", total_matches)
metric_cols[1].metric("Wins", wins)
metric_cols[2].metric("Losses", losses)
metric_cols[3].metric("No Results", no_results)
metric_cols[4].metric("Win Rate", f"{win_rate:.1f}%")
metric_cols[5].metric("Avg Run Margin", f"{avg_runs - avg_conceded:+.1f}")

st.markdown("---")
overview_col, season_col = st.columns(2)

with overview_col:
    st.subheader("📊 Match Results")
    result_counts = team_matches['Result'].value_counts().reindex(
        ['Won', 'Lost', 'No Result'], fill_value=0
    ).rename_axis('Result').reset_index(name='Matches')
    result_fig = px.pie(
        result_counts, names='Result', values='Matches', hole=0.45,
        color='Result', color_discrete_map={'Won': '#1f9d55', 'Lost': '#d64545', 'No Result': '#88909b'}
    )
    result_fig.update_layout(height=320, margin=dict(t=20, b=10, l=10, r=10))
    st.plotly_chart(result_fig, use_container_width=True)

with season_col:
    st.subheader("📈 Season Performance")
    season_stats = team_matches.groupby('season', as_index=False).agg(
        Matches=('id', 'count'),
        Wins=('Result', lambda values: (values == 'Won').sum())
    )
    season_stats['Win Rate'] = (season_stats['Wins'] / season_stats['Matches'] * 100).round(1)
    season_fig = px.bar(
        season_stats, x='season', y='Win Rate', text='Win Rate',
        labels={'season': 'Season', 'Win Rate': 'Win rate (%)'},
        color='Win Rate', color_continuous_scale='RdYlGn'
    )
    season_fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    season_fig.update_layout(height=320, coloraxis_showscale=False, yaxis_range=[0, 105])
    st.plotly_chart(season_fig, use_container_width=True)

st.subheader("🏏 Scoring Profile")
score_col1, score_col2 = st.columns(2)
with score_col1:
    st.metric("Total Runs Scored", f"{total_runs:,}")
    st.caption(f"Average batting output: {avg_runs:.1f} runs per match")
with score_col2:
    st.metric("Total Runs Conceded", f"{runs_conceded:,}")
    st.caption(f"Average conceded: {avg_conceded:.1f} runs per match")

opponents = team_matches.apply(
    lambda row: row['team2'] if row['team1'] == team else row['team1'], axis=1
)
opponent_stats = pd.DataFrame({'Opponent': opponents, 'Result': team_matches['Result'].values})
opponent_stats = opponent_stats.groupby('Opponent', as_index=False).agg(
    Matches=('Result', 'size'),
    Wins=('Result', lambda values: (values == 'Won').sum())
)
opponent_stats['Losses'] = opponent_stats['Matches'] - opponent_stats['Wins']
opponent_stats['Win Rate'] = (opponent_stats['Wins'] / opponent_stats['Matches'] * 100).round(1)
opponent_stats = opponent_stats.sort_values(['Matches', 'Win Rate'], ascending=[False, False])

opponent_col, venue_col = st.columns(2)
with opponent_col:
    st.subheader("🎯 Opponent Record")
    st.dataframe(opponent_stats, use_container_width=True, hide_index=True)

with venue_col:
    st.subheader("🏟️ Venue Win Rate")
    venue_stats = team_matches.groupby('venue', as_index=False).agg(
        Matches=('id', 'count'),
        Wins=('Result', lambda values: (values == 'Won').sum())
    )
    venue_stats['Win Rate'] = (venue_stats['Wins'] / venue_stats['Matches'] * 100).round(1)
    venue_stats = venue_stats.sort_values('Matches', ascending=False).head(10)
    venue_fig = px.bar(
        venue_stats, x='Win Rate', y='venue', orientation='h', text='Win Rate',
        labels={'venue': 'Venue', 'Win Rate': 'Win rate (%)'}, color='Win Rate',
        color_continuous_scale='Blues'
    )
    venue_fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    venue_fig.update_layout(height=420, coloraxis_showscale=False, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(venue_fig, use_container_width=True)

st.subheader("👥 Key Players")
player_col1, player_col2 = st.columns(2)
with player_col1:
    top_batters = team_batting.groupby('batter', as_index=False)['batsman_runs'].sum()
    top_batters = top_batters.nlargest(10, 'batsman_runs').rename(
        columns={'batter': 'Player', 'batsman_runs': 'Runs'}
    )
    st.dataframe(top_batters, use_container_width=True, hide_index=True)
with player_col2:
    top_bowlers = team_bowling[team_bowling['is_wicket'] == 1].groupby('bowler').size()
    top_bowlers = top_bowlers.nlargest(10).rename('Wickets').reset_index().rename(columns={'bowler': 'Player'})
    st.dataframe(top_bowlers, use_container_width=True, hide_index=True)

st.subheader("🗓️ Recent Matches")
recent = team_matches.sort_values('date', ascending=False).head(10)
recent_display = recent[['date', 'team1', 'team2', 'Result', 'venue']].rename(columns={
    'date': 'Date', 'team1': 'Team 1', 'team2': 'Team 2', 'venue': 'Venue'
})
st.dataframe(recent_display, use_container_width=True, hide_index=True)
