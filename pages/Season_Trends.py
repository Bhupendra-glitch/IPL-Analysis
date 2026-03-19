import streamlit as st
import plotly.express as px
from utils import load_data

st.title("📅 Season Trends")

matches, _ = load_data()

season = matches['season'].value_counts().sort_index()

fig = px.line(x=season.index, y=season.values, title="Matches per Season")
st.plotly_chart(fig)