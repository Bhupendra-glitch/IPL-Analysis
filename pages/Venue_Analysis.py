import streamlit as st
from utils import load_data

try:
    import plotly.express as px
except ImportError:
    px = None

st.title("📍 Venue Analysis")

matches, _ = load_data()

venue = matches['venue'].value_counts().reset_index()
venue.columns = ['Venue', 'Matches']

if px is not None:
    fig = px.bar(venue, x='Venue', y='Matches')
    st.plotly_chart(fig)
else:
    st.warning("Plotly is not installed. Install it with `pip install plotly` to view the venue analysis chart.")
    st.bar_chart(venue.set_index('Venue'))