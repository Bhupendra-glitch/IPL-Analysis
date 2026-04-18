import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from utils import load_data

st.title("🤖 ML Predictions")

matches, _ = load_data()
data = matches[['team1', 'team2', 'winner']].dropna()

X = pd.get_dummies(data[['team1', 'team2']])
y = data['winner']

model = RandomForestClassifier()
model.fit(X, y)

st.success("Model trained successfully ✅")