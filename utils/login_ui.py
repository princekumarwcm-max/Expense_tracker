import streamlit as st
import bcrypt
import json
import os
import time

USER_DB_PATH = "users.json"
VIDEO_URL = "app/static/active_bg.mp4"

# ---------- USER DB ----------
def load_users():
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

# ---------- UI ----------
def render_login():

    st.markdown(f"""
    <style>
    body {{
        background-color: black;
    }}

    #bg-video {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -1;
        filter: brightness(0.4);
    }}

    .title {{
        text-align: center;
        font-size: 60px;
        font-weight: 800;
        color: #ff4d8d;
    }}

    .card {{
        background: rgba(0,0,0,0.7);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #ff4d8d;
        box-shadow: 0 0 40px #ff4d8d;
    }}
    </style>

    <video autoplay muted loop id="bg-video">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>EXPENSE TRACKER</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])

    # ---------- LOGIN ----------
    with tab1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            users = load_users()

            # 🔥 Hard login
            if email == "princekumar.wcm@gmail.com" and password == "admin123":
                st.session_state["auth"] = True
                st.success("Login Success ✅")
                time.sleep(1)
                st.rerun()

            user = users.get(email)

            if user and bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
                st.session_state["auth"] = True
                st.success("Login Success ✅")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- REGISTER ----------
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        new_email = st.text_input("New Email")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
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

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- MAIN ----------
def main():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        render_login()
    else:
        st.title("💸 Dashboard")
        st.write("Ab yaha tumhara pura expense tracker chalega 🚀")

if __name__ == "__main__":
    main()
