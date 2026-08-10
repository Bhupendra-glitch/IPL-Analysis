import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import load_data

st.set_page_config(layout="wide")
st.title("📅 Season Trends Analytics")

matches, deliveries = load_data()

# Sidebar filters
st.sidebar.header("🎛️ Filters")
all_seasons = sorted(matches['season'].unique())
selected_seasons = st.sidebar.multiselect("Select Seasons", all_seasons, default=all_seasons)

# Filter data based on selection
if not selected_seasons:
    st.warning("⚠️ Please select at least one season to view data")
    st.stop()

filtered_matches = matches[matches['season'].isin(selected_seasons)]
if len(filtered_matches) == 0:
    st.warning("⚠️ No data available for selected seasons")
    st.stop()

filtered_deliveries = deliveries[deliveries['match_id'].isin(filtered_matches['id'])]

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overall Trends",
    "🏆 Team Performance",
    "🏏 Batting Trends",
    "🎯 Match Patterns",
    "📈 Statistics",
    "🔍 Insights"
])

# ==================== OVERALL TRENDS ====================
with tab1:
    st.header("📊 Season-wise Overall Trends")
    
    # Matches per season
    matches_per_season = filtered_matches.groupby('season').size().reset_index(name='Matches')
    
    # Calculate runs per season
    runs_per_season = filtered_deliveries.groupby(filtered_deliveries['match_id'].map(
        filtered_matches.set_index('id')['season'].to_dict()
    ))['total_runs'].sum().groupby(level=0).sum().reset_index()
    runs_per_season.columns = ['season', 'Total Runs']
    
    # Merge data
    season_data = matches_per_season.merge(runs_per_season, on='season', how='left').fillna(0)
    season_data['Avg Runs per Match'] = (season_data['Total Runs'] / season_data['Matches']).round(2)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total Matches", int(season_data['Matches'].sum()))
    with col2:
        st.metric("🏏 Total Runs", int(season_data['Total Runs'].sum()))
    with col3:
        st.metric("📈 Avg Runs/Match", f"{season_data['Avg Runs per Match'].mean():.2f}")
    with col4:
        st.metric("🎯 Seasons", len(selected_seasons))
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_matches = px.bar(season_data, x='season', y='Matches',
                            title="Matches per Season",
                            color='Matches',
                            color_continuous_scale='Blues',
                            markers=False)
        fig_matches.update_layout(height=400)
        st.plotly_chart(fig_matches, use_container_width=True)
    
    with col2:
        fig_runs = px.line(season_data, x='season', y='Total Runs',
                          title="Total Runs per Season",
                          markers=True,
                          line_shape='linear')
        fig_runs.update_layout(height=400)
        st.plotly_chart(fig_runs, use_container_width=True)
    
    # Season comparison table
    st.subheader("📋 Season-wise Statistics")
    season_display = season_data[['season', 'Matches', 'Total Runs', 'Avg Runs per Match']].copy()
    season_display.columns = ['Season', 'Matches', 'Total Runs', 'Avg Runs/Match']
    st.dataframe(season_display, use_container_width=True)

# ==================== TEAM PERFORMANCE TRENDS ====================
with tab2:
    st.header("🏆 Team Performance Over Seasons")
    
    # Get team wins per season
    team_wins = filtered_matches.groupby(['season', 'winner']).size().reset_index(name='Wins')
    team_wins.columns = ['season', 'team', 'wins']
    
    # Get top teams
    top_teams = team_wins.groupby('team')['wins'].sum().nlargest(5).index.tolist()
    team_wins_filtered = team_wins[team_wins['team'].isin(top_teams)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Top Teams - Wins Trend")
        fig_team_wins = px.line(team_wins_filtered, x='season', y='wins', color='team',
                               title="Top 5 Teams - Wins Over Seasons",
                               markers=True)
        fig_team_wins.update_layout(height=400)
        st.plotly_chart(fig_team_wins, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Total Wins by Team (Selected Seasons)")
        total_wins = team_wins.groupby('team')['wins'].sum().nlargest(10).reset_index()
        fig_total_wins = px.bar(total_wins, x='team', y='wins',
                               title="All-Time Wins (in Selected Seasons)",
                               color='wins',
                               color_continuous_scale='Greens')
        fig_total_wins.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_total_wins, use_container_width=True)
    
    # Team performance matrix
    st.subheader("📊 Team Season Performance Matrix")
    team_season_matrix = filtered_matches.groupby(['season', 'winner']).size().unstack(fill_value=0)
    st.dataframe(team_season_matrix, use_container_width=True)

# ==================== BATTING TRENDS ====================
with tab3:
    st.header("🏏 Batting Trends Over Seasons")
    
    # Calculate batting stats per season
    batting_by_season = []
    for season in selected_seasons:
        season_matches = filtered_matches[filtered_matches['season'] == season]['id']
        season_deliveries = filtered_deliveries[filtered_deliveries['match_id'].isin(season_matches)]
        
        total_runs = season_deliveries['batsman_runs'].sum()
        total_balls = len(season_deliveries)
        avg_sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
        matches_count = len(season_matches)
        avg_runs_per_match = total_runs / matches_count if matches_count > 0 else 0
        
        batting_by_season.append({
            'Season': season,
            'Total Runs': total_runs,
            'Total Balls': total_balls,
            'Strike Rate': avg_sr,
            'Avg Runs/Match': avg_runs_per_match
        })
    
    batting_df = pd.DataFrame(batting_by_season)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sr = px.line(batting_df, x='Season', y='Strike Rate',
                        title="Average Strike Rate Trend",
                        markers=True,
                        line_shape='linear')
        fig_sr.update_layout(height=400)
        st.plotly_chart(fig_sr, use_container_width=True)
    
    with col2:
        fig_avg_runs = px.bar(batting_df, x='Season', y='Avg Runs/Match',
                             title="Average Runs per Match Trend",
                             color='Avg Runs/Match',
                             color_continuous_scale='Oranges')
        fig_avg_runs.update_layout(height=400)
        st.plotly_chart(fig_avg_runs, use_container_width=True)
    
    # Batting statistics table
    st.subheader("📋 Batting Statistics per Season")
    batting_display = batting_df[['Season', 'Total Runs', 'Strike Rate', 'Avg Runs/Match']].copy()
    batting_display['Strike Rate'] = batting_display['Strike Rate'].round(2)
    batting_display['Avg Runs/Match'] = batting_display['Avg Runs/Match'].round(2)
    st.dataframe(batting_display, use_container_width=True)
    
    # Top batsmen per season
    st.subheader("⭐ Top Batsmen per Season")
    top_batsmen_season = []
    for season in selected_seasons:
        season_matches = filtered_matches[filtered_matches['season'] == season]['id']
        season_deliveries = filtered_deliveries[filtered_deliveries['match_id'].isin(season_matches)]
        
        top_batter = season_deliveries.groupby('batter')['batsman_runs'].sum().nlargest(1)
        if len(top_batter) > 0:
            top_batsmen_season.append({
                'Season': season,
                'Top Batsman': top_batter.index[0],
                'Runs': int(top_batter.values[0])
            })
    
    top_batsmen_df = pd.DataFrame(top_batsmen_season)
    st.dataframe(top_batsmen_df, use_container_width=True)

# ==================== MATCH PATTERNS ====================
with tab4:
    st.header("🎯 Match Patterns & Trends")
    
    # Toss wins vs match wins
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🪙 Toss Impact Analysis")
        toss_impact = filtered_matches.copy()
        toss_impact['Toss Winner Won'] = toss_impact['toss_winner'] == toss_impact['winner']
        toss_impact['Toss Impact'] = toss_impact['Toss Winner Won'].apply(lambda x: 'Won' if x else 'Lost')
        
        toss_stats = toss_impact.groupby('Toss Impact').size().reset_index(name='Count')
        fig_toss = px.pie(toss_stats, values='Count', names='Toss Impact',
                         title="Toss Winner Match Outcome",
                         color_discrete_map={'Won': 'green', 'Lost': 'red'})
        st.plotly_chart(fig_toss, use_container_width=True)
        
        # Calculate toss win percentage
        toss_win_pct = (toss_impact['Toss Winner Won'].sum() / len(toss_impact) * 100)
        st.metric("🪙 Toss Win Conversion", f"{toss_win_pct:.1f}%")
    
    with col2:
        st.subheader("🏟️ Venue Distribution")
        venue_counts = filtered_matches['venue'].value_counts().head(10).reset_index()
        venue_counts.columns = ['venue', 'matches']
        
        fig_venue = px.bar(venue_counts, x='venue', y='matches',
                          title="Top 10 Venues - Matches Hosted",
                          color='matches',
                          color_continuous_scale='Viridis')
        fig_venue.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_venue, use_container_width=True)
    
    # Match duration trends
    st.subheader("⏱️ Match Duration Analysis")
    
    if 'date' in filtered_matches.columns:
        filtered_matches['date'] = pd.to_datetime(filtered_matches['date'])
        matches_over_time = filtered_matches.groupby(pd.Grouper(key='date', freq='M')).size().reset_index(name='Matches')
        
        fig_timeline = px.line(matches_over_time, x='date', y='Matches',
                              title="Matches Over Time",
                              markers=True)
        fig_timeline.update_layout(height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)

# ==================== DETAILED STATISTICS ====================
with tab5:
    st.header("📈 Detailed Season Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🎲 Top Teams")
        team_matches = filtered_matches['winner'].value_counts().head(5).reset_index()
        team_matches.columns = ['Team', 'Wins']
        st.dataframe(team_matches, use_container_width=True)
    
    with col2:
        st.subheader("🏏 Top Batsmen")
        top_batsmen = filtered_deliveries.groupby('batter')['batsman_runs'].sum().nlargest(5).reset_index()
        top_batsmen.columns = ['Player', 'Runs']
        st.dataframe(top_batsmen, use_container_width=True)
    
    with col3:
        st.subheader("🎯 Top Bowlers")
        top_bowlers = filtered_deliveries[filtered_deliveries['is_wicket'] == 1].groupby('bowler').size().nlargest(5).reset_index()
        top_bowlers.columns = ['Player', 'Wickets']
        st.dataframe(top_bowlers, use_container_width=True)
    
    # Statistics summary
    st.subheader("📊 Comprehensive Statistics")
    
    stats_summary = {
        'Total Matches': len(filtered_matches),
        'Total Runs (Across All Matches)': int(filtered_deliveries['total_runs'].sum()),
        'Total Balls': len(filtered_deliveries),
        'Unique Teams': filtered_matches['team1'].nunique() + filtered_matches['team2'].nunique(),
        'Unique Venues': filtered_matches['venue'].nunique(),
        'Unique Batsmen': filtered_deliveries['batter'].nunique(),
        'Unique Bowlers': filtered_deliveries['bowler'].nunique(),
        'Total Wickets': int(filtered_deliveries['is_wicket'].sum()),
    }
    
    stats_df = pd.DataFrame(list(stats_summary.items()), columns=['Metric', 'Value'])
    st.dataframe(stats_df, use_container_width=True)

# ==================== KEY INSIGHTS ====================
with tab6:
    st.header("🔍 Season Insights & Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Key Findings")
        
        # Calculate trends
        if len(season_data) > 1:
            first_season_matches = season_data.iloc[0]['Matches']
            last_season_matches = season_data.iloc[-1]['Matches']
            matches_trend = "📈 Increasing" if last_season_matches > first_season_matches else "📉 Decreasing"
            
            first_season_runs = season_data.iloc[0]['Avg Runs per Match']
            last_season_runs = season_data.iloc[-1]['Avg Runs per Match']
            runs_trend = "📈 Increasing" if last_season_runs > first_season_runs else "📉 Decreasing"
            
            insights = f"""
            **Match Frequency:** {matches_trend}
            - First season: {int(first_season_matches)} matches
            - Last season: {int(last_season_matches)} matches
            
            **Scoring Trend:** {runs_trend}
            - First season avg: {first_season_runs:.2f} runs/match
            - Last season avg: {last_season_runs:.2f} runs/match
            
            **Most Active Season:** {season_data.loc[season_data['Matches'].idxmax(), 'season']} ({int(season_data['Matches'].max())} matches)
            
            **Highest Scoring Season:** {season_data.loc[season_data['Total Runs'].idxmax(), 'season']} ({int(season_data['Total Runs'].max())} total runs)
            """
            st.info(insights)
    
    with col2:
        st.subheader("🏆 Team Insights")
        
        if len(filtered_matches) > 0:
            most_wins_team = filtered_matches['winner'].value_counts().idxmax()
            most_wins_count = filtered_matches['winner'].value_counts().max()
            
            total_unique_teams = filtered_matches['team1'].nunique()
            avg_wins_per_team = most_wins_count / total_unique_teams if total_unique_teams > 0 else 0
            
            team_insights = f"""
            **Most Successful Team:** {most_wins_team}
            - Total Wins: {int(most_wins_count)}
            
            **Team Participation:** {int(total_unique_teams)} teams
            - Avg wins per team: {avg_wins_per_team:.1f}
            
            **Toss Significance:** {toss_win_pct:.1f}% of toss winners won the match
            
            **Top Venue:** {venue_counts.iloc[0]['venue'] if len(venue_counts) > 0 else 'N/A'}
            - Matches hosted: {int(venue_counts.iloc[0]['matches']) if len(venue_counts) > 0 else 0}
            """
            st.info(team_insights)
    
    # Performance comparison
    st.subheader("📊 Season-over-Season Comparison")
    
    if len(season_data) > 1:
        season_data['Matches Change'] = season_data['Matches'].diff()
        season_data['Runs Change'] = season_data['Total Runs'].diff()
        
        comparison_display = season_data[['season', 'Matches', 'Matches Change', 'Total Runs', 'Runs Change', 'Avg Runs per Match']].copy()
        comparison_display['Matches Change'] = comparison_display['Matches Change'].fillna(0).astype(int)
        comparison_display['Runs Change'] = comparison_display['Runs Change'].fillna(0).astype(int)
        comparison_display['Avg Runs per Match'] = comparison_display['Avg Runs per Match'].round(2)
        
        st.dataframe(comparison_display, use_container_width=True)