import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="IPL Analysis", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    matches = pd.read_csv("E:\Py3\End-to-End-ML-with-Deployment\matches.csv")
    deliveries = pd.read_csv("E:\Py3\End-to-End-ML-with-Deployment\deliveries.csv")
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
    st.title("🏏 IPL Data Analysis")
    st.write("Welcome to IPL Dashboard 🚀")

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
    fig = px.bar(wins, x='Team', y='Wins')
    st.plotly_chart(fig)

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