from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

@st.cache_data
def load_data():
    matches = pd.read_csv(BASE_DIR / "matches.csv")
    deliveries = pd.read_csv(BASE_DIR / "deliveries.csv")
    return matches, deliveries

def get_teams(matches):
    return sorted(matches['team1'].dropna().unique())