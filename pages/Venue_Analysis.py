import streamlit as st
import plotly.express as px
from utils import load_data

st.title("📍 Venue Analysis")

matches, _ = load_data()

venue = matches['venue'].value_counts().reset_index()
venue.columns = ['Venue', 'Matches']

fig = px.bar(venue, x='Venue', y='Matches')
st.plotly_chart(fig)