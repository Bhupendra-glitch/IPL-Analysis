import streamlit as st
from utils import load_data

st.title("👤 Player Analysis")

_, deliveries = load_data()

top_batsmen = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)

st.bar_chart(top_batsmen)