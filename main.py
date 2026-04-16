# main.py
import streamlit as st
import json
import bcrypt
import os
import utils.app as app
from utils.alerts import start_background_scheduler
from utils.alarm_system import password_gate, check_budget_alarm
from utils.login_ui import render_login_page

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="Expense Tracker",
    layout="centered"
)

# -------------------------------
# Session state
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# -------------------------------
# LOGIN PAGE - Advanced Cinematic UI
# -------------------------------
if not st.session_state["authenticated"]:
    from utils.login_ui import render_login_page
    render_login_page()
    st.stop()

# --- SECONDARY SECURITY GATE ---
if not password_gate("Dashboard"):
    st.stop()


# -------------------------------
# MAIN APP - Sirf login ke baad
# -------------------------------
user_email = st.session_state.get("user_email", "Admin").split("@")[0]
st.sidebar.success(f"✅ Logged in as: {user_email}")
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = None
    if "live_df" in st.session_state:
        del st.session_state["live_df"]
    st.rerun()

st.sidebar.markdown("## 🤖 xAI (Grok) Settings")
xai_key_default = "xai-WBlt1bYcxiCgVr7w6A9Ff6ZJYnfLSSt4z3biMudczMw87ejXHnQNX2dK32PB29KiHsWhNpVSkJrHFmaz"
xai_api_key = st.sidebar.text_input("xAI API Key", type="password", value=xai_key_default)
if xai_api_key:
    st.session_state["xai_api_key"] = xai_api_key

st.session_state["monthly_budget"] = st.sidebar.number_input(
    "Monthly Budget (₹)", min_value=1000, value=30000, step=1000
)

# Start background scheduler
try:
    start_background_scheduler()
except Exception as e:
    st.sidebar.warning(f"Background scheduler error: {e}")





# Run the app
try:
    app.run()
except Exception as e:
    st.error(f"Error in app: {e}")
    st.info("Make sure all files are present in utils folder")
















