import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Profile", "📈 Career Stats", "🎯 Form Analysis", "📍 Venue Analysis", "🤝 Partnerships", "🔍 Player Profile"])

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
    player_matches = matches[matches['id'].isin(player_deliveries['match_id'].unique())]
    
    # Merge venue info with player stats
    venue_stats = []
    for idx, row in player_matches.iterrows():
        venue = row['venue']
        match_id = row['id']
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

# ==================== DETAILED PLAYER PROFILE ANALYSIS ====================
with tab6:
    st.header(f"🔍 {selected_player} - Detailed Player Profile")
    
    player_deliveries = deliveries[deliveries['batter'] == selected_player]
    
    # ===== PLAYER ARCHETYPE CLASSIFICATION =====
    st.subheader("🎭 Player Archetype Classification")
    
    # Build comprehensive player stats dictionary for all players
    all_player_stats = {}
    for batter in deliveries['batter'].unique():
        batter_del = deliveries[deliveries['batter'] == batter]
        b_runs = batter_del['batsman_runs'].sum()
        b_balls = len(batter_del)
        b_dismissals = len(batter_del[batter_del['player_dismissed'] == batter])
        b_avg = b_runs / b_dismissals if b_dismissals > 0 else 0
        b_sr = (b_runs / b_balls * 100) if b_balls > 0 else 0
        b_matches = batter_del['match_id'].nunique()
        
        # Get first match and batting position in that match
        first_match = batter_del['match_id'].min()
        first_match_batters = deliveries[deliveries['match_id'] == first_match]['batter'].unique()
        batting_order = list(first_match_batters).index(batter) + 1 if batter in first_match_batters else 0
        
        all_player_stats[batter] = {
            'runs': b_runs,
            'balls': b_balls,
            'average': b_avg,
            'sr': b_sr,
            'matches': b_matches,
            'batting_order': batting_order
        }
    
    player_stats = all_player_stats[selected_player]
    p_runs = player_stats['runs']
    p_balls = player_stats['balls']
    p_avg = player_stats['average']
    p_sr = player_stats['sr']
    p_matches = player_stats['matches']
    
    # Classify player archetype
    def classify_player_type(stats):
        """Classify player into different archetypes"""
        avg_sr = np.mean([p['sr'] for p in all_player_stats.values()])
        avg_avg = np.mean([p['average'] for p in all_player_stats.values()])
        
        sr = stats['sr']
        avg = stats['average']
        
        if sr > avg_sr and avg > avg_avg:
            return "🔥 Explosive All-rounder", "High strike rate & average - Best of both worlds"
        elif sr > avg_sr and avg <= avg_avg:
            return "⚡ Aggressive Hitter", "High strike rate but lower average - Explosive but risky"
        elif sr <= avg_sr and avg > avg_avg:
            return "🛡️ Anchor/Accumulator", "Reliable average but lower SR - Builds innings steadily"
        elif sr > 100 and avg > 25:
            return "💥 Dynamic Striker", "Balanced approach - Aggressive when required"
        else:
            return "🐢 Steady Consolidator", "Defensive approach - Focuses on stability"
    
    player_archetype, archetype_desc = classify_player_type(player_stats)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.success(f"**Archetype:**\n{player_archetype}")
    with col2:
        st.info(f"**Style:**\n{archetype_desc}")
    with col3:
        st.metric("🎯 Career Span", f"{p_matches} matches")
    with col4:
        st.metric("📊 Career SR", f"{p_sr:.1f}%")
    
    # ===== COMPARE WITH SIMILAR PLAYERS =====
    st.subheader("🤝 Similar Player Types Analysis")
    
    # Find similar players based on archetype
    similar_players = []
    for player, stats in all_player_stats.items():
        if player != selected_player and stats['matches'] >= 3:  # Min 3 matches
            similar_type, _ = classify_player_type(stats)
            if similar_type == player_archetype:
                similar_players.append((player, stats))
    
    if similar_players:
        similar_df = pd.DataFrame([
            {
                'Player': p[0],
                'Runs': int(p[1]['runs']),
                'Avg': round(p[1]['average'], 2),
                'SR': round(p[1]['sr'], 2),
                'Matches': int(p[1]['matches'])
            }
            for p in similar_players
        ]).sort_values('Runs', ascending=False)
        
        st.write(f"**Players with {player_archetype} archetype:**")
        st.dataframe(similar_df, use_container_width=True)
        
        # Ranking within archetype
        similar_df_sorted = similar_df.sort_values('Runs', ascending=False)
        player_rank = list(similar_df_sorted['Player']).index(selected_player) + 1 if selected_player in similar_df_sorted['Player'].values else 0
        
        if player_rank > 0:
            st.info(f"🏆 **Ranking among {player_archetype[4:]} players:** #{player_rank} out of {len(similar_df_sorted)}")
    
    # ===== PLAYING STYLE ANALYSIS =====
    st.subheader("🎯 Playing Style Deep Dive")
    
    # Determine playing style
    if p_sr > 130:
        playing_style = "🔥 Aggressive - Plays shots freely, high strike rate"
    elif p_sr > 110:
        playing_style = "⚡ Dynamic - Balanced aggressive-defensive approach"
    elif p_sr > 90:
        playing_style = "🛡️ Composed - Steady accumulator with selective attacking"
    else:
        playing_style = "🐢 Defensive - Plays for stability, accumulates runs slowly"
    
    # Consistency metric
    innings_runs = player_deliveries.groupby('match_id')['batsman_runs'].sum()
    consistency_score = (100 - (innings_runs.std() / innings_runs.mean() * 100)) if innings_runs.mean() > 0 else 0
    consistency_score = max(0, min(100, consistency_score))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"""
        **Playing Style**
        {playing_style}
        """)
    with col2:
        st.metric("🎯 Consistency Score", f"{consistency_score:.1f}%")
    with col3:
        st.metric("⚡ Aggression Index", f"{p_sr:.1f}")
    with col4:
        st.metric("🎪 Reliability Index", f"{p_avg:.2f}")
    
    # ===== DISMISSAL ANALYSIS =====
    st.subheader("📉 Dismissal Analysis")
    
    dismissal_modes = player_deliveries[player_deliveries['player_dismissed'] == selected_player]['dismissal_kind'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if len(dismissal_modes) > 0:
            fig_dismissal = px.pie(dismissal_modes.reset_index(), values='count', names='dismissal_kind',
                                  title="Dismissal Modes Distribution")
            st.plotly_chart(fig_dismissal, use_container_width=True)
    
    with col2:
        if len(dismissal_modes) > 0:
            dismissal_text = "**Dismissal Tendencies:**\n"
            for mode, count in dismissal_modes.items():
                pct = (count / dismissal_modes.sum()) * 100
                dismissal_text += f"- {mode}: {int(count)} times ({pct:.1f}%)\n"
            st.info(dismissal_text)
        
        # Most common dismisser
        st.subheader("👹 Most Common Dismissers")
        dismissers = player_deliveries[player_deliveries['player_dismissed'] == selected_player]['bowler'].value_counts().head(5)
        if len(dismissers) > 0:
            for bowler, count in dismissers.items():
                st.write(f"🎯 **{bowler}** - {int(count)} dismissals")
    
    # ===== SCORING PATTERNS =====
    st.subheader("📊 Scoring Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Runs by run type
        run_types = {
            '0s': len(player_deliveries[player_deliveries['batsman_runs'] == 0]),
            '1s': len(player_deliveries[player_deliveries['batsman_runs'] == 1]),
            '2s': len(player_deliveries[player_deliveries['batsman_runs'] == 2]),
            '3s': len(player_deliveries[player_deliveries['batsman_runs'] == 3]),
            '4s': len(player_deliveries[player_deliveries['batsman_runs'] == 4]),
            '6s': len(player_deliveries[player_deliveries['batsman_runs'] == 6]),
        }
        run_types_df = pd.DataFrame(list(run_types.items()), columns=['Run Type', 'Count'])
        
        fig_runs_type = px.bar(run_types_df, x='Run Type', y='Count',
                              title="Deliveries by Run Type",
                              color='Count', color_continuous_scale='Blues')
        st.plotly_chart(fig_runs_type, use_container_width=True)
    
    with col2:
        # Percentage of runs from different sources
        total_runs = p_runs
        runs_from_1s = len(player_deliveries[player_deliveries['batsman_runs'] == 1]) * 1
        runs_from_2s = len(player_deliveries[player_deliveries['batsman_runs'] == 2]) * 2
        runs_from_4s = len(player_deliveries[player_deliveries['batsman_runs'] == 4]) * 4
        runs_from_6s = len(player_deliveries[player_deliveries['batsman_runs'] == 6]) * 6
        
        runs_sources = {
            '1s': runs_from_1s,
            '2s': runs_from_2s,
            '4s': runs_from_4s,
            '6s': runs_from_6s,
        }
        
        if sum(runs_sources.values()) > 0:
            fig_runs_value = px.pie(values=list(runs_sources.values()), names=list(runs_sources.keys()),
                                   title="Total Runs by Source",
                                   hole=0.3)
            st.plotly_chart(fig_runs_value, use_container_width=True)
    
    # ===== PHASE-WISE PERFORMANCE =====
    st.subheader("🔄 Phase-wise Performance (Powerplay, Middle, Death)")
    
    def get_phase(over_number):
        """Classify delivery phase"""
        if over_number <= 6:
            return "Powerplay (1-6)"
        elif over_number <= 16:
            return "Middle Overs (7-16)"
        else:
            return "Death Overs (17-20)"
    
    player_deliveries['Phase'] = player_deliveries['over'].apply(get_phase)
    phase_stats = player_deliveries.groupby('Phase').agg({
        'batsman_runs': ['sum', 'count', 'mean']
    }).reset_index()
    phase_stats.columns = ['Phase', 'Runs', 'Balls', 'Avg per Ball']
    phase_stats['Strike Rate'] = (phase_stats['Runs'] / phase_stats['Balls'] * 100).round(2)
    phase_stats = phase_stats[['Phase', 'Runs', 'Balls', 'Strike Rate']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_phase = px.bar(phase_stats, x='Phase', y='Runs',
                          title="Runs Scored in Different Phases",
                          color='Strike Rate', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_phase, use_container_width=True)
    
    with col2:
        fig_phase_sr = px.bar(phase_stats, x='Phase', y='Strike Rate',
                             title="Strike Rate in Different Phases",
                             color='Strike Rate', color_continuous_scale='Viridis')
        st.plotly_chart(fig_phase_sr, use_container_width=True)
    
    st.dataframe(phase_stats.round(2), use_container_width=True)
    
    # ===== PERFORMANCE TIMELINE =====
    st.subheader("📅 Performance Timeline")
    
    # Get matches and sort by date
    player_match_ids = player_deliveries['match_id'].unique()
    player_matches = matches[matches['id'].isin(player_match_ids)][['id', 'date']].rename(columns={'id': 'match_id'}).drop_duplicates()
    player_matches = player_matches.sort_values('date')
    
    # Calculate runs per match
    runs_per_match = player_deliveries.groupby('match_id')['batsman_runs'].sum().reset_index()
    runs_per_match = runs_per_match.merge(player_matches, on='match_id')
    runs_per_match['Cumulative'] = runs_per_match['batsman_runs'].cumsum()
    runs_per_match = runs_per_match.sort_values('date')
    
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=runs_per_match['date'], y=runs_per_match['batsman_runs'],
        mode='markers+lines', name='Runs per Match',
        marker=dict(size=8, color=runs_per_match['batsman_runs'], 
                   colorscale='Viridis', showscale=True)
    ))
    fig_timeline.update_layout(title="Performance Timeline", height=400)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # ===== PLAYER RATING CARD =====
    st.subheader("⭐ Overall Player Rating")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate ratings
    run_rating = min(100, (p_runs / 200) * 100)  # 200 runs = 100 rating
    avg_rating = min(100, (p_avg / 50) * 100)  # 50 average = 100 rating
    sr_rating = min(100, (p_sr / 140) * 100)  # 140 SR = 100 rating
    consistency_rating = consistency_score
    
    overall_rating = (run_rating + avg_rating + sr_rating + consistency_rating) / 4
    
    with col1:
        st.metric("📊 Run Rating", f"{run_rating:.1f}%")
    with col2:
        st.metric("📈 Average Rating", f"{avg_rating:.1f}%")
    with col3:
        st.metric("⚡ Strike Rate Rating", f"{sr_rating:.1f}%")
    with col4:
        st.metric("🎯 Consistency Rating", f"{consistency_rating:.1f}%")
    with col5:
        st.metric("⭐ Overall Rating", f"{overall_rating:.1f}%")
    
    # ===== PLAYER TYPE RADAR CHART =====
    st.subheader("🎯 Player Profile Radar Chart")
    
    # Normalize metrics to 0-100 scale for radar chart
    run_norm = min(100, (p_runs / 200) * 100)
    avg_norm = min(100, (p_avg / 50) * 100)
    sr_norm = min(100, (p_sr / 140) * 100)
    cons_norm = consistency_score
    
    # Calculate dominant shots efficiency
    fours_count = len(player_deliveries[player_deliveries['batsman_runs'] == 4])
    sixes_count = len(player_deliveries[player_deliveries['batsman_runs'] == 6])
    boundary_norm = min(100, ((fours_count + sixes_count * 1.5) / (p_balls * 0.3)) * 100)
    
    # Create radar chart
    categories = ['Total Runs', 'Average', 'Strike Rate', 'Consistency', 'Boundary Hitting']
    values = [run_norm, avg_norm, sr_norm, cons_norm, boundary_norm]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=selected_player
    ))
    fig_radar.update_layout(
        title=f"{selected_player} - Player Profile Radar",
        height=500,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # ===== PLAYER TYPE MATRIX =====
    st.subheader("📊 All Players Type Matrix")
    
    # Create matrix of all players
    matrix_data = []
    for player, stats in all_player_stats.items():
        if stats['matches'] >= 2:  # Only players with 2+ matches
            matrix_data.append({
                'Player': player,
                'Average': stats['average'],
                'Strike Rate': stats['sr'],
                'Runs': stats['runs'],
                'Matches': stats['matches']
            })
    
    matrix_df = pd.DataFrame(matrix_data)
    
    # Create scatter plot showing all player types
    fig_matrix = px.scatter(matrix_df, x='Strike Rate', y='Average',
                           size='Runs', hover_name='Player',
                           title="Player Type Matrix - Average vs Strike Rate",
                           color='Runs', color_continuous_scale='Viridis',
                           labels={'Strike Rate': 'Strike Rate (%)', 'Average': 'Batting Average'})
    
    # Highlight selected player
    selected_player_data = matrix_df[matrix_df['Player'] == selected_player]
    if len(selected_player_data) > 0:
        fig_matrix.add_scatter(x=selected_player_data['Strike Rate'], 
                              y=selected_player_data['Average'],
                              mode='markers',
                              marker=dict(size=15, color='red', symbol='star'),
                              name=f'{selected_player} (Selected)',
                              hovertext=selected_player)
    
    # Add quadrant lines for player type classification
    fig_matrix.add_vline(x=np.mean(matrix_df['Strike Rate']), line_dash="dash", line_color="gray", opacity=0.5)
    fig_matrix.add_hline(y=np.mean(matrix_df['Average']), line_dash="dash", line_color="gray", opacity=0.5)
    
    fig_matrix.update_layout(height=500)
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # ===== PLAYER ARCHETYPE INSIGHTS =====
    st.subheader("💡 Archetype Insights & Recommendations")
    
    insight_text = f"""
    **Player Type: {player_archetype}**
    
    **Profile Summary:**
    {archetype_desc}
    
    **Key Strengths:**
    """
    
    if "Explosive" in player_archetype:
        insight_text += """
    - Combines aggression with reliability
    - Consistently high scorer across conditions
    - Valuable in pressure situations
    """
    elif "Aggressive" in player_archetype:
        insight_text += """
    - Explosive batting ability
    - Capable of quick runs
    - Best used in specific match situations
    """
    elif "Anchor" in player_archetype or "Accumulator" in player_archetype:
        insight_text += """
    - Builds stable innings foundation
    - Lower dismissal rate
    - Excellent for partnership building
    """
    else:
        insight_text += """
    - Brings stability to innings
    - Lower risk approach
    - Good team player
    """
    
    insight_text += f"""
    
    **Match Impact:**
    - Consistency Score: {consistency_score:.1f}% (Higher is better)
    - Aggression Index: {p_sr:.1f}% (League avg: {np.mean(matrix_df['Strike Rate']):.1f}%)
    - Reliability Index: {p_avg:.2f} (League avg: {np.mean(matrix_df['Average']):.2f})
    
    **Strengths in Different Phases:**
    - Powerplay Specialist: {'✅ Yes' if len(phase_stats[phase_stats['Phase'] == 'Powerplay (1-6)']) > 0 and phase_stats[phase_stats['Phase'] == 'Powerplay (1-6)']['Strike Rate'].values[0] > 120 else '❌ No'}
    - Middle Overs Anchor: {'✅ Yes' if len(phase_stats[phase_stats['Phase'] == 'Middle Overs (7-16)']) > 0 and phase_stats[phase_stats['Phase'] == 'Middle Overs (7-16)']['Strike Rate'].values[0] > 100 else '❌ No'}
    - Finisher: {'✅ Yes' if len(phase_stats[phase_stats['Phase'] == 'Death Overs (17-20)']) > 0 and phase_stats[phase_stats['Phase'] == 'Death Overs (17-20)']['Strike Rate'].values[0] > 130 else '❌ No'}
    """
    
    st.info(insight_text)

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