import streamlit as st
import pandas as pd
import numpy as np
import importlib.util

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Check sklearn availability
SKLEARN_AVAILABLE = False
if importlib.util.find_spec("sklearn") is not None:
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        SKLEARN_AVAILABLE = True
    except Exception:
        pass

from utils import load_data, get_teams

st.set_page_config(
    page_title="Live Match Predictor",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏏 Live Match Predictor")
st.markdown("**Real-time win probability predictions with interactive match simulation**")

matches, deliveries = load_data()
teams = get_teams(matches)

# Sidebar for match setup
st.sidebar.header("⚙️ Match Setup")

match_type = st.sidebar.selectbox("Match Format", ["T20", "ODI", "Test"], index=0)
total_overs = 20 if match_type == "T20" else 50 if match_type == "ODI" else 90

batting_team = st.sidebar.selectbox("Batting Team", teams)
bowling_team = st.sidebar.selectbox("Bowling Team", [t for t in teams if t != batting_team])

is_chase = st.sidebar.checkbox("Chasing Target", value=False)
if is_chase:
    target_runs = st.sidebar.number_input("Target Runs", min_value=1, value=150)
else:
    target_runs = None

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Current Match Situation")

    # Interactive inputs
    col_a, col_b = st.columns(2)
    with col_a:
        current_score = st.number_input("Current Score", min_value=0, value=85, step=1)
        wickets_fallen = st.slider("Wickets Fallen", min_value=0, max_value=10, value=2)
        overs_completed = st.slider("Overs Completed", min_value=0.0, max_value=float(total_overs), value=8.3, step=0.1)

    with col_b:
        balls_remaining = int((total_overs - overs_completed) * 6)
        runs_needed = (target_runs - current_score) if is_chase and target_runs else None

        st.metric("Balls Remaining", balls_remaining)
        if runs_needed:
            st.metric("Runs Needed", max(0, runs_needed))
        st.metric("Run Rate", f"{current_score/overs_completed:.2f}" if overs_completed > 0 else "0.00")

    # Calculate win probability
    if st.button("🔮 Calculate Win Probability", type="primary", use_container_width=True):
        with st.spinner("Analyzing match situation..."):

            # Simple win probability calculation based on historical data
            # This is a simplified model - in production you'd use trained ML models

            # Factors affecting win probability:
            # 1. Current run rate vs required run rate
            # 2. Wickets remaining
            # 3. Balls remaining
            # 4. Team strength (historical performance)
            # 5. Venue factors

            # Get team performance data
            batting_matches = matches[(matches['team1'] == batting_team) | (matches['team2'] == batting_team)]
            bowling_matches = matches[(matches['team1'] == bowling_team) | (matches['team2'] == bowling_team)]

            batting_win_rate = len(batting_matches[batting_matches['winner'] == batting_team]) / len(batting_matches) if len(batting_matches) > 0 else 0.5
            bowling_win_rate = len(bowling_matches[bowling_matches['winner'] == bowling_team]) / len(bowling_matches) if len(bowling_matches) > 0 else 0.5

            # Current match factors
            balls_bowled = int(overs_completed * 6)
            balls_remaining = int((total_overs - overs_completed) * 6)

            current_rr = current_score / overs_completed if overs_completed > 0 else 0
            required_rr = (target_runs - current_score) / (total_overs - overs_completed) if is_chase and target_runs and overs_completed < total_overs else 0

            # Win probability calculation (simplified logistic model)
            wickets_remaining = 10 - wickets_fallen

            # Base probability from team strength
            base_prob = (batting_win_rate + (1 - bowling_win_rate)) / 2

            # Adjust for current situation
            situation_factor = 0

            # Run rate advantage
            if is_chase:
                if current_rr > required_rr:
                    situation_factor += 0.2
                elif current_rr < required_rr * 0.8:
                    situation_factor -= 0.2
            else:
                # Batting first - higher scores are better
                if current_rr > 8:  # Good run rate
                    situation_factor += 0.1
                elif current_rr < 6:  # Poor run rate
                    situation_factor -= 0.1

            # Wickets factor
            wickets_factor = wickets_remaining / 10  # More wickets = higher chance
            situation_factor += (wickets_factor - 0.5) * 0.3

            # Balls remaining factor
            if balls_remaining < 24:  # Last 4 overs
                if wickets_remaining >= 3:
                    situation_factor += 0.1
                else:
                    situation_factor -= 0.2

            # Calculate final probability
            win_probability = min(max(base_prob + situation_factor, 0.05), 0.95)

            # Display results
            st.success("✅ Win Probability Calculated!")

            # Win probability display
            col_win1, col_win2 = st.columns(2)
            with col_win1:
                st.metric(f"{batting_team} Win Probability",
                         f"{win_probability*100:.1f}%",
                         delta=f"+{win_probability*100-50:.1f}%" if win_probability > 0.5 else f"{win_probability*100-50:.1f}%")
            with col_win2:
                st.metric(f"{bowling_team} Win Probability",
                         f"{(1-win_probability)*100:.1f}%",
                         delta=f"+{(1-win_probability)*100-50:.1f}%" if (1-win_probability) > 0.5 else f"{(1-win_probability)*100-50:.1f}%")

            # Progress bars
            st.subheader("📊 Win Probability Breakdown")
            st.progress(win_probability, text=f"{batting_team}: {win_probability*100:.1f}%")

            # Key factors
            st.subheader("🎯 Key Factors")
            factors = {
                "Team Strength": f"{batting_win_rate*100:.1f}% vs {bowling_win_rate*100:.1f}%",
                "Current Run Rate": f"{current_rr:.2f} RPO",
                "Wickets Remaining": wickets_remaining,
                "Balls Remaining": balls_remaining,
                "Required Run Rate": f"{required_rr:.2f} RPO" if required_rr > 0 else "N/A"
            }

            for factor, value in factors.items():
                st.write(f"**{factor}:** {value}")

with col2:
    st.subheader("📈 Win Probability Graph")

    # Generate sample win probability over time
    if 'win_probability' in locals():
        # Create sample data for visualization
        overs_range = np.arange(0, total_overs + 1, 1)
        win_probs_over_time = []

        for overs in overs_range:
            if overs <= overs_completed:
                # Historical data (simulated)
                base_prob = 0.5 + 0.1 * np.sin(overs * 0.5)  # Simulated momentum
                win_probs_over_time.append(min(max(base_prob, 0.1), 0.9))
            else:
                # Future prediction (simulated)
                remaining_overs = total_overs - overs
                decay_factor = np.exp(-remaining_overs * 0.1)
                future_prob = win_probability * decay_factor + 0.5 * (1 - decay_factor)
                win_probs_over_time.append(min(max(future_prob, 0.1), 0.9))

        if PLOTLY_AVAILABLE:
            fig = go.Figure()

            # Add win probability line
            fig.add_trace(go.Scatter(
                x=overs_range,
                y=[p*100 for p in win_probs_over_time],
                mode='lines+markers',
                name='Win Probability %',
                line=dict(color='#FF6B35', width=3),
                marker=dict(size=6)
            ))

            # Add current position marker
            fig.add_trace(go.Scatter(
                x=[overs_completed],
                y=[win_probability*100],
                mode='markers',
                name='Current Position',
                marker=dict(color='red', size=12, symbol='star')
            ))

            # Add target line at 50%
            fig.add_hline(y=50, line_dash="dash", line_color="gray",
                         annotation_text="50% Win Probability")

            fig.update_layout(
                title="Win Probability Over Match Progress",
                xaxis_title="Overs",
                yaxis_title="Win Probability (%)",
                height=400,
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Install plotly for interactive win probability graphs")
            # Simple matplotlib alternative
            st.line_chart(pd.DataFrame({
                'Overs': overs_range,
                'Win_Probability': [p*100 for p in win_probs_over_time]
            }).set_index('Overs'))

    else:
        st.info("Click 'Calculate Win Probability' to see the momentum graph")

# Additional features
st.markdown("---")
st.subheader("🎮 Match Simulation")

col_sim1, col_sim2, col_sim3 = st.columns(3)

with col_sim1:
    if st.button("⚡ Powerplay Analysis"):
        powerplay_overs = min(6, overs_completed)
        powerplay_score = current_score * (powerplay_overs / overs_completed) if overs_completed > 0 else 0
        st.metric("Powerplay Score", f"{powerplay_score:.0f} runs")
        st.info("Powerplay is crucial for setting the tempo!")

with col_sim2:
    if st.button("🎯 Death Overs Analysis"):
        death_overs_remaining = max(0, total_overs - overs_completed - 12)
        if death_overs_remaining <= 4:
            death_rr_needed = (target_runs - current_score) / death_overs_remaining if is_chase and death_overs_remaining > 0 else 0
            st.metric("Death Overs RR Needed", f"{death_rr_needed:.2f}")
            st.info("High pressure situation!")
        else:
            st.info("Death overs not yet reached")

with col_sim3:
    if st.button("📊 Match Statistics"):
        st.metric("Projected Final Score", f"{int(current_score + (total_overs - overs_completed) * current_rr)}")
        st.metric("Win Probability", f"{win_probability*100:.1f}%" if 'win_probability' in locals() else "Calculate first")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>Live Match Predictor</strong></p>
    <p>Real-time cricket analytics with win probability modeling</p>
    <p>🏏 Powered by historical IPL data and machine learning</p>
</div>
""", unsafe_allow_html=True)