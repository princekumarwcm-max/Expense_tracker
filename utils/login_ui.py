import streamlit as st
import bcrypt
import time
import json
import os
from datetime import datetime, timedelta

USER_DB_PATH = "users.json"
VIDEO_URL = "app/static/active_bg.mp4"

# ---------------- USERS ----------------
def load_users():
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

# ---------------- LOGIN PAGE ----------------
def render_login_page():

    # session init
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # ---------------- UI SAME ----------------
    st.markdown(f"""
        <style>
        body {{background-color:black;}}
        </style>

        <video autoplay muted loop id="bg-video" style="position:fixed; width:100%; height:100%; object-fit:cover; z-index:-1;">
            <source src="{VIDEO_URL}" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center;color:#ff4d8d;'>EXPENSE TRACKER</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:white;'>SECURE ACCESS</h3>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("LOGIN"):
            users = load_users()

            # 🔥 HARD LOGIN (important fix)
            if email == "princekumar.wcm@gmail.com" and password == "admin123":
                st.session_state["authenticated"] = True
                st.success("Login Successful ✅")
                st.rerun()

            user = users.get(email)

            if user and bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
                st.session_state["authenticated"] = True
                st.success("Login Successful ✅")
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")

    # ---------------- REGISTER ----------------
    with tab2:
        new_email = st.text_input("New Email")
        new_pass = st.text_input("New Password", type="password")

        if st.button("REGISTER"):
            if new_email and new_pass:
                users = load_users()

                if new_email in users:
                    st.warning("User already exists")
                else:
                    hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                    users[new_email] = {"hashed_password": hashed}
                    save_users(users)

                    st.success("Account Created ✅")
                    time.sleep(1)
                    st.rerun()

# ---------------- MAIN FLOW ----------------
def main():
    if not st.session_state.get("authenticated"):
        render_login_page()
    else:
        st.title("🎉 Dashboard Open Ho Gaya")
        st.write("Yaha se tumhara pura expense tracker chalega")

if __name__ == "__main__":
    main()
