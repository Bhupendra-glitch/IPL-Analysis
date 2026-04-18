import streamlit as st
from utils import load_data

try:
    import plotly.express as px
except ImportError:
    px = None

st.title("📅 Season Trends")

matches, _ = load_data()

season = matches['season'].value_counts().sort_index()

if px is not None:
    fig = px.line(x=season.index, y=season.values, title="Matches per Season")
    st.plotly_chart(fig)
else:
    st.warning("Plotly is not installed. Install it with `pip install plotly` to view the season trend chart.")
    st.line_chart(season)