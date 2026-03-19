import streamlit as st
from utils import load_data

st.title("🎯 Fantasy Team Generator")

_, deliveries = load_data()

top_players = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(11)

st.write("### Suggested Playing XI")
st.write(top_players)