import json
import streamlit as st

try:
    with open("auth.json", "r") as f:
        auth_data = json.load(f)
except json.JSONDecodeError:
    st.error("❌ auth.json file is empty or invalid JSON")
    auth_data = {}
except FileNotFoundError:
    st.error("❌ auth.json file not found")
    auth_data = {}
