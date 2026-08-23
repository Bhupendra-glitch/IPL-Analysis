import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import load_data

st.set_page_config(layout="wide")
st.title("🏆 Team Analysis Dashboard")

matches, deliveries = load_data()

# Sidebar team selection
st.sidebar.header("🎛️ Team Selection")
all_teams = sorted(pd.concat([matches['team1'], matches['team2']]).unique())
selected_team = st.sidebar.selectbox("Select Team", all_teams)

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Team Overview",
    "📈 Performance Stats",
    "🎯 Head-to-Head",
    "👥 Squad Analysis",
    "🏟️ Venue Insights",
    "📉 Match Patterns"
])

# ==================== TEAM OVERVIEW ====================
with tab1:
    st.header(f"🏆 {selected_team} - Team Overview")
    
    # Get team matches
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)].copy()
    team_matches['Result'] = team_matches.apply(
        lambda row: 'Won' if row['winner'] == selected_team else 'Lost' if row['winner'] != '' else 'No Result',
        axis=1
    )
    
    # Calculate stats
    total_matches = len(team_matches)
    wins = len(team_matches[team_matches['winner'] == selected_team])
    losses = len(team_matches[
        team_matches['winner'].notna() &
        (team_matches['winner'] != '') &
        (team_matches['winner'] != selected_team)
    ])
    no_results = total_matches - wins - losses
    win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0
    
    # Use the delivery team fields so team2 innings are included correctly.
    team_batting_deliveries = deliveries[deliveries['batting_team'] == selected_team]
    team_bowling_deliveries = deliveries[deliveries['bowling_team'] == selected_team]
    team_runs_scored = team_batting_deliveries['total_runs'].sum()
    runs_conceded = team_bowling_deliveries['total_runs'].sum()
    
    # Calculate average runs per match
    avg_runs_for = team_runs_scored / total_matches if total_matches > 0 else 0
    avg_runs_against = runs_conceded / total_matches if total_matches > 0 else 0
    recent_results = team_matches['winner'].tail(5).apply(
        lambda winner: 'W' if winner == selected_team else 'L' if pd.notna(winner) and winner != '' else 'NR'
    ).tolist()
    recent_form = ' - '.join(recent_results) if recent_results else 'N/A'
    
    # KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("🎯 Total Matches", total_matches)
    with col2:
        st.metric("🏆 Wins", wins)
    with col3:
        st.metric("📉 Losses", losses)
    with col4:
        st.metric("📊 Win %", f"{win_percentage:.1f}%")
    with col5:
        st.metric("📈 Avg For", f"{avg_runs_for:.0f}")
    with col6:
        st.metric("📉 Avg Against", f"{avg_runs_against:.0f}")

    st.caption(f"Recent form (oldest to newest): {recent_form} | No results: {no_results}")
    
    # Recent form
    st.subheader("📋 Recent Matches (Last 10)")
    recent_matches = team_matches.tail(10)[['date', 'team1', 'team2', 'winner', 'venue']].copy()
    recent_matches.columns = ['Date', 'Team 1', 'Team 2', 'Winner', 'Venue']
    st.dataframe(recent_matches, use_container_width=True)
    
    # Team composition
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎲 Match Results Distribution")
        results_data = team_matches['Result'].value_counts().reset_index()
        results_data.columns = ['Result', 'Count']
        
        fig_results = px.pie(results_data, values='Count', names='Result',
                            title="Win/Loss Distribution",
                            color_discrete_map={'Won': 'green', 'Lost': 'red', 'No Result': 'gray'})
        st.plotly_chart(fig_results, use_container_width=True)
    
    with col2:
        st.subheader("📊 Team Summary")
        summary_text = f"""
        **{selected_team} Statistics**
        
        - **Total Matches:** {total_matches}
        - **Wins:** {wins}
        - **Losses:** {losses}
        - **No Results:** {no_results}
        - **Win Rate:** {win_percentage:.2f}%
        - **Current Form:** {"🔥 Good" if win_percentage > 50 else "⚠️ Average" if win_percentage > 33 else "❌ Poor"}
        
        **Batting Performance:**
        - Avg Runs/Match: {avg_runs_for:.0f}
        - Avg Runs Conceded/Match: {avg_runs_against:.0f}
        - Seasons Played: {team_matches['season'].nunique()}
        """
        st.info(summary_text)

# ==================== PERFORMANCE STATISTICS ====================
with tab2:
    st.header(f"📈 {selected_team} - Performance Statistics")
    
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Performance Over Seasons")
        
        # Win/Loss per season
        team_matches['season_key'] = team_matches['season']
        season_performance = team_matches.groupby('season_key').apply(
            lambda x: pd.Series({
                'Wins': len(x[x['winner'] == selected_team]),
                'Total': len(x)
            })
        ).reset_index()
        season_performance['Win %'] = (season_performance['Wins'] / season_performance['Total'] * 100).round(2)
        
        fig_season = px.bar(season_performance, x='season_key', y=['Wins', 'Total'],
                           title="Wins vs Total Matches per Season",
                           barmode='group')
        st.plotly_chart(fig_season, use_container_width=True)
    
    with col2:
        st.subheader("📊 Win % Trend Over Seasons")
        fig_trend = px.line(season_performance, x='season_key', y='Win %',
                           title="Win Percentage Trend",
                           markers=True,
                           line_shape='linear')
        fig_trend.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="50% Mark")
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Detailed stats table
    st.subheader("📋 Season-wise Performance")
    st.dataframe(season_performance, use_container_width=True)
    
    # Runs statistics
    st.subheader("🏏 Batting Statistics Over Seasons")
    
    runs_by_season = []
    for season in team_matches['season'].unique():
        season_data = team_matches[team_matches['season'] == season]
        season_match_ids = season_data['id'].tolist()

        # Get only the selected team's batting innings for this season.
        team_runs = deliveries[
            deliveries['match_id'].isin(season_match_ids) &
            (deliveries['batting_team'] == selected_team)
        ]['total_runs'].sum()
        
        total_runs = team_runs
        matches_count = len(season_data)
        avg_runs = total_runs / matches_count if matches_count > 0 else 0
        
        runs_by_season.append({
            'Season': season,
            'Total Runs': total_runs,
            'Matches': matches_count,
            'Avg Runs/Match': avg_runs
        })
    
    runs_df = pd.DataFrame(runs_by_season).sort_values('Season')
    
    fig_runs = px.bar(runs_df, x='Season', y='Avg Runs/Match',
                     title="Average Runs per Match by Season",
                     color='Avg Runs/Match',
                     color_continuous_scale='Oranges')
    st.plotly_chart(fig_runs, use_container_width=True)

# ==================== HEAD-TO-HEAD ANALYSIS ====================
with tab3:
    st.header(f"🎯 {selected_team} - Head-to-Head Records")
    
    # Get all opponents
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)].copy()
    
    # Identify opponents
    opponents = []
    for idx, row in team_matches.iterrows():
        opponent = row['team2'] if row['team1'] == selected_team else row['team1']
        opponents.append(opponent)
    
    team_matches['opponent'] = opponents
    
    # Head-to-head stats
    h2h_stats = []
    for opponent in team_matches['opponent'].unique():
        h2h_matches = team_matches[team_matches['opponent'] == opponent]
        wins_vs_opponent = len(h2h_matches[h2h_matches['winner'] == selected_team])
        total_h2h = len(h2h_matches)
        
        h2h_stats.append({
            'Opponent': opponent,
            'Wins': wins_vs_opponent,
            'Losses': total_h2h - wins_vs_opponent,
            'Total Matches': total_h2h,
            'Win %': (wins_vs_opponent / total_h2h * 100) if total_h2h > 0 else 0
        })
    
    h2h_df = pd.DataFrame(h2h_stats).sort_values('Total Matches', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Head-to-Head Records")
        fig_h2h = px.bar(h2h_df.head(10), x='Opponent', y=['Wins', 'Losses'],
                        title="H2H Record vs Top Opponents",
                        barmode='stack',
                        color_discrete_map={'Wins': 'green', 'Losses': 'red'})
        fig_h2h.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_h2h, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Best Records Against")
        best_records = h2h_df[h2h_df['Total Matches'] >= 2].nlargest(5, 'Win %')
        
        for idx, row in best_records.iterrows():
            st.write(f"vs **{row['Opponent']}**: {int(row['Wins'])}-{int(row['Losses'])} ({row['Win %']:.1f}%)")
    
    # Difficult opponents
    if len(h2h_df[h2h_df['Total Matches'] >= 2]) > 0:
        st.subheader("⚠️ Difficult Opponents")
        worst_records = h2h_df[h2h_df['Total Matches'] >= 2].nsmallest(5, 'Win %')
        
        for idx, row in worst_records.iterrows():
            st.write(f"vs **{row['Opponent']}**: {int(row['Wins'])}-{int(row['Losses'])} ({row['Win %']:.1f}%)")
    
    # Detailed H2H table
    st.subheader("📋 Complete Head-to-Head Statistics")
    h2h_display = h2h_df[['Opponent', 'Wins', 'Losses', 'Total Matches', 'Win %']].copy()
    h2h_display['Win %'] = h2h_display['Win %'].round(2)
    st.dataframe(h2h_display, use_container_width=True)

# ==================== SQUAD ANALYSIS ====================
with tab4:
    st.header(f"👥 {selected_team} - Squad Analysis")
    
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)].copy()
    team_match_ids = team_matches['id'].tolist()
    team_deliveries = deliveries[deliveries['match_id'].isin(team_match_ids)]
    
    col1, col2, col3 = st.columns(3)
    
    # Top batsmen
    with col1:
        st.subheader("🏏 Top Batsmen")
        top_batsmen = team_deliveries[team_deliveries['batting_team'] == selected_team].groupby('batter')['batsman_runs'].sum().nlargest(10).reset_index()
        top_batsmen.columns = ['Player', 'Runs']
        
        fig_bat = px.bar(top_batsmen, x='Player', y='Runs',
                        title="Top 10 Scorers",
                        color='Runs',
                        color_continuous_scale='Blues')
        fig_bat.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_bat, use_container_width=True)
    
    # Top bowlers
    with col2:
        st.subheader("🎯 Top Bowlers")
        top_bowlers = team_deliveries[
            (team_deliveries['bowling_team'] == selected_team) &
            (team_deliveries['is_wicket'] == 1)
        ].groupby('bowler').size().nlargest(10).reset_index(name='Wickets')
        
        fig_bowl = px.bar(top_bowlers, x='bowler', y='Wickets',
                         title="Top 10 Wicket-Takers",
                         color='Wickets',
                         color_continuous_scale='Reds')
        fig_bowl.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_bowl, use_container_width=True)
    
    # Player diversity
    with col3:
        st.subheader("👥 Squad Diversity")
        stats_text = f"""
        **Squad Statistics**
        
        - **Total Matches:** {len(team_matches)}
        - **Unique Batsmen:** {team_deliveries['batter'].nunique()}
        - **Unique Bowlers:** {team_deliveries['bowler'].nunique()}
        - **Seasons:** {team_matches['season'].nunique()}
        
        **Key Players:**
        - Top Scorer: {top_batsmen.iloc[0]['Player']} ({int(top_batsmen.iloc[0]['Runs'])} runs)
        - Leading Bowler: {top_bowlers.iloc[0]['bowler']} ({int(top_bowlers.iloc[0]['Wickets'])} wickets)
        """
        st.info(stats_text)
    
    # Detailed squad stats
    st.subheader("📋 Batting Statistics")
    batting_stats = team_deliveries[team_deliveries['batting_team'] == selected_team].groupby('batter').agg({
        'batsman_runs': ['sum', 'count', 'mean'],
    }).reset_index()
    batting_stats.columns = ['Player', 'Runs', 'Balls', 'Avg per Ball']
    batting_stats['Strike Rate'] = (batting_stats['Runs'] / batting_stats['Balls'] * 100).round(2)
    batting_stats = batting_stats.sort_values('Runs', ascending=False).head(15)
    st.dataframe(batting_stats, use_container_width=True)

# ==================== VENUE ANALYSIS ====================
with tab5:
    st.header(f"🏟️ {selected_team} - Venue Performance")
    
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)].copy()
    
    # Venue performance
    venue_stats = []
    for venue in team_matches['venue'].unique():
        venue_matches = team_matches[team_matches['venue'] == venue]
        wins = len(venue_matches[venue_matches['winner'] == selected_team])
        total = len(venue_matches)
        
        venue_stats.append({
            'Venue': venue,
            'Matches': total,
            'Wins': wins,
            'Losses': total - wins,
            'Win %': (wins / total * 100) if total > 0 else 0
        })
    
    venue_df = pd.DataFrame(venue_stats).sort_values('Matches', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏟️ Best Venues (By Matches)")
        fig_venue_matches = px.bar(venue_df.head(10), x='Venue', y='Matches',
                                  title="Top 10 Venues - Matches Played",
                                  color='Matches',
                                  color_continuous_scale='Greens')
        fig_venue_matches.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_venue_matches, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Best Win Rate (Min 3 Matches)")
        best_venues = venue_df[venue_df['Matches'] >= 3].nlargest(10, 'Win %')
        fig_venue_wr = px.bar(best_venues, x='Venue', y='Win %',
                             title="Best Win % at Venues (Min 3 Matches)",
                             color='Win %',
                             color_continuous_scale='RdYlGn')
        fig_venue_wr.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_venue_wr, use_container_width=True)
    
    # Venue details table
    st.subheader("📋 Venue Performance Details")
    venue_display = venue_df[['Venue', 'Matches', 'Wins', 'Losses', 'Win %']].copy()
    venue_display['Win %'] = venue_display['Win %'].round(2)
    st.dataframe(venue_display, use_container_width=True)

# ==================== MATCH PATTERNS ====================
with tab6:
    st.header(f"📉 {selected_team} - Match Patterns & Analysis")
    
    team_matches = matches[(matches['team1'] == selected_team) | (matches['team2'] == selected_team)].copy()
    team_match_ids = team_matches['id'].tolist()
    team_deliveries = deliveries[
        deliveries['match_id'].isin(team_match_ids) &
        (deliveries['batting_team'] == selected_team)
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🪙 Toss Decision Impact")
        
        # Analyze toss decisions
        team_matches['Is Team Toss Winner'] = team_matches['toss_winner'] == selected_team
        team_matches['Is Team Match Winner'] = team_matches['winner'] == selected_team
        
        toss_impact = team_matches.copy()
        toss_impact['Toss Decision'] = toss_impact['toss_decision']
        
        decision_stats = toss_impact[toss_impact['Is Team Toss Winner']].groupby('toss_decision').apply(
            lambda x: pd.Series({
                'Total': len(x),
                'Wins': len(x[x['Is Team Match Winner']]),
                'Win %': (len(x[x['Is Team Match Winner']]) / len(x) * 100) if len(x) > 0 else 0
            })
        ).reset_index()
        
        if len(decision_stats) > 0:
            fig_decision = px.bar(decision_stats, x='toss_decision', y='Win %',
                                 title="Win % by Toss Decision",
                                 color='Win %',
                                 color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_decision, use_container_width=True)
        
        toss_wins = len(team_matches[team_matches['Is Team Toss Winner']])
        toss_win_pct = (toss_wins / len(team_matches) * 100) if len(team_matches) > 0 else 0
        st.metric("🪙 Toss Win %", f"{toss_win_pct:.1f}%")
    
    with col2:
        st.subheader("⏱️ Performance by Season")
        
        season_perf = team_matches.groupby('season').apply(
            lambda x: pd.Series({
                'Wins': len(x[x['winner'] == selected_team]),
                'Total': len(x)
            })
        ).reset_index()
        
        season_perf['Win %'] = (season_perf['Wins'] / season_perf['Total'] * 100).round(2)
        
        fig_season_perf = px.line(season_perf, x='season', y='Win %',
                                 markers=True,
                                 title="Win % Trend Over Seasons",
                                 line_shape='linear')
        st.plotly_chart(fig_season_perf, use_container_width=True)
    
    # Insights
    st.subheader("💡 Team Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Batting insights
        team_del_runs = team_deliveries['total_runs'].sum()
        avg_runs_per_match = team_del_runs / len(team_matches) if len(team_matches) > 0 else 0
        
        insights = f"""
        **Batting Insights:**
        - Total Runs: {int(team_del_runs)}
        - Avg Runs/Match: {avg_runs_per_match:.0f}
        - Batting Form: {"🔥 Strong" if avg_runs_per_match > 150 else "⚠️ Moderate" if avg_runs_per_match > 120 else "❌ Weak"}
        
        **Key Stats:**
        - Win Rate: {(len(team_matches[team_matches['winner'] == selected_team]) / len(team_matches) * 100):.1f}%
        """
        if len(venue_df) > 0:
            best_venue = venue_df.nlargest(1, 'Win %').iloc[0]
            insights += f"\n- Best Venue: {best_venue['Venue']} ({best_venue['Win %']:.1f}%)"
        
        st.info(insights)
    
    with col2:
        # Recommendations
        best_venue = venue_df.nlargest(1, 'Win %').iloc[0]
        worst_venue = venue_df.nsmallest(1, 'Win %').iloc[0]
        
        recommendations = f"""
        **Performance Analysis:**
        - Best Performing Venue: {best_venue['Venue']} ({best_venue['Win %']:.1f}%)
        - Challenging Venue: {worst_venue['Venue']} ({worst_venue['Win %']:.1f}%)
        
        **Recommendations:**
        ✅ Leverage strength against weaker opponents
        ✅ Focus on home games with high win rate
        ⚠️ Prepare special strategies for difficult venues
        ✅ Continue strong batting performances
        """
        st.success(recommendations)
