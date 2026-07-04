import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import csv
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import load_data
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Performance Analysis Dashboard")

matches, deliveries = load_data()

# Sidebar filters
st.sidebar.header("🎛️ Filters")
tab1, tab2, tab3 = st.tabs(["🏏 Batting", "🎯 Bowling", "📊 Comparisons"])

# ==================== BATTING PERFORMANCE ====================
with tab1:
    st.header("🏏 Batting Performance")
    
    # Calculate batting stats
    batting_runs = deliveries.groupby('batter')['batsman_runs'].sum()
    batting_balls = deliveries.groupby('batter').size()
    batting_dismissals = deliveries[deliveries['player_dismissed'] == deliveries['batter']].groupby('batter').size()
    
    # Centuries and Half-centuries
    innings_runs = deliveries.groupby(['match_id', 'batter'])['batsman_runs'].sum()
    centuries = (innings_runs >= 100).groupby('batter').sum()
    half_centuries = ((innings_runs >= 50) & (innings_runs < 100)).groupby('batter').sum()
    
    batting_stats = pd.DataFrame({
        'Runs': batting_runs,
        'Balls Faced': batting_balls,
        'Dismissals': batting_dismissals,
        'Centuries': centuries,
        'Half-Centuries': half_centuries
    }).fillna(0)
    
    batting_stats['Average'] = batting_stats['Runs'] / batting_stats['Dismissals'].replace(0, 1)
    batting_stats['Strike Rate'] = (batting_stats['Runs'] / batting_stats['Balls Faced']) * 100
    batting_stats['Consistency'] = batting_stats.groupby(level=0).apply(lambda x: (batting_stats.loc[x.index, 'Runs'] / batting_stats.loc[x.index, 'Balls Faced']).std()).fillna(0)
    batting_stats = batting_stats.sort_values('Runs', ascending=False)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_balls = st.slider("Minimum Balls Faced", 50, 500, 100)
    with col2:
        min_avg = st.slider("Minimum Average", 0.0, 100.0, 20.0)
    with col3:
        top_n = st.slider("Top N Players", 5, 50, 15)
    
    batting_filtered = batting_stats[
        (batting_stats['Balls Faced'] >= min_balls) & 
        (batting_stats['Average'] >= min_avg)
    ].head(top_n)
    
    # KPI Cards
    st.subheader("⭐ Top Batsmen Highlights")
    if len(batting_filtered) > 0:
        top_batter = batting_filtered.iloc[0]
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🏆 Most Runs", int(top_batter['Runs']))
        with col2:
            st.metric("🎯 Best Average", f"{top_batter['Average']:.2f}")
        with col3:
            st.metric("⚡ Highest SR", f"{top_batter['Strike Rate']:.2f}%")
        with col4:
            st.metric("💯 Centuries", int(top_batter['Centuries']))
        with col5:
            st.metric("👑 Half-Centuries", int(top_batter['Half-Centuries']))
    
    # Visualizations
    st.subheader("📈 Batting Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_runs = px.bar(batting_filtered.reset_index(), x='batter', y='Runs', 
                         title="Top Batsmen by Runs", color='Strike Rate',
                         color_continuous_scale="Viridis")
        fig_runs.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_runs, use_container_width=True)
    
    with col2:
        fig_avg = px.scatter(batting_filtered.reset_index(), x='Balls Faced', y='Average',
                            size='Runs', hover_name='batter', title="Average vs Balls Faced",
                            color='Strike Rate', color_continuous_scale="Plasma")
        fig_avg.update_layout(height=400)
        st.plotly_chart(fig_avg, use_container_width=True)
    
    # Data Table
    st.subheader("📋 Detailed Batting Stats")
    display_cols = ['Runs', 'Balls Faced', 'Dismissals', 'Average', 'Strike Rate', 'Centuries', 'Half-Centuries']
    batting_display = batting_filtered[display_cols].copy()
    batting_display = batting_display.round(2)
    st.dataframe(batting_display, use_container_width=True)
    
    # Export functionality
    csv_buffer = StringIO()
    batting_display.to_csv(csv_buffer)
    csv_bytes = csv_buffer.getvalue()
    
    st.download_button(
        label="📥 Download Batting Stats (CSV)",
        data=csv_bytes,
        file_name="batting_performance.csv",
        mime="text/csv"
    )
    
    # Expandable detailed insights
    with st.expander("📊 Detailed Player Insights"):
        selected_batter = st.selectbox("Select Batter for Details", batting_filtered.index, key="batter_select")
        if selected_batter:
            player_data = batting_stats.loc[selected_batter]
            st.write(f"**{selected_batter}**")
            st.metric("Career Runs", int(player_data['Runs']))
            st.metric("Career Average", f"{player_data['Average']:.2f}")
            st.metric("Career Strike Rate", f"{player_data['Strike Rate']:.2f}%")
            st.metric("Total Centuries", int(player_data['Centuries']))
            st.metric("Total Half-Centuries", int(player_data['Half-Centuries']))

# ==================== BOWLING PERFORMANCE ====================
with tab2:
    st.header("🎯 Bowling Performance")
    
    # Calculate bowling stats
    bowling_wickets = deliveries[deliveries['is_wicket'] == 1].groupby('bowler').size()
    bowling_runs = deliveries.groupby('bowler')['total_runs'].sum()
    bowling_balls = deliveries.groupby('bowler').size()
    
    # Calculate best figures (highest wickets in a match)
    match_bowling = deliveries[deliveries['is_wicket'] == 1].groupby(['match_id', 'bowler']).size()
    best_figures = match_bowling.groupby('bowler').max()
    
    bowling_stats = pd.DataFrame({
        'Wickets': bowling_wickets,
        'Runs Conceded': bowling_runs,
        'Balls Bowled': bowling_balls,
        'Best Figures': best_figures
    }).fillna(0)
    
    bowling_stats['Average'] = bowling_stats['Runs Conceded'] / bowling_stats['Wickets'].replace(0, 1)
    bowling_stats['Economy'] = (bowling_stats['Runs Conceded'] / (bowling_stats['Balls Bowled'] / 6)).fillna(0)
    bowling_stats = bowling_stats.sort_values('Wickets', ascending=False)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_balls_bowl = st.slider("Minimum Balls Bowled", 50, 500, 100, key="bowl_balls")
    with col2:
        min_economy = st.slider("Maximum Economy Rate", 4.0, 15.0, 10.0)
    with col3:
        top_n_bowl = st.slider("Top N Bowlers", 5, 50, 15, key="top_bowlers")
    
    bowling_filtered = bowling_stats[
        (bowling_stats['Balls Bowled'] >= min_balls_bowl) & 
        (bowling_stats['Economy'] <= min_economy)
    ].head(top_n_bowl)
    
    # KPI Cards
    st.subheader("⭐ Top Bowlers Highlights")
    if len(bowling_filtered) > 0:
        top_bowler = bowling_filtered.iloc[0]
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🏆 Most Wickets", int(top_bowler['Wickets']))
        with col2:
            st.metric("💨 Best Economy", f"{top_bowler['Economy']:.2f}")
        with col3:
            st.metric("📊 Best Figures", int(top_bowler['Best Figures']))
        with col4:
            st.metric("🎯 Bowling Average", f"{top_bowler['Average']:.2f}")
        with col5:
            st.metric("📈 Overs Bowled", int(top_bowler['Balls Bowled'] / 6))
    
    # Visualizations
    st.subheader("📈 Bowling Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_wickets = px.bar(bowling_filtered.reset_index(), x='bowler', y='Wickets',
                            title="Top Bowlers by Wickets", color='Economy',
                            color_continuous_scale="RdYlGn_r")
        fig_wickets.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_wickets, use_container_width=True)
    
    with col2:
        fig_eco = px.scatter(bowling_filtered.reset_index(), x='Balls Bowled', y='Economy',
                            size='Wickets', hover_name='bowler', title="Economy vs Balls Bowled",
                            color='Average', color_continuous_scale="Turbo")
        fig_eco.update_layout(height=400)
        st.plotly_chart(fig_eco, use_container_width=True)
    
    # Data Table
    st.subheader("📋 Detailed Bowling Stats")
    display_cols_bowl = ['Wickets', 'Runs Conceded', 'Balls Bowled', 'Average', 'Economy', 'Best Figures']
    bowling_display = bowling_filtered[display_cols_bowl].copy()
    bowling_display = bowling_display.round(2)
    st.dataframe(bowling_display, use_container_width=True)
    
    # Export functionality
    csv_buffer_bowl = StringIO()
    bowling_display.to_csv(csv_buffer_bowl)
    csv_bytes_bowl = csv_buffer_bowl.getvalue()
    
    st.download_button(
        label="📥 Download Bowling Stats (CSV)",
        data=csv_bytes_bowl,
        file_name="bowling_performance.csv",
        mime="text/csv",
        key="download_bowling"
    )
    
    # Expandable detailed insights
    with st.expander("📊 Detailed Bowler Insights"):
        selected_bowler = st.selectbox("Select Bowler for Details", bowling_filtered.index, key="bowler_select")
        if selected_bowler:
            player_data_bowl = bowling_stats.loc[selected_bowler]
            st.write(f"**{selected_bowler}**")
            st.metric("Career Wickets", int(player_data_bowl['Wickets']))
            st.metric("Career Economy", f"{player_data_bowl['Economy']:.2f}")
            st.metric("Career Average", f"{player_data_bowl['Average']:.2f}")
            st.metric("Best Match Figures", int(player_data_bowl['Best Figures']))
            st.metric("Total Overs", int(player_data_bowl['Balls Bowled'] / 6))

# ==================== PLAYER COMPARISONS ====================
with tab3:
    st.header("👥 Player Comparisons")
    
    # Prepare combined data
    all_stats = pd.DataFrame()
    
    # Add batsmen stats
    for batter in batting_stats.index:
        row_data = batting_stats.loc[batter].to_dict()
        row_data['Player'] = batter
        row_data['Type'] = 'Batter'
        all_stats = pd.concat([all_stats, pd.DataFrame([row_data])], ignore_index=True)
    
    # Compare two players
    st.subheader("🔄 Head-to-Head Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        player1 = st.selectbox("Select First Player", batting_stats.index, key="player1")
    with col2:
        player2 = st.selectbox("Select Second Player", batting_stats.index, key="player2")
    
    if player1 and player2:
        comp_data = pd.DataFrame({
            player1: batting_stats.loc[player1],
            player2: batting_stats.loc[player2]
        })
        
        # Create comparison visualization
        metrics_to_compare = ['Runs', 'Average', 'Strike Rate', 'Centuries', 'Half-Centuries']
        comp_data_filtered = comp_data.loc[metrics_to_compare]
        
        fig_comp = go.Figure(data=[
            go.Bar(name=player1, x=metrics_to_compare, y=comp_data_filtered[player1]),
            go.Bar(name=player2, x=metrics_to_compare, y=comp_data_filtered[player2])
        ])
        fig_comp.update_layout(title="Player Comparison", barmode='group', height=400)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Detailed comparison table
        st.subheader("📊 Detailed Comparison")
        st.dataframe(comp_data_filtered.round(2), use_container_width=True)
    
    # Best performers across categories
    st.subheader("🏆 Best Performers")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💯 Most Runs")
        best_runs = batting_stats.nlargest(5, 'Runs')[['Runs']].round(0)
        st.dataframe(best_runs, use_container_width=True)
    
    with col2:
        st.markdown("### ⚡ Highest Strike Rate")
        best_sr = batting_stats[batting_stats['Balls Faced'] >= 100].nlargest(5, 'Strike Rate')[['Strike Rate']].round(2)
        st.dataframe(best_sr, use_container_width=True)
    
    with col3:
        st.markdown("### 🎯 Best Average")
        best_avg = batting_stats[batting_stats['Dismissals'] >= 5].nlargest(5, 'Average')[['Average']].round(2)
        st.dataframe(best_avg, use_container_width=True)