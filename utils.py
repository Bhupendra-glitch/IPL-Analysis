import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    matches = pd.read_csv("data/matches.csv")
    deliveries = pd.read_csv("data/deliveries.csv")
    return matches, deliveries

def get_teams(matches):
    return sorted(matches['team1'].dropna().unique())