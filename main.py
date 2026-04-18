import streamlit as st
import pandas as pd
from pathlib import Path
import time

# Set page configuration
st.set_page_config(
    page_title="IPL Cricket Analytics Dashboard",
    page_icon="🏏",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={
        'Get Help': 'https://github.com/your-repo/ipl-analysis',
        'Report a bug': 'https://github.com/your-repo/ipl-analysis/issues',
        'About': '''
        # IPL Cricket Analytics Dashboard
        Comprehensive analysis platform for Indian Premier League cricket data.
        Built with Streamlit, Pandas, and Machine Learning.
        '''
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #FF6B35;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent
    matches = pd.read_csv(base_dir / "matches.csv")
    deliveries = pd.read_csv(base_dir / "deliveries.csv")
    return matches, deliveries

matches, deliveries = load_data()

# Main header
st.markdown('<h1 class="main-header">🏏 IPL Cricket Analytics Dashboard</h1>', unsafe_allow_html=True)

# Subtitle
st.markdown("""
<div style="text-align: center; font-size: 1.2rem; margin-bottom: 2rem; color: #666;">
    <strong>End-to-End Machine Learning Analysis of Indian Premier League Cricket Data</strong><br>
    From 2008 to 2024 • Ball-by-ball insights • Predictive analytics • Fantasy sports optimization
</div>
""", unsafe_allow_html=True)

# Key metrics in a beautiful layout
st.markdown("## 📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{len(matches):,}</h3>
        <p>Total Matches</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{len(matches['team1'].unique())}</h3>
        <p>Teams</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{len(matches['season'].unique())}</h3>
        <p>Seasons</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{len(deliveries):,}</h3>
        <p>Deliveries</p>
    </div>
    """, unsafe_allow_html=True)

# Project description
st.markdown("## 🎯 About This Project")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🚀 Comprehensive IPL Analysis Platform</h4>
        <p>This dashboard provides an end-to-end solution for IPL cricket data analysis, featuring:</p>
        <ul>
            <li><strong>Data Exploration:</strong> Interactive visualizations of IPL statistics</li>
            <li><strong>Team & Player Analysis:</strong> Performance metrics and comparisons</li>
            <li><strong>Machine Learning:</strong> Match prediction and score forecasting</li>
            <li><strong>Fantasy Sports:</strong> Data-driven team optimization</li>
            <li><strong>Real-time Insights:</strong> Live match predictions and trends</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>🛠️ Technology Stack</h4>
        <ul>
            <li>🐍 Python</li>
            <li>📊 Pandas & NumPy</li>
            <li>🎨 Streamlit</li>
            <li>📈 Plotly</li>
            <li>🤖 Scikit-learn</li>
            <li>📉 Machine Learning</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Key features showcase
st.markdown("## ✨ Key Features")

features = [
    {
        "icon": "📊",
        "title": "Data Visualization",
        "description": "Interactive charts and graphs for comprehensive data exploration"
    },
    {
        "icon": "🤖",
        "title": "ML Predictions",
        "description": "Advanced machine learning models for match outcome prediction"
    },
    {
        "icon": "👥",
        "title": "Player Analytics",
        "description": "Detailed performance analysis for batsmen, bowlers, and all-rounders"
    },
    {
        "icon": "🏟️",
        "title": "Venue Analysis",
        "description": "Stadium-wise performance statistics and insights"
    },
    {
        "icon": "📈",
        "title": "Season Trends",
        "description": "Year-over-year analysis and historical patterns"
    },
    {
        "icon": "🎯",
        "title": "Fantasy Optimization",
        "description": "Data-driven fantasy cricket team selection and strategy"
    }
]

cols = st.columns(3)
for i, feature in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="feature-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{feature['icon']}</div>
            <h5>{feature['title']}</h5>
            <p style="color: #666; font-size: 0.9rem;">{feature['description']}</p>
        </div>
        """, unsafe_allow_html=True)

# Quick insights section
st.markdown("## 🔍 Quick Insights")

col1, col2, col3 = st.columns(3)

with col1:
    # Top run scorer
    top_batsman = deliveries.groupby('batter')['batsman_runs'].sum().idxmax()
    top_runs = deliveries.groupby('batter')['batsman_runs'].sum().max()
    st.metric("Top Run Scorer", f"{top_batsman}", f"{top_runs:,} runs")

with col2:
    # Most successful team
    most_wins = matches['winner'].value_counts().idxmax()
    win_count = matches['winner'].value_counts().max()
    st.metric("Most Successful Team", f"{most_wins}", f"{win_count} wins")

with col3:
    # Highest scoring venue
    avg_scores = matches.groupby('venue')['target_runs'].mean().dropna()
    top_venue = avg_scores.idxmax()
    avg_score = avg_scores.max()
    st.metric("Highest Scoring Venue", f"{top_venue[:20]}...", f"{avg_score:.0f} avg runs")

# Navigation guide
st.markdown("## 🧭 Navigation Guide")

st.markdown("""
<div class="feature-card">
    <p>Use the sidebar to navigate through different sections of the dashboard:</p>
    <ul>
        <li><strong>🏠 Home:</strong> Project overview and key metrics</li>
        <li><strong>📊 Overview:</strong> Dataset summary and basic statistics</li>
        <li><strong>📈 EDA Dashboard:</strong> Exploratory data analysis with visualizations</li>
        <li><strong>🏏 Team Analysis:</strong> Team performance and comparisons</li>
        <li><strong>👤 Player Analysis:</strong> Individual player statistics</li>
        <li><strong>🤖 ML Predictions:</strong> Machine learning based predictions</li>
        <li><strong>📌 Insights:</strong> Key findings and conclusions</li>
        <li><strong>📥 Export Reports:</strong> Download analysis results and data</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><strong>IPL Cricket Analytics Dashboard</strong></p>
        <p>Built with ❤️ using Streamlit • Data Science for Cricket Enthusiasts</p>
        <p>© 2026 IPL Analytics Project</p>
    </div>
    """, unsafe_allow_html=True)

# Add some animation/loading effect
if st.button("🚀 Start Exploring", type="primary"):
    with st.spinner("Loading dashboard..."):
        time.sleep(1)
    st.success("Dashboard ready! Use the sidebar to navigate.")
    st.balloons()

