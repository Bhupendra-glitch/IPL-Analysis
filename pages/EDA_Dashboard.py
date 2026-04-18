import streamlit as st
from utils import load_data

try:
    import plotly.express as px
except ImportError:
    px = None

st.title("📈 EDA Dashboard")

matches, _ = load_data()

wins = matches['winner'].value_counts().reset_index()
wins.columns = ['Team', 'Wins']

if px is not None:
    fig = px.bar(wins, x='Team', y='Wins', title="Most Wins by Teams")
    st.plotly_chart(fig)
else:
    st.warning("Plotly is not installed. Install it with `pip install plotly` to view the full EDA chart.")
    st.bar_chart(wins.set_index('Team'))