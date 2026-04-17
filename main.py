import streamlit as st

st.set_page_config(
    page_title="IPL Analysis",
    page_icon="🏏",
    initial_sidebar_state="expanded",
    layout="wide"
)

from app import load_data
import homePage
import exploratoryDataAnalysis
import playerAnalysis
import batter_vs_bowlerAnalysis
import teamAnalysis
import team_vs_teamAnalysis
import scorePrediction 
import winnerPrediction

