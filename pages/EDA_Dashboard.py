import streamlit as st
import plotly.express as px
from utils import load_data

st.title("📈 EDA Dashboard")

matches, _ = load_data()

wins = matches['winner'].value_counts().reset_index()
wins.columns = ['Team', 'Wins']

fig = px.bar(wins, x='Team', y='Wins', title="Most Wins by Teams")
st.plotly_chart(fig)