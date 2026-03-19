import streamlit as st
from utils import load_data

st.title("📊 Overview")

matches, deliveries = load_data()

st.metric("Total Matches", len(matches))
st.metric("Total Deliveries", len(deliveries))

st.write("### Sample Data")
st.dataframe(matches.head())