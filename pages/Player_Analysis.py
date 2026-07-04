import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from utils import load_data

st.set_page_config(layout="wide")
st.title("👤 Player Analysis Dashboard")

matches, deliveries = load_data()

# Sidebar player selection
st.sidebar.header("🎛️ Player Selection")
all_batsmen = sorted(deliveries['batter'].unique())
selected_player = st.sidebar.selectbox("Select Player", all_batsmen)

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Profile", "📈 Career Stats", "🎯 Form Analysis", "📍 Venue Analysis", "🤝 Partnerships"])

# ==================== PLAYER PROFILE ====================
with tab1:
    st.header(f"👤 {selected_player} - Player Profile")
    
    # Get player stats
    player_deliveries = deliveries[deliveries['batter'] == selected_player]
    player_runs = player_deliveries['batsman_runs'].sum()
    player_balls = len(player_deliveries)
    player_dismissals = len(player_deliveries[player_deliveries['player_dismissed'] == selected_player])
    
    # Centuries and Half-centuries
    innings_runs = player_deliveries.groupby('match_id')['batsman_runs'].sum()
    centuries = len(innings_runs[innings_runs >= 100])
    half_centuries = len(innings_runs[(innings_runs >= 50) & (innings_runs < 100)])
    
    # Fours and Sixes
    fours = len(player_deliveries[player_deliveries['batsman_runs'] == 4])
    sixes = len(player_deliveries[player_deliveries['batsman_runs'] == 6])
    
    # Calculate stats
    avg = player_runs / player_dismissals if player_dismissals > 0 else 0
    sr = (player_runs / player_balls * 100) if player_balls > 0 else 0
    matches_played = player_deliveries['match_id'].nunique()
    
    # Display KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🏃 Matches", matches_played)
    with col2:
        st.metric("🏏 Total Runs", int(player_runs))
    with col3:
        st.metric("📊 Average", f"{avg:.2f}")
    with col4:
        st.metric("⚡ Strike Rate", f"{sr:.2f}%")
    with col5:
        st.metric("🎯 Status", "Active" if matches_played > 0 else "Inactive")
    
    # Second row KPI
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("💯 Centuries", centuries)
    with col2:
        st.metric("👑 Half-Centuries", half_centuries)
    with col3:
        st.metric("🔢 Fours", fours)
    with col4:
        st.metric("💥 Sixes", sixes)
    with col5:
        st.metric("📉 Dismissals", int(player_dismissals))
    
    # Player Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Career Snapshot")
        st.info(f"""
        **{selected_player}**
        - Total Runs: {int(player_runs)}
        - Total Balls Faced: {int(player_balls)}
        - Matches Played: {matches_played}
        - Dismissals: {int(player_dismissals)}
        - Innings (approx): {matches_played}
        - Average: {avg:.2f}
        - Strike Rate: {sr:.2f}%
        """)
    
    with col2:
        st.subheader("🎖️ Milestones")
        milestone_text = f"""
        - 🏆 Centuries: {centuries}
        - 🥈 Half-Centuries: {half_centuries}
        - 🔥 Boundary Count (4s): {fours}
        - 💣 Boundary Count (6s): {sixes}
        - 🎯 Best Performance: {int(innings_runs.max())} runs
        """
        st.success(milestone_text)

# ==================== CAREER STATS ====================
with tab2:
    st.header(f"📈 {selected_player} - Career Statistics")
    
    player_deliveries = deliveries[deliveries['batter'] == selected_player]
    
    # Performance trend over matches
    player_innings = player_deliveries.groupby('match_id')['batsman_runs'].sum().reset_index()
    player_innings['Cumulative Runs'] = player_innings['batsman_runs'].cumsum()
    player_innings = player_innings.sort_values('match_id').reset_index(drop=True)
    player_innings['Match Number'] = range(1, len(player_innings) + 1)
    
    # Line chart for cumulative runs
    st.subheader("📊 Cumulative Runs Over Matches")
    fig_cumulative = px.line(player_innings, x='Match Number', y='Cumulative Runs',
                             title=f"{selected_player} - Cumulative Runs Progression",
                             markers=True)
    fig_cumulative.update_layout(height=400)
    st.plotly_chart(fig_cumulative, use_container_width=True)
    
    # Distribution of innings
    st.subheader("🎯 Innings Runs Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_dist = px.histogram(player_innings, x='batsman_runs', nbins=20,
                               title=f"Runs Per Innings Distribution",
                               labels={'batsman_runs': 'Runs', 'count': 'Frequency'})
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Box plot for consistency
        fig_box = go.Figure(data=[go.Box(y=player_innings['batsman_runs'],
                                         name=selected_player)])
        fig_box.update_layout(title="Consistency Analysis (Box Plot)", height=400)
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Detailed innings table
    st.subheader("📋 Innings Details")
    innings_detail = player_innings[['Match Number', 'batsman_runs', 'Cumulative Runs']].copy()
    innings_detail.columns = ['Match #', 'Runs', 'Cumulative Runs']
    st.dataframe(innings_detail, use_container_width=True)

# ==================== FORM ANALYSIS ====================
with tab3:
    st.header(f"📉 {selected_player} - Form Analysis")
    
    player_deliveries = deliveries[deliveries['batter'] == selected_player]
    
    # Last 10 innings
    last_innings = player_deliveries.groupby('match_id')['batsman_runs'].sum().tail(10).reset_index()
    last_innings['Match Sequence'] = range(len(last_innings) - 9, len(last_innings) + 1)
    
    st.subheader("🔄 Last 10 Innings Form")
    col1, col2 = st.columns(2)
    
    with col1:
        # Recent form bar chart
        fig_recent = px.bar(last_innings, x='Match Sequence', y='batsman_runs',
                           title="Last 10 Innings Performance",
                           color='batsman_runs',
                           color_continuous_scale="RdYlGn")
        fig_recent.update_layout(height=400)
        st.plotly_chart(fig_recent, use_container_width=True)
    
    with col2:
        # Form statistics
        avg_last_10 = last_innings['batsman_runs'].mean()
        form_std = last_innings['batsman_runs'].std()
        best_recent = last_innings['batsman_runs'].max()
        worst_recent = last_innings['batsman_runs'].min()
        
        st.metric("📊 Avg (Last 10)", f"{avg_last_10:.2f}")
        st.metric("⚡ Best Recent", int(best_recent))
        st.metric("📉 Worst Recent", int(worst_recent))
        st.metric("📈 Consistency", f"{form_std:.2f}" if not pd.isna(form_std) else "N/A")
    
    # Form trend indicator
    st.subheader("📊 Form Trend")
    first_5_avg = player_deliveries.groupby('match_id')['batsman_runs'].sum().head(5).mean()
    last_5_avg = player_deliveries.groupby('match_id')['batsman_runs'].sum().tail(5).mean()
    trend = "📈 Improving" if last_5_avg > first_5_avg else "📉 Declining"
    
    st.info(f"""
    **Form Assessment:**
    - First 5 Average: {first_5_avg:.2f}
    - Last 5 Average: {last_5_avg:.2f}
    - Trend: {trend}
    """)

# ==================== VENUE ANALYSIS ====================
with tab4:
    st.header(f"📍 {selected_player} - Venue Analysis")
    
    player_deliveries = deliveries[deliveries['batter'] == selected_player]
    
    # Get venue from matches
    player_matches = matches[matches['match_id'].isin(player_deliveries['match_id'].unique())]
    
    # Merge venue info with player stats
    venue_stats = []
    for idx, row in player_matches.iterrows():
        venue = row['venue']
        match_id = row['match_id']
        match_runs = player_deliveries[player_deliveries['match_id'] == match_id]['batsman_runs'].sum()
        venue_stats.append({'venue': venue, 'match_id': match_id, 'runs': match_runs})
    
    venue_df = pd.DataFrame(venue_stats)
    venue_summary = venue_df.groupby('venue').agg({
        'runs': ['sum', 'mean', 'count']
    }).reset_index()
    venue_summary.columns = ['Venue', 'Total Runs', 'Average', 'Matches']
    venue_summary = venue_summary.sort_values('Total Runs', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏟️ Top Venues by Runs")
        fig_venue = px.bar(venue_summary.head(10), x='Venue', y='Total Runs',
                          title="Top 10 Venues - Total Runs",
                          color='Average')
        fig_venue.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_venue, use_container_width=True)
    
    with col2:
        st.subheader("📊 Venue Performance Scatter")
        fig_venue_scatter = px.scatter(venue_summary, x='Matches', y='Average',
                                      size='Total Runs', hover_name='Venue',
                                      title="Venue Performance (Avg vs Matches)",
                                      color='Average')
        fig_venue_scatter.update_layout(height=400)
        st.plotly_chart(fig_venue_scatter, use_container_width=True)
    
    # Venue table
    st.subheader("📋 Venue Statistics")
    venue_display = venue_summary[['Venue', 'Total Runs', 'Average', 'Matches']].copy()
    venue_display['Average'] = venue_display['Average'].round(2)
    st.dataframe(venue_display, use_container_width=True)

# ==================== PARTNERSHIPS ====================
with tab5:
    st.header(f"🤝 {selected_player} - Partnership Analysis")
    
    player_deliveries = deliveries[deliveries['batter'] == selected_player]
    
    # Get most common partners (non-striker)
    partnership_data = player_deliveries.groupby('non_striker')['batsman_runs'].agg(['sum', 'count']).reset_index()
    partnership_data.columns = ['Partner', 'Runs Together', 'Deliveries']
    partnership_data['Average Per Delivery'] = partnership_data['Runs Together'] / partnership_data['Deliveries']
    partnership_data = partnership_data.sort_values('Runs Together', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Partnerships")
        fig_partners = px.bar(partnership_data.head(10), x='Partner', y='Runs Together',
                             title="Top 10 Partnership Combinations",
                             color='Average Per Delivery')
        fig_partners.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_partners, use_container_width=True)
    
    with col2:
        st.subheader("📊 Partnership Efficiency")
        fig_eff = px.scatter(partnership_data[partnership_data['Deliveries'] >= 20],
                            x='Deliveries', y='Average Per Delivery',
                            size='Runs Together', hover_name='Partner',
                            title="Partnership Efficiency (Min 20 Balls)",
                            color='Runs Together')
        fig_eff.update_layout(height=400)
        st.plotly_chart(fig_eff, use_container_width=True)
    
    # Partnership table
    st.subheader("📋 Partnership Details")
    partnership_display = partnership_data[['Partner', 'Runs Together', 'Deliveries', 'Average Per Delivery']].copy()
    partnership_display['Average Per Delivery'] = partnership_display['Average Per Delivery'].round(3)
    st.dataframe(partnership_display, use_container_width=True)
    
    # Most productive partnerships
    st.subheader("🌟 Best Partnerships")
    best_partnerships = partnership_data[partnership_data['Deliveries'] >= 20].nlargest(5, 'Runs Together')
    if len(best_partnerships) > 0:
        for idx, row in best_partnerships.iterrows():
            st.success(f"🤝 **{selected_player}** & **{row['Partner']}** - {int(row['Runs Together'])} runs in {int(row['Deliveries'])} deliveries (Avg: {row['Average Per Delivery']:.2f})")

# ==================== COMPARISON WITH OTHERS ====================
st.divider()
st.header("📊 Comparisons & Rankings")

comparison_tab1, comparison_tab2 = st.tabs(["vs Top Players", "🏆 Leaderboards"])

with comparison_tab1:
    st.subheader("Compare with Other Players")
    
    # Select comparison player
    comparison_player = st.selectbox("Select Player to Compare", all_batsmen, key="compare_player")
    
    if comparison_player != selected_player:
        # Get stats for both players
        p1_runs = deliveries[deliveries['batter'] == selected_player]['batsman_runs'].sum()
        p1_balls = len(deliveries[deliveries['batter'] == selected_player])
        p1_avg = p1_runs / len(deliveries[(deliveries['batter'] == selected_player) & (deliveries['player_dismissed'] == selected_player)]) if len(deliveries[(deliveries['batter'] == selected_player) & (deliveries['player_dismissed'] == selected_player)]) > 0 else 0
        
        p2_runs = deliveries[deliveries['batter'] == comparison_player]['batsman_runs'].sum()
        p2_balls = len(deliveries[deliveries['batter'] == comparison_player])
        p2_avg = p2_runs / len(deliveries[(deliveries['batter'] == comparison_player) & (deliveries['player_dismissed'] == comparison_player)]) if len(deliveries[(deliveries['batter'] == comparison_player) & (deliveries['player_dismissed'] == comparison_player)]) > 0 else 0
        
        comparison_data = pd.DataFrame({
            selected_player: [p1_runs, p1_balls, p1_avg, (p1_runs/p1_balls*100) if p1_balls > 0 else 0],
            comparison_player: [p2_runs, p2_balls, p2_avg, (p2_runs/p2_balls*100) if p2_balls > 0 else 0]
        }, index=['Total Runs', 'Balls Faced', 'Average', 'Strike Rate'])
        
        # Comparison chart
        fig_comp = px.bar(comparison_data.reset_index(), x='index', 
                         y=[selected_player, comparison_player],
                         title=f"{selected_player} vs {comparison_player}",
                         barmode='group')
        fig_comp.update_layout(height=400)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Comparison table
        st.dataframe(comparison_data.round(2), use_container_width=True)
    else:
        st.warning("⚠️ Select a different player to compare")

with comparison_tab2:
    st.subheader("🏆 Global Leaderboards")
    
    # Overall statistics for all batsmen
    all_batsmen_stats = []
    for batter in deliveries['batter'].unique():
        batter_del = deliveries[deliveries['batter'] == batter]
        runs = batter_del['batsman_runs'].sum()
        balls = len(batter_del)
        dismissals = len(batter_del[batter_del['player_dismissed'] == batter])
        avg = runs / dismissals if dismissals > 0 else 0
        sr = (runs / balls * 100) if balls > 0 else 0
        all_batsmen_stats.append({
            'Player': batter,
            'Runs': runs,
            'Balls': balls,
            'Average': avg,
            'SR': sr
        })
    
    all_stats_df = pd.DataFrame(all_batsmen_stats)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💯 Most Runs")
        top_runs = all_stats_df.nlargest(5, 'Runs')[['Player', 'Runs']]
        st.dataframe(top_runs, use_container_width=True)
    
    with col2:
        st.markdown("### ⚡ Highest SR (Min 100 balls)")
        top_sr = all_stats_df[all_stats_df['Balls'] >= 100].nlargest(5, 'SR')[['Player', 'SR']]
        st.dataframe(top_sr, use_container_width=True)
    
    with col3:
        st.markdown("### 📊 Highest Average (Min 5 dismissals)")
        top_avg = all_stats_df[all_stats_df['Balls'] >= 50].nlargest(5, 'Average')[['Player', 'Average']]
        st.dataframe(top_avg, use_container_width=True)