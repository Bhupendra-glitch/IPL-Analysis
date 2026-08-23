import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

st.set_page_config(page_title="Head-to-Head", page_icon="⚔️", layout="wide")
st.title("⚔️ Head-to-Head Analysis")
st.caption("Compare two teams across results, scoring, venues, tosses, and recent meetings.")

matches, deliveries = load_data()
teams = sorted(pd.concat([matches['team1'], matches['team2']]).dropna().unique())

team1 = st.selectbox("Team 1", teams, key="h2h_team1")
team2 = st.selectbox("Team 2", teams, index=1 if len(teams) > 1 else 0, key="h2h_team2")

h2h = matches[
    ((matches['team1'] == team1) & (matches['team2'] == team2)) |
    ((matches['team1'] == team2) & (matches['team2'] == team1))
].copy()

if team1 == team2:
    st.warning("Select two different teams to compare.")
    st.stop()

if h2h.empty:
    st.info(f"No recorded matches found between {team1} and {team2}.")
    st.stop()

h2h['Winner'] = h2h['winner'].fillna('No Result')
h2h['Result'] = h2h['Winner'].apply(
    lambda winner: 'No Result' if winner == 'No Result' else 'Team 1' if winner == team1 else 'Team 2'
)

team1_wins = int((h2h['Winner'] == team1).sum())
team2_wins = int((h2h['Winner'] == team2).sum())
no_results = len(h2h) - team1_wins - team2_wins
team1_rate = team1_wins / len(h2h) * 100
team2_rate = team2_wins / len(h2h) * 100

metric_cols = st.columns(5)
metric_cols[0].metric("Meetings", len(h2h))
metric_cols[1].metric(f"{team1} Wins", team1_wins)
metric_cols[2].metric(f"{team2} Wins", team2_wins)
metric_cols[3].metric("No Results", no_results)
metric_cols[4].metric("Last Winner", h2h.sort_values('date').iloc[-1]['Winner'])

st.markdown("---")
record_col, trend_col = st.columns(2)

with record_col:
    st.subheader("📊 Overall Record")
    record_df = pd.DataFrame({
        'Team': [team1, team2, 'No Result'],
        'Matches': [team1_wins, team2_wins, no_results]
    })
    record_fig = px.bar(
        record_df, x='Team', y='Matches', text='Matches', color='Team',
        color_discrete_sequence=['#e76f51', '#2a9d8f', '#8d99ae']
    )
    record_fig.update_layout(height=320, showlegend=False, margin=dict(t=20, b=10, l=10, r=10))
    st.plotly_chart(record_fig, use_container_width=True)
    st.caption(f"Win rates: {team1} {team1_rate:.1f}% | {team2} {team2_rate:.1f}%")

with trend_col:
    st.subheader("📈 Season-by-Season Trend")
    season_trend = h2h.groupby('season', as_index=False).agg(
        **{team1: ('Winner', lambda values: (values == team1).sum()),
           team2: ('Winner', lambda values: (values == team2).sum()),
           'No Result': ('Winner', lambda values: (values == 'No Result').sum())}
    )
    trend_fig = px.bar(
        season_trend, x='season', y=[team1, team2, 'No Result'], barmode='group',
        labels={'value': 'Matches Won', 'variable': 'Outcome'}
    )
    trend_fig.update_layout(height=320, margin=dict(t=20, b=10, l=10, r=10))
    st.plotly_chart(trend_fig, use_container_width=True)

match_ids = h2h['id'].tolist()
h2h_deliveries = deliveries[deliveries['match_id'].isin(match_ids)]
score_by_match = h2h_deliveries.groupby(['match_id', 'batting_team'], as_index=False)['total_runs'].sum()
score_by_team = score_by_match[score_by_match['batting_team'].isin([team1, team2])]
score_summary = score_by_team.groupby('batting_team')['total_runs'].agg(['mean', 'max']).reindex([team1, team2])

stats_col, toss_col = st.columns(2)
with stats_col:
    st.subheader("🏏 Scoring Comparison")
    scoring_df = pd.DataFrame({
        'Team': [team1, team2],
        'Average Score': score_summary['mean'].fillna(0).round(1).values,
        'Highest Score': score_summary['max'].fillna(0).astype(int).values
    })
    st.dataframe(scoring_df, use_container_width=True, hide_index=True)

with toss_col:
    st.subheader("🪙 Toss Impact")
    toss_wins = int((h2h['toss_winner'] == team1).sum())
    toss_wins_2 = int((h2h['toss_winner'] == team2).sum())
    toss_df = pd.DataFrame({
        'Team': [team1, team2],
        'Toss Wins': [toss_wins, toss_wins_2],
        'Won Match After Toss': [
            int(((h2h['toss_winner'] == team1) & (h2h['Winner'] == team1)).sum()),
            int(((h2h['toss_winner'] == team2) & (h2h['Winner'] == team2)).sum())
        ]
    })
    toss_df['Conversion Rate'] = (toss_df['Won Match After Toss'] / toss_df['Toss Wins'] * 100).fillna(0).round(1)
    st.dataframe(toss_df, use_container_width=True, hide_index=True)

st.subheader("🏟️ Venue Breakdown")
venue_df = h2h.groupby(['venue', 'Winner'], as_index=False).size().rename(columns={'size': 'Matches'})
venue_fig = px.bar(
    venue_df, x='venue', y='Matches', color='Winner', barmode='stack',
    labels={'venue': 'Venue', 'Winner': 'Match outcome'}
)
venue_fig.update_layout(height=380, xaxis_tickangle=-35)
st.plotly_chart(venue_fig, use_container_width=True)

if h2h['player_of_match'].notna().any():
    st.subheader("⭐ Player of the Match Leaders")
    awards = h2h['player_of_match'].dropna().value_counts().head(10).rename_axis('Player').reset_index(name='Awards')
    st.dataframe(awards, use_container_width=True, hide_index=True)

st.subheader("🗓️ Recent Meetings")
recent = h2h.sort_values('date', ascending=False).head(10)
recent_display = recent[['date', 'season', 'team1', 'team2', 'Winner', 'result_margin', 'venue']].rename(columns={
    'date': 'Date', 'season': 'Season', 'team1': 'Team 1', 'team2': 'Team 2',
    'result_margin': 'Margin', 'venue': 'Venue'
})
st.dataframe(recent_display, use_container_width=True, hide_index=True)