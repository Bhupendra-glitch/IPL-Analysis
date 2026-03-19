import streamlit as st

st.title("📊 Live Match Predictor")

runs = st.number_input("Current Score")
overs = st.number_input("Overs Completed")

if st.button("Predict"):
    predicted = runs + (20 - overs) * 8
    st.success(f"Predicted Score: {predicted}")