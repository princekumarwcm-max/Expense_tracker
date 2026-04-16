import streamlit as st
import bcrypt
import json
import os
import time

USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)

def render_login_page():

    st.markdown("""
    <style>
    body {background:black;}

    .title{
        text-align:center;
        font-size:55px;
        font-weight:900;
        color:#ff4d8d;
        text-shadow:0 0 20px #ff4d8d;
    }

    .box{
        background:rgba(0,0,0,0.7);
        padding:30px;
        border-radius:20px;
        border:2px solid #ff4d8d;
        box-shadow:0 0 30px #ff4d8d;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>💸 EXPENSE TRACKER</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])

    # LOGIN
    with tab1:
        st.markdown("<div class='box'>", unsafe_allow_html=True)

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("LOGIN"):
            users = load_users()

            # demo login
            if email == "admin@gmail.com" and password == "admin123":
                st.session_state["auth"] = True
                st.success("Login Success 🚀")
                st.rerun()

            user = users.get(email)
            if user and bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
                st.session_state["auth"] = True
                st.success("Login Success 🚀")
                st.rerun()
            else:
                st.error("Wrong Credentials ❌")

        st.markdown("</div>", unsafe_allow_html=True)

    # REGISTER
    with tab2:
        st.markdown("<div class='box'>", unsafe_allow_html=True)

        new_email = st.text_input("New Email")
        new_pass = st.text_input("New Password", type="password")

        if st.button("REGISTER"):
            users = load_users()

            if new_email in users:
                st.warning("Already exists")
            else:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                users[new_email] = {"hashed_password": hashed}
                save_users(users)
                st.success("Account created ✅")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
