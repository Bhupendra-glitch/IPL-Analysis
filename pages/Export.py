import streamlit as st
from utils import load_data

st.title("📥 Export Reports")

matches, _ = load_data()

csv = matches.to_csv(index=False).encode('utf-8')

st.download_button(
    "Download Matches Data",
    csv,
    "matches.csv",
    "text/csv"
)