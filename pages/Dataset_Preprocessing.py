import streamlit as st
from utils import load_data

st.title("📂 Dataset & Preprocessing")

matches, deliveries = load_data()

st.write("### Missing Values")
st.write(matches.isnull().sum())

st.write("### Data Types")
st.write(matches.dtypes)