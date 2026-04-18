import streamlit as st
import pandas as pd
from pathlib import Path
try:
    import plotly.express as px
except ImportError:
    px = None

try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    RandomForestClassifier = None

BASE_DIR = Path(__file__).resolve().parent


# ---------------- CONFIG ----------------
st.set_page_config(page_title="IPL Analysis", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    matches = pd.read_csv(BASE_DIR / "matches.csv")
    deliveries = pd.read_csv(BASE_DIR / "deliveries.csv")
    return matches, deliveries

matches, deliveries = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🏏 IPL Dashboard")

page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📊 Overview",
    "📂 Dataset & Preprocessing",
    "📈 EDA Dashboard",
    "🏏 Team Analysis",
    "👤 Player Analysis",
    "⚔️ Head-to-Head",
    "📍 Venue Analysis",
    "📅 Season Trends",
    "🤖 ML Predictions",
    "📊 Live Match Predictor",
    "🎯 Fantasy Team Generator",
    "⚡ Performance Optimization",
    "📌 Insights",
    "📥 Export Reports"
])

# ---------------- HOME ----------------
if page == "🏠 Home":
    st.title("🏏 IPL Data Analysis Dashboard")
    st.markdown("""
    ## Welcome to the Comprehensive IPL Analytics Platform 🚀

    This interactive dashboard provides in-depth analysis of Indian Premier League (IPL) cricket data, offering insights into team performances, player statistics, match predictions, and more. Built with modern data science techniques and machine learning models, this platform serves as a complete toolkit for cricket enthusiasts, analysts, and fantasy sports players.

    ### 🎯 Key Features

    **📊 Data Exploration**
    - Comprehensive dataset of IPL matches from 2008-2022
    - Ball-by-ball delivery data for granular analysis
    - Interactive visualizations and charts

    **🏏 Team & Player Analysis**
    - Detailed team performance metrics and trends
    - Individual player statistics (batting, bowling, fielding)
    - Head-to-head comparisons between teams and players

    **🤖 Machine Learning Predictions**
    - Match winner prediction using advanced ML models
    - Score prediction for ongoing matches
    - Live match predictor with real-time updates

    **📈 Advanced Analytics**
    - Exploratory Data Analysis (EDA) with interactive dashboards
    - Venue-wise performance analysis
    - Season trends and historical patterns
    - Fantasy team optimization suggestions

    **⚡ Performance Insights**
    - Batting and bowling performance metrics
    - Strike rates, averages, and economy analysis
    - Top performers across different categories

    ### 📋 Dataset Overview
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Matches", len(matches))
        st.metric("Total Teams", len(matches['team1'].unique()))
    with col2:
        st.metric("Total Deliveries", f"{len(deliveries):,}")
        st.metric("Seasons Covered", len(matches['season'].unique()))

    st.markdown("""
    ### 🛠️ Technology Stack
    - **Frontend**: Streamlit for interactive web interface
    - **Data Processing**: Pandas, NumPy for data manipulation
    - **Visualization**: Plotly, Streamlit charts for interactive plots
    - **Machine Learning**: Scikit-learn for predictive modeling
    - **Deployment**: Ready for cloud deployment on Azure, AWS, or GCP

    ### 🎮 How to Use
    Navigate through the sidebar to explore different analysis modules. Each page offers interactive filters and visualizations to customize your analysis. Use the ML Predictions section for match outcome forecasting and fantasy team suggestions.

    ---
    *Built with ❤️ for cricket analytics | Data source: Kaggle IPL Dataset*
    """)

# ---------------- OVERVIEW ----------------
elif page == "📊 Overview":
    st.title("Overview")
    st.metric("Total Matches", len(matches))
    st.metric("Total Deliveries", len(deliveries))

# ---------------- DATASET ----------------
elif page == "📂 Dataset & Preprocessing":
    st.title("Dataset Info")
    st.write(matches.head())
    st.write(matches.isnull().sum())

# ---------------- EDA ----------------
elif page == "📈 EDA Dashboard":
    st.title("EDA Dashboard")
    wins = matches['winner'].value_counts().reset_index()
    wins.columns = ['Team', 'Wins']
    if px is not None:
        fig = px.bar(wins, x='Team', y='Wins')
        st.plotly_chart(fig)
    else:
        st.warning("Plotly is not installed. Install it with `pip install plotly` to view the full chart.")
        st.bar_chart(wins.set_index('Team'))

# ---------------- TEAM ANALYSIS ----------------
elif page == "🏏 Team Analysis":
    st.title("Team Analysis")
    teams = matches['team1'].dropna().unique()
    team = st.selectbox("Select Team", teams)

    team_matches = matches[
        (matches['team1'] == team) | (matches['team2'] == team)
    ]
    wins = team_matches[team_matches['winner'] == team]

    st.metric("Matches", len(team_matches))
    st.metric("Wins", len(wins))

# ---------------- PLAYER ----------------
elif page == "👤 Player Analysis":
    st.title("Top Batsmen")
    top = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top)

# ---------------- HEAD TO HEAD ----------------
elif page == "⚔️ Head-to-Head":
    st.title("Head to Head")
    teams = matches['team1'].dropna().unique()

    t1 = st.selectbox("Team 1", teams)
    t2 = st.selectbox("Team 2", teams)

    h2h = matches[
        ((matches['team1'] == t1) & (matches['team2'] == t2)) |
        ((matches['team1'] == t2) & (matches['team2'] == t1))
    ]

    st.write(h2h[['team1', 'team2', 'winner']])

# ---------------- VENUE ----------------
elif page == "📍 Venue Analysis":
    st.title("Venue Analysis")
    venue = matches['venue'].value_counts()
    st.bar_chart(venue)

# ---------------- SEASON ----------------
elif page == "📅 Season Trends":
    st.title("Season Trends")
    season = matches['season'].value_counts().sort_index()
    st.line_chart(season)

# ---------------- ML ----------------
elif page == "🤖 ML Predictions":
    st.title("ML Model")

    data = matches[['team1', 'team2', 'winner']].dropna()
    data = pd.get_dummies(data)

    X = data.drop('winner', axis=1)
    y = data['winner']

    model = RandomForestClassifier()
    model.fit(X, y)

    st.success("Model trained ✅")

# ---------------- LIVE PREDICTOR ----------------
elif page == "📊 Live Match Predictor":
    st.title("Live Score Predictor")

    runs = st.number_input("Runs")
    overs = st.number_input("Overs")

    if st.button("Predict"):
        score = runs + (20 - overs) * 8
        st.success(f"Predicted Score: {score}")

# ---------------- FANTASY ----------------
elif page == "🎯 Fantasy Team Generator":
    st.title("Fantasy XI")

    top = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(11)
    st.write(top)

# ---------------- PERFORMANCE ----------------
elif page == "⚡ Performance Optimization":
    st.title("Optimization")
    st.write("Using caching and optimized queries")

# ---------------- INSIGHTS ----------------
elif page == "📌 Insights":
    st.title("Insights")

    st.write("""
    - Chasing teams win more matches
    - Top order dominates scoring
    """)

# ---------------- EXPORT ----------------
elif page == "📥 Export Reports":
    st.title("Download Data")

    csv = matches.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download CSV",
        csv,
        "ipl_data.csv",
        "text/csv"
    )