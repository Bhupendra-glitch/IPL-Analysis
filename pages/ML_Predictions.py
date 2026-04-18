import streamlit as st
import pandas as pd
from utils import load_data

try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    RandomForestClassifier = None

st.title("🤖 ML Predictions")

matches, _ = load_data()
data = matches[['team1', 'team2', 'winner']].dropna()

X = pd.get_dummies(data[['team1', 'team2']])
y = data['winner']

if RandomForestClassifier is not None:
    model = RandomForestClassifier()
    model.fit(X, y)
    st.success("Model trained successfully ✅")
else:
    st.warning("scikit-learn is not installed. Install it with `pip install scikit-learn` to enable ML predictions.")
    st.info("The dataset is loaded, but model training is disabled until scikit-learn is available.")