import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import load_data

st.set_page_config(layout="wide")
st.title("📍 Venue Analysis Dashboard")

matches, deliveries = load_data()

# Sidebar venue selection
st.sidebar.header("🎛️ Analysis Mode")
analysis_mode = st.sidebar.radio("Select Analysis Type", 
    ["📊 Single Venue", "🔄 Compare Venues", "🌍 All Venues Overview"])

all_venues = sorted(matches['venue'].unique())

if analysis_mode == "📊 Single Venue":
    st.sidebar.header("🎯 Venue Selection")
    selected_venue = st.sidebar.selectbox("Select Venue", all_venues)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Venue Overview",
        "🏆 Team Performance",
        "🏏 Batting Trends",
        "📈 Match Statistics",
        "👑 Player Stats",
        "🔍 Insights"
    ])

    # ==================== VENUE OVERVIEW ====================
    with tab1:
        st.header(f"📍 {selected_venue} - Venue Overview")
        
        # Get venue matches
        venue_matches = matches[matches['venue'] == selected_venue].copy()
        
        # Calculate stats
        total_matches = len(venue_matches)
        unique_teams = pd.concat([venue_matches['team1'], venue_matches['team2']]).nunique()
        seasons = venue_matches['season'].nunique()
        
        # Get winner distribution
        winner_dist = venue_matches['winner'].value_counts()
        
        # Get runs
        venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
        total_runs = venue_deliveries['total_runs'].sum()
        avg_runs_per_match = total_runs / total_matches if total_matches > 0 else 0
        
        # Highest run match
        highest_run_match = venue_deliveries.groupby('match_id')['total_runs'].sum().max()
        
        # KPI Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🎯 Total Matches", total_matches)
        with col2:
            st.metric("🏆 Unique Teams", unique_teams)
        with col3:
            st.metric("📊 Seasons", seasons)
        with col4:
            st.metric("📈 Avg Runs", f"{avg_runs_per_match:.0f}")
        with col5:
            st.metric("💯 Max Runs", int(highest_run_match))
        
        # Venue characteristics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Venue Characteristics")
            
            # Determine if high or low scoring
            league_avg_runs = matches.groupby('venue').apply(
                lambda x: deliveries[deliveries['match_id'].isin(x['match_id'])]['total_runs'].sum() / len(x)
            ).mean()
            
            venue_type = "🔥 High Scoring" if avg_runs_per_match > league_avg_runs * 1.1 else "🛡️ Low Scoring" if avg_runs_per_match < league_avg_runs * 0.9 else "⚖️ Neutral"
            
            char_text = f"""
            **{selected_venue}**
            
            - **Total Matches:** {total_matches}
            - **Unique Teams:** {unique_teams}
            - **Seasons Hosted:** {seasons}
            - **Average Runs/Match:** {avg_runs_per_match:.0f}
            - **Venue Type:** {venue_type}
            - **Highest Score:** {int(highest_run_match)} runs
            - **Date Range:** {venue_matches['date'].min()} to {venue_matches['date'].max()}
            """
            st.info(char_text)
        
        with col2:
            st.subheader("🎲 Match Results Distribution")
            
            # Win distribution
            fig_wins = px.pie(winner_dist.reset_index(), values='count', names='winner',
                             title="Winners at This Venue",
                             hole=0.3)
            st.plotly_chart(fig_wins, use_container_width=True)
        
        # Runs distribution
        st.subheader("📊 Runs per Match Distribution")
        
        runs_per_match = venue_deliveries.groupby('match_id')['total_runs'].sum().reset_index()
        runs_per_match.columns = ['match_id', 'runs']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(runs_per_match, x='runs', nbins=20,
                                   title="Runs Distribution at This Venue",
                                   labels={'runs': 'Total Runs', 'count': 'Number of Matches'})
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot for consistency
            fig_box = go.Figure(data=[go.Box(y=runs_per_match['runs'])])
            fig_box.update_layout(title="Runs Consistency (Box Plot)", height=400)
            st.plotly_chart(fig_box, use_container_width=True)

    # ==================== TEAM PERFORMANCE ====================
    with tab2:
        st.header(f"🏆 {selected_venue} - Team Performance")
        
        venue_matches = matches[matches['venue'] == selected_venue].copy()
        
        # Team stats at this venue
        team_stats = []
        all_teams = pd.concat([venue_matches['team1'], venue_matches['team2']]).unique()
        
        for team in all_teams:
            team_matches = venue_matches[(venue_matches['team1'] == team) | (venue_matches['team2'] == team)]
            wins = len(team_matches[team_matches['winner'] == team])
            total = len(team_matches)
            
            team_stats.append({
                'Team': team,
                'Matches': total,
                'Wins': wins,
                'Losses': total - wins,
                'Win %': (wins / total * 100) if total > 0 else 0
            })
        
        team_df = pd.DataFrame(team_stats).sort_values('Matches', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Team Matches at Venue")
            fig_matches = px.bar(team_df.head(15), x='Team', y='Matches',
                                title="Top Teams by Matches",
                                color='Matches',
                                color_continuous_scale='Blues')
            fig_matches.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_matches, use_container_width=True)
        
        with col2:
            st.subheader("🏆 Best Win Rate (Min 3 Matches)")
            best_teams = team_df[team_df['Matches'] >= 3].nlargest(10, 'Win %')
            
            fig_wr = px.bar(best_teams, x='Team', y='Win %',
                           title="Best Win % at Venue",
                           color='Win %',
                           color_continuous_scale='RdYlGn')
            fig_wr.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_wr, use_container_width=True)
        
        # Team details table
        st.subheader("📋 Team Performance Details")
        team_display = team_df[['Team', 'Matches', 'Wins', 'Losses', 'Win %']].copy()
        team_display['Win %'] = team_display['Win %'].round(2)
        st.dataframe(team_display, use_container_width=True)

    # ==================== BATTING TRENDS ====================
    with tab3:
        st.header(f"🏏 {selected_venue} - Batting Trends")
        
        venue_matches = matches[matches['venue'] == selected_venue]
        venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Overall Strike Rate Trend")
            
            # SR by season
            sr_by_season = []
            for season in venue_matches['season'].unique():
                season_matches = venue_matches[venue_matches['season'] == season]['match_id']
                season_del = venue_deliveries[venue_deliveries['match_id'].isin(season_matches)]
                
                total_runs = season_del['batsman_runs'].sum()
                total_balls = len(season_del)
                sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
                
                sr_by_season.append({
                    'Season': season,
                    'Strike Rate': sr
                })
            
            sr_df = pd.DataFrame(sr_by_season).sort_values('Season')
            
            fig_sr = px.line(sr_df, x='Season', y='Strike Rate',
                            title="Strike Rate Trend Over Seasons",
                            markers=True)
            st.plotly_chart(fig_sr, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Top Batsmen at Venue")
            top_batsmen = venue_deliveries.groupby('batter')['batsman_runs'].sum().nlargest(10).reset_index()
            top_batsmen.columns = ['Player', 'Runs']
            
            fig_bat = px.bar(top_batsmen, x='Player', y='Runs',
                            title="Top 10 Scorers at Venue",
                            color='Runs',
                            color_continuous_scale='Oranges')
            fig_bat.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig_bat, use_container_width=True)
        
        # Scoring pattern analysis
        st.subheader("📊 Scoring Patterns at Venue")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Runs by type
            run_types = {
                '0s': len(venue_deliveries[venue_deliveries['batsman_runs'] == 0]),
                '1s': len(venue_deliveries[venue_deliveries['batsman_runs'] == 1]),
                '2s': len(venue_deliveries[venue_deliveries['batsman_runs'] == 2]),
                '3s': len(venue_deliveries[venue_deliveries['batsman_runs'] == 3]),
                '4s': len(venue_deliveries[venue_deliveries['batsman_runs'] == 4]),
                '6s': len(venue_deliveries[venue_deliveries['batsman_runs'] == 6]),
            }
            
            fig_types = px.pie(values=list(run_types.values()), names=list(run_types.keys()),
                              title="Delivery Type Distribution")
            st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            # Boundary distribution
            fours = len(venue_deliveries[venue_deliveries['batsman_runs'] == 4])
            sixes = len(venue_deliveries[venue_deliveries['batsman_runs'] == 6])
            singles = len(venue_deliveries[venue_deliveries['batsman_runs'] == 1])
            
            boundary_text = f"""
            **Boundary Distribution**
            
            - **Fours:** {fours}
            - **Sixes:** {sixes}
            - **Singles:** {singles}
            - **4/6 Ratio:** {fours/sixes if sixes > 0 else "N/A":.2f}
            
            **Scoring Efficiency:**
            - Fours %: {(fours/len(venue_deliveries)*100):.1f}%
            - Sixes %: {(sixes/len(venue_deliveries)*100):.1f}%
            """
            st.info(boundary_text)

    # ==================== MATCH STATISTICS ====================
    with tab4:
        st.header(f"📈 {selected_venue} - Match Statistics")
        
        venue_matches = matches[matches['venue'] == selected_venue]
        venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎲 Total Statistics")
            stats_text = f"""
            **Overall Stats**
            
            - Total Matches: {len(venue_matches)}
            - Total Runs: {int(venue_deliveries['total_runs'].sum())}
            - Total Balls: {len(venue_deliveries)}
            - Total Wickets: {int(venue_deliveries['is_wicket'].sum())}
            - Avg Runs/Match: {(venue_deliveries['total_runs'].sum() / len(venue_matches)):.0f}
            """
            st.info(stats_text)
        
        with col2:
            st.subheader("🏏 Batting Stats")
            batting_text = f"""
            **Batting Metrics**
            
            - Total Batsmen: {venue_deliveries['batter'].nunique()}
            - Avg Balls/Match: {len(venue_deliveries) / len(venue_matches):.0f}
            - Avg Runs/Ball: {(venue_deliveries['batsman_runs'].sum() / len(venue_deliveries)):.3f}
            - Strike Rate: {(venue_deliveries['batsman_runs'].sum() / len(venue_deliveries) * 100):.2f}%
            """
            st.info(batting_text)
        
        with col3:
            st.subheader("🎯 Bowling Stats")
            bowling_text = f"""
            **Bowling Metrics**
            
            - Total Bowlers: {venue_deliveries['bowler'].nunique()}
            - Wickets/Match: {(venue_deliveries['is_wicket'].sum() / len(venue_matches)):.1f}
            - Economy Rate: {((venue_deliveries['total_runs'].sum() / (len(venue_deliveries) / 6))):.2f}
            - Avg Wickets: {int(venue_deliveries['is_wicket'].sum())}
            """
            st.info(bowling_text)
        
        # Match timeline
        st.subheader("📅 Matches Over Time")
        
        if 'date' in venue_matches.columns:
            venue_matches_sorted = venue_matches.sort_values('date')
            venue_matches_sorted['Cumulative Matches'] = range(1, len(venue_matches_sorted) + 1)
            
            fig_timeline = px.line(venue_matches_sorted, x='date', y='Cumulative Matches',
                                  title="Matches Hosted Over Time",
                                  markers=True)
            st.plotly_chart(fig_timeline, use_container_width=True)

    # ==================== PLAYER STATISTICS ====================
    with tab5:
        st.header(f"👑 {selected_venue} - Player Statistics")
        
        venue_matches = matches[matches['venue'] == selected_venue]
        venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🏏 Top 10 Batsmen")
            top_bat = venue_deliveries.groupby('batter')['batsman_runs'].sum().nlargest(10).reset_index()
            top_bat.columns = ['Player', 'Runs']
            st.dataframe(top_bat, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Top 10 Bowlers")
            top_bowl = venue_deliveries[venue_deliveries['is_wicket'] == 1].groupby('bowler').size().nlargest(10).reset_index(name='Wickets')
            st.dataframe(top_bowl, use_container_width=True)
        
        with col3:
            st.subheader("📊 Most Consistent")
            consistency = venue_deliveries.groupby('batter')['batsman_runs'].apply(
                lambda x: x.std() / x.mean() if x.mean() > 0 else 0
            ).nsmallest(10).reset_index()
            consistency.columns = ['Player', 'Consistency Score']
            st.dataframe(consistency, use_container_width=True)

    # ==================== KEY INSIGHTS ====================
    with tab6:
        st.header(f"🔍 {selected_venue} - Key Insights & Analysis")
        
        venue_matches = matches[matches['venue'] == selected_venue]
        venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Venue Characteristics")
            
            # Calculate characteristics
            avg_runs = venue_deliveries['total_runs'].sum() / len(venue_matches) if len(venue_matches) > 0 else 0
            league_avg = deliveries.groupby(deliveries['match_id'].map(matches.set_index('match_id')['venue'].to_dict())).apply(
                lambda x: x['total_runs'].sum()
            ).mean()
            
            batting_friendly = avg_runs > league_avg * 1.1
            
            insights = f"""
            **Venue Analysis:**
            
            - **Overall Score:** {avg_runs:.0f} runs/match
            - **League Average:** {league_avg:.0f} runs/match
            - **Pace:** {"⚡ Fast" if avg_runs > 160 else "⚖️ Neutral" if avg_runs > 130 else "🐢 Slow"}
            - **Batting:** {"🔥 Batsman Friendly" if batting_friendly else "🛡️ Bowler Friendly"}
            - **Wickets/Match:** {(venue_deliveries['is_wicket'].sum() / len(venue_matches)):.1f}
            - **Total Teams:** {pd.concat([venue_matches['team1'], venue_matches['team2']]).nunique()}
            """
            st.info(insights)
        
        with col2:
            st.subheader("🏆 Performance Summary")
            
            # Top performer
            top_team = pd.concat([venue_matches['team1'], venue_matches['team2']]).value_counts().idxmax()
            
            summary = f"""
            **Key Statistics:**
            
            - **Most Active Team:** {top_team}
            - **Total Unique Teams:** {pd.concat([venue_matches['team1'], venue_matches['team2']]).nunique()}
            - **Seasons Hosted:** {venue_matches['season'].nunique()}
            - **First Match:** {venue_matches['date'].min()}
            - **Latest Match:** {venue_matches['date'].max()}
            
            **Records:**
            - Highest Score: {int(venue_deliveries.groupby('match_id')['total_runs'].sum().max())} runs
            - Lowest Score: {int(venue_deliveries.groupby('match_id')['total_runs'].sum().min())} runs
            """
            st.success(summary)
        
        # Recommendations
        st.subheader("💡 Strategic Insights")
        
        avg_runs = venue_deliveries['total_runs'].sum() / len(venue_matches)
        avg_wickets = venue_deliveries['is_wicket'].sum() / len(venue_matches)
        
        rec_text = f"""
        **Venue-Specific Recommendations:**
        
        ✅ **For Batsmen:**
        - Expect {avg_runs:.0f} runs/match average
        - {"Go aggressive with more boundaries" if avg_runs > 150 else "Play cautiously and build innings"}
        - Focus on maintaining strike rate
        
        ✅ **For Bowlers:**
        - Wickets available: {avg_wickets:.1f}/match
        - {"Bowl attacking lengths" if avg_wickets < 6 else "Mix up bowling strategy"}
        - Economy rate critical at this venue
        
        ✅ **For Teams:**
        - {"Target 160+ for competitive score" if avg_runs > 140 else "Target 140+ for competitive score"}
        - {"Prioritize aggressive batting in powerplay" if avg_runs > 150 else "Build steady partnerships"}
        - Venue has hosted {len(venue_matches)} matches, suggesting {"hostile conditions" if avg_runs < 130 else "favorable conditions"}
        """
        st.info(rec_text)

# ==================== MULTI-VENUE COMPARISON ====================
elif analysis_mode == "🔄 Compare Venues":
    st.header("🔄 Multi-Venue Comparison")
    
    st.sidebar.header("🎯 Select Venues to Compare")
    selected_venues = st.sidebar.multiselect("Choose 2-5 Venues", all_venues, default=all_venues[:3])
    
    if len(selected_venues) < 2:
        st.warning("⚠️ Please select at least 2 venues to compare")
    else:
        # Prepare comparison data
        comparison_data = []
        for venue in selected_venues:
            venue_matches = matches[matches['venue'] == venue]
            venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
            
            total_matches = len(venue_matches)
            total_runs = venue_deliveries['total_runs'].sum()
            avg_runs = total_runs / total_matches if total_matches > 0 else 0
            wickets = venue_deliveries['is_wicket'].sum()
            avg_wickets = wickets / total_matches if total_matches > 0 else 0
            unique_teams = pd.concat([venue_matches['team1'], venue_matches['team2']]).nunique()
            sr = (venue_deliveries['batsman_runs'].sum() / len(venue_deliveries) * 100) if len(venue_deliveries) > 0 else 0
            
            comparison_data.append({
                'Venue': venue,
                'Matches': total_matches,
                'Total Runs': int(total_runs),
                'Avg Runs/Match': avg_runs,
                'Avg Wickets': avg_wickets,
                'Strike Rate': sr,
                'Unique Teams': unique_teams
            })
        
        comp_df = pd.DataFrame(comparison_data)
        
        # Comparison metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Venues Compared", len(selected_venues))
        with col2:
            st.metric("📊 Total Matches", int(comp_df['Matches'].sum()))
        with col3:
            st.metric("📈 Avg Runs (All)", f"{comp_df['Avg Runs/Match'].mean():.0f}")
        with col4:
            st.metric("🎯 Avg Wickets (All)", f"{comp_df['Avg Wickets'].mean():.1f}")
        
        # Comparison charts
        st.subheader("📊 Venue Comparison Charts")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_matches = px.bar(comp_df, x='Venue', y='Matches',
                               title="Total Matches per Venue",
                               color='Matches',
                               color_continuous_scale='Blues')
            st.plotly_chart(fig_matches, use_container_width=True)
        
        with col2:
            fig_runs = px.bar(comp_df, x='Venue', y='Avg Runs/Match',
                            title="Average Runs per Match",
                            color='Avg Runs/Match',
                            color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_runs, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sr = px.bar(comp_df, x='Venue', y='Strike Rate',
                           title="Overall Strike Rate",
                           color='Strike Rate',
                           color_continuous_scale='Oranges')
            st.plotly_chart(fig_sr, use_container_width=True)
        
        with col2:
            fig_wickets = px.bar(comp_df, x='Venue', y='Avg Wickets',
                               title="Average Wickets per Match",
                               color='Avg Wickets',
                               color_continuous_scale='Reds')
            st.plotly_chart(fig_wickets, use_container_width=True)
        
        # Comparison table
        st.subheader("📋 Detailed Comparison Table")
        comp_display = comp_df.copy()
        comp_display['Avg Runs/Match'] = comp_display['Avg Runs/Match'].round(0)
        comp_display['Avg Wickets'] = comp_display['Avg Wickets'].round(1)
        comp_display['Strike Rate'] = comp_display['Strike Rate'].round(2)
        st.dataframe(comp_display, use_container_width=True)
        
        # Insights
        st.subheader("💡 Comparative Insights")
        
        highest_runs_venue = comp_df.loc[comp_df['Avg Runs/Match'].idxmax(), 'Venue']
        lowest_runs_venue = comp_df.loc[comp_df['Avg Runs/Match'].idxmin(), 'Venue']
        highest_sr_venue = comp_df.loc[comp_df['Strike Rate'].idxmax(), 'Venue']
        
        insights = f"""
        **Key Findings:**
        
        - 🔥 **Highest Scoring:** {highest_runs_venue} ({comp_df.loc[comp_df['Venue'] == highest_runs_venue, 'Avg Runs/Match'].values[0]:.0f} runs/match)
        - 🛡️ **Lowest Scoring:** {lowest_runs_venue} ({comp_df.loc[comp_df['Venue'] == lowest_runs_venue, 'Avg Runs/Match'].values[0]:.0f} runs/match)
        - ⚡ **Highest Strike Rate:** {highest_sr_venue} ({comp_df.loc[comp_df['Venue'] == highest_sr_venue, 'Strike Rate'].values[0]:.1f}%)
        - 🏟️ **Most Active:** {comp_df.loc[comp_df['Matches'].idxmax(), 'Venue']} ({int(comp_df['Matches'].max())} matches)
        """
        st.info(insights)

# ==================== ALL VENUES OVERVIEW ====================
elif analysis_mode == "🌍 All Venues Overview":
    st.header("🌍 All Venues Overview - League-wide Analysis")
    
    # Get stats for all venues
    all_venue_data = []
    for venue in all_venues:
        venue_matches = matches[matches['venue'] == venue]
        venue_deliveries = deliveries[deliveries['match_id'].isin(venue_matches['match_id'])]
        
        total_matches = len(venue_matches)
        total_runs = venue_deliveries['total_runs'].sum()
        avg_runs = total_runs / total_matches if total_matches > 0 else 0
        wickets = venue_deliveries['is_wicket'].sum()
        avg_wickets = wickets / total_matches if total_matches > 0 else 0
        unique_teams = pd.concat([venue_matches['team1'], venue_matches['team2']]).nunique()
        sr = (venue_deliveries['batsman_runs'].sum() / len(venue_deliveries) * 100) if len(venue_deliveries) > 0 else 0
        
        all_venue_data.append({
            'Venue': venue,
            'Matches': total_matches,
            'Avg Runs': avg_runs,
            'Avg Wickets': avg_wickets,
            'Strike Rate': sr,
            'Unique Teams': unique_teams
        })
    
    all_venues_df = pd.DataFrame(all_venue_data).sort_values('Matches', ascending=False)
    
    # Overview metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🌍 Total Venues", len(all_venues))
    with col2:
        st.metric("🎯 Total Matches", int(all_venues_df['Matches'].sum()))
    with col3:
        st.metric("📈 League Avg Runs", f"{all_venues_df['Avg Runs'].mean():.0f}")
    with col4:
        st.metric("🏏 League Avg SR", f"{all_venues_df['Strike Rate'].mean():.1f}%")
    with col5:
        st.metric("🎯 League Avg Wickets", f"{all_venues_df['Avg Wickets'].mean():.1f}")
    
    # All venues charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 15 Venues by Matches")
        fig_all_matches = px.bar(all_venues_df.head(15), x='Venue', y='Matches',
                                title="Matches Hosted by Venue",
                                color='Matches',
                                color_continuous_scale='Blues')
        fig_all_matches.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_all_matches, use_container_width=True)
    
    with col2:
        st.subheader("🔥 Highest Scoring Venues")
        top_scoring = all_venues_df.nlargest(15, 'Avg Runs')
        fig_high_scoring = px.bar(top_scoring, x='Venue', y='Avg Runs',
                                 title="Highest Avg Runs/Match",
                                 color='Avg Runs',
                                 color_continuous_scale='RdYlGn')
        fig_high_scoring.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_high_scoring, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Highest Strike Rate Venues")
        high_sr = all_venues_df.nlargest(15, 'Strike Rate')
        fig_sr_all = px.bar(high_sr, x='Venue', y='Strike Rate',
                           title="Highest Strike Rate",
                           color='Strike Rate',
                           color_continuous_scale='Oranges')
        fig_sr_all.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_sr_all, use_container_width=True)
    
    with col2:
        st.subheader("🏟️ Most Bowler-Friendly (Avg Wickets)")
        high_wickets = all_venues_df.nlargest(15, 'Avg Wickets')
        fig_wickets_all = px.bar(high_wickets, x='Venue', y='Avg Wickets',
                                title="Most Wickets per Match",
                                color='Avg Wickets',
                                color_continuous_scale='Reds')
        fig_wickets_all.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_wickets_all, use_container_width=True)
    
    # Venue heatmap
    st.subheader("🔥 Venue Characteristics Heatmap")
    
    heatmap_data = all_venues_df[['Venue', 'Matches', 'Avg Runs', 'Strike Rate', 'Avg Wickets']].set_index('Venue')
    # Normalize for heatmap
    heatmap_data_norm = (heatmap_data - heatmap_data.mean()) / heatmap_data.std()
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data_norm.values,
        x=heatmap_data_norm.columns,
        y=heatmap_data_norm.index,
        colorscale='RdBu_r'
    ))
    fig_heatmap.update_layout(title="Venue Characteristics Heatmap (Normalized)", height=600)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Full table
    st.subheader("📋 Complete Venues Statistics")
    table_display = all_venues_df.copy()
    table_display['Avg Runs'] = table_display['Avg Runs'].round(0)
    table_display['Avg Wickets'] = table_display['Avg Wickets'].round(1)
    table_display['Strike Rate'] = table_display['Strike Rate'].round(2)
    st.dataframe(table_display, use_container_width=True)
    
    # Venue categories
    st.subheader("🏆 Venue Categories")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔥 High Scoring Venues")
        high_scoring_venues = all_venues_df[all_venues_df['Avg Runs'] > all_venues_df['Avg Runs'].quantile(0.75)]
        for idx, row in high_scoring_venues.head(5).iterrows():
            st.write(f"⭐ {row['Venue']}: {row['Avg Runs']:.0f} runs")
    
    with col2:
        st.markdown("### 🛡️ Bowler-Friendly Venues")
        bowler_venues = all_venues_df[all_venues_df['Avg Wickets'] > all_venues_df['Avg Wickets'].quantile(0.75)]
        for idx, row in bowler_venues.head(5).iterrows():
            st.write(f"⭐ {row['Venue']}: {row['Avg Wickets']:.1f} wickets")
    
    with col3:
        st.markdown("### ⚡ Most Active Venues")
        active_venues = all_venues_df.head(5)
        for idx, row in active_venues.iterrows():
            st.write(f"⭐ {row['Venue']}: {int(row['Matches'])} matches")
