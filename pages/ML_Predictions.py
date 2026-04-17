import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from utils import load_data

st.title("🤖 ML Predictions")

matches, _ = load_data("E:\Py3\End-to-End-ML-with-Deployment\matches.csv")
data = matches[['team1', 'team2', 'winner']].dropna()

data = pd.get_dummies(data)

x = data.drop('Winner', axis=1)
y = data['Winner']

model = RandomForestClassifier()
model.fit(x, y)

st.success("Model trained successfully ✅")