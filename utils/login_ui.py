import streamlit as st
import bcrypt
import time
import json
import os
import pandas as pd
from datetime import datetime, timedelta

USER_DB_PATH = "users.json"
# Serving from static folder to prevent memory crashes
VIDEO_URL = "app/static/active_bg.mp4"

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

def render_login_page():
    # Initialize lockout state
    if "failed_attempts" not in st.session_state:
        st.session_state["failed_attempts"] = 0
    if "lockout_until" not in st.session_state:
        st.session_state["lockout_until"] = None

    # Check for lockout
    is_locked = False
    if st.session_state["lockout_until"]:
        if datetime.now() < st.session_state["lockout_until"]:
            is_locked = True
        else:
            st.session_state["lockout_until"] = None
            st.session_state["failed_attempts"] = 0

    # CSS for Cinematic HD Video Gateway + Pop Title Layout + SHAKE ENGINE
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Inter:wght@300;400;500;600;700&family=Poppins:wght@800&display=swap');

            html, body, [data-testid="stAppViewContainer"], .main {{
                background-color: #000 !important;
                margin: 0; padding: 0; overflow-x: hidden;
            }}

            [data-testid="stSidebar"], [data-testid="stHeader"], footer {{ display: none !important; }}

            /* --- VIDEO BACKGROUND --- */
            #bg-video {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                object-fit: cover; z-index: 0;
                filter: brightness(0.4);
            }}

            /* --- HEADER SECTION --- */
            .header-container {{
                text-align: center;
                margin-top: 5vh;
                margin-bottom: 20px;
                animation: pop-in 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
                position: relative; z-index: 1000;
            }}
            .main-title-text {{
                font-family: 'Poppins', sans-serif;
                font-size: 5rem; font-weight: 800;
                color: #ff4d8d;
                background: linear-gradient(135deg, #ff4d8d 0%, #ffcbe0 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                filter: drop-shadow(0 0 30px rgba(255, 77, 141, 0.6));
                margin-bottom: 5px;
            }}
            .system-pill {{
                display: inline-block;
                background: linear-gradient(90deg, #ff4d8d, #ec4899);
                color: #fff;
                padding: 6px 20px;
                border-radius: 50px;
                font-family: 'Orbitron', sans-serif;
                font-size: 0.75rem;
                font-weight: 800;
                letter-spacing: 2px;
                text-transform: uppercase;
                box-shadow: 0 0 20px rgba(255, 77, 141, 0.4);
            }}

            /* --- LOGIN CARD --- */
            .stForm, .login-box {{
                background: rgba(10, 10, 10, 0.8) !important;
                backdrop-filter: blur(40px) !important;
                border: 2px solid rgba(255, 77, 141, 0.4) !important;
                border-radius: 40px !important;
                padding: 45px !important;
                box-shadow: 0 0 100px rgba(0, 0, 0, 0.8) !important;
                width: 480px !important;
                max-width: 95% !important;
                margin: 0 auto !important;
                position: relative; z-index: 10001;
            }}

            /* --- SHAKE ANIMATION --- */
            .shake-effect {{
                animation: shake 0.5s cubic-bezier(.36,.07,.19,1) both;
            }}
            @keyframes shake {{
                10%, 90% {{ transform: translate3d(-1px, 0, 0); }}
                20%, 80% {{ transform: translate3d(2px, 0, 0); }}
                30%, 50%, 70% {{ transform: translate3d(-4px, 0, 0); }}
                40%, 60% {{ transform: translate3d(4px, 0, 0); }}
            }}
            
            /* --- FLASH RED ANIMATION --- */
            .flash-red-active {{
                animation: flash-red 0.5s ease-out;
            }}
            @keyframes flash-red {{
                0% {{ box-shadow: 0 0 0px red; }}
                50% {{ box-shadow: 0 0 100px red; border-color: red; }}
                100% {{ box-shadow: 0 0 0px red; }}
            }}

            /* --- UI CONTROLS --- */
            [data-testid="stTextInput"] label {{
                font-family: 'Orbitron', sans-serif !important;
                color: rgba(255, 255, 255, 0.8) !important;
                font-size: 0.75rem !important;
                letter-spacing: 2px !important;
                text-transform: uppercase !important;
            }}
            [data-testid="stTextInput"] input {{
                background: rgba(255, 255, 255, 0.08) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                color: #fff !important;
                border-radius: 12px !important;
                padding: 16px !important;
            }}
            .stButton button {{
                width: 100%;
                background: linear-gradient(135deg, #ff4d8d 0%, #ec4899 100%) !important;
                border-radius: 14px !important;
                padding: 18px !important;
                font-family: 'Orbitron', sans-serif !important;
                font-weight: 800 !important;
                color: #fff !important;
                border: none !important;
                box-shadow: 0 10px 30px rgba(255, 77, 141, 0.3) !important;
            }}
            
            .secure-heading {{
                font-family: 'Orbitron', sans-serif; 
                text-align: center; 
                color: #fff; 
                font-size: 2.2rem; 
                letter-spacing: 6px; 
                font-weight: 800;
                margin-bottom: 30px;
                text-transform: uppercase;
                background: linear-gradient(135deg, #fff, #ff4d8d);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }}

            /* --- AI PULSING ORB ANIMATION --- */
            .ai-orb-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 10px 0 30px 0;
            }}
            .ai-orb {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: radial-gradient(circle, #ffcbe0 10%, #ff4d8d 50%, #1a0033 90%);
                box-shadow: 0 0 30px #ff4d8d, inset 0 0 15px #fff;
                animation: pulse-orb 2s infinite alternate ease-in-out;
            }}
            @keyframes pulse-orb {{
                0% {{ transform: scale(0.95); box-shadow: 0 0 20px #ff4d8d, inset 0 0 10px #fff; }}
                100% {{ transform: scale(1.05); box-shadow: 0 0 60px #fff, inset 0 0 30px #ffcbe0; }}
            }}

            .audio-info {{
                position: fixed; bottom: 20px; width: 100%; text-align: center;
                color: rgba(255,255,255,0.4); font-size: 0.7rem; font-family: Inter;
                pointer-events: none; z-index: 999;
            }}
            
            /* Hide tab headers background */
            [data-testid="stTabs"] {{ background: transparent !important; }}
        </style>

        <video autoplay muted loop id="bg-video">
            <source src="{VIDEO_URL}" type="video/mp4">
        </video>

        <div class="audio-info">[ Security Audio Armed & Optimized ]</div>

        <script>
            // DASHBOARD ALARM SYSTEM
            const sirenAud = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-police-siren-one-loop-1631.mp3");
            const alertAud = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-system-beep-buzz-952.mp3");

            let systemStartArmed = true;

            function playSiren(strong = false) {{
                sirenAud.currentTime = 0;
                sirenAud.volume = strong ? 0.8 : 0.5;
                sirenAud.play().catch(e => {{
                    console.log("Audio ARM required - first click will enable sirens.");
                    // Arm on first body click if blocked
                    document.body.addEventListener('click', () => sirenAud.play().catch(()=>{{}}), {{once: true}});
                }});
                setTimeout(() => sirenAud.pause(), 7000);
            }}

            // --- START-UP SIREN ENGINE ---
            function handleStartUp() {{
                if (systemStartArmed) {{
                    playSiren();
                    systemStartArmed = false;
                }}
            }}
            document.addEventListener('mouseover', handleStartUp, {{once: true}});
            document.addEventListener('click', handleStartUp, {{once: true}});

            window.triggerSecurity = function(type) {{
                const target = document.querySelector('.stForm') || document.querySelector('.login-box');
                if (!target) return;

                if (type === 'fail') {{
                    playSiren();
                    target.classList.add('shake-effect');
                    target.classList.add('flash-red-active');
                    setTimeout(() => {{
                        target.classList.remove('shake-effect');
                        target.classList.remove('flash-red-active');
                    }}, 1000);
                }}
            }}

            // Streamlit Bridge for SIREN
            const obs = new MutationObserver(() => {{
                const text = document.body.innerText;
                if (text.includes("INVALID CREDENTIALS") || text.includes("Too many attempts")) {{
                    window.triggerSecurity('fail');
                }}
            }});
            obs.observe(document.body, {{ childList: true, subtree: true }});
        </script>
    """, unsafe_allow_html=True)

    # PAGE STRUCTURE
    st.markdown('<div class="header-container"><div class="main-title-text">EXPENSE TRACKER</div><div class="system-pill">Neural Identity System v8</div></div>', unsafe_allow_html=True)

    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.container():
            st.markdown('<div class="secure-heading">SECURE ACCESS</div>', unsafe_allow_html=True)
            st.markdown('<div class="ai-orb-container"><div class="ai-orb"></div></div>', unsafe_allow_html=True)
            
            # --- LOCKOUT MESSAGE ---
            if is_locked:
                remaining = int((st.session_state["lockout_until"] - datetime.now()).total_seconds())
                st.error(f"🚨 TOO MANY ATTEMPTS. CONSOLE LOCKED FOR {remaining}s.")
                st.info("System security protocol active. Please wait for cool-down.")
                time.sleep(1)
                st.rerun()

            if st.session_state.get("feedback_msg"):
                st.error(st.session_state["feedback_msg"])
                st.session_state["feedback_msg"] = None

            tab1, tab2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])
            
            with tab1:
                email = st.text_input("RECOGNITION ID (EMAIL)", placeholder="operator@neural.net", disabled=is_locked, key="login_email")
                password = st.text_input("CRYPTOGRAPHIC KEY", type="password", placeholder="••••••••", disabled=is_locked, key="login_pass")
                
                if st.button("AUTHENTICATE SYSTEM", disabled=is_locked):
                    users = load_users()
                    user_data = users.get(email)
                    stored_hash = user_data.get("hashed_password") if isinstance(user_data, dict) else user_data
                    
                    if stored_hash and bcrypt.checkpw(password.encode(), stored_hash.encode()):
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = email
                        st.session_state["failed_attempts"] = 0
                        # Clear old live_df when a new user logs in
                        if "live_df" in st.session_state:
                            del st.session_state["live_df"]
                        st.success("ACCESS GRANTED.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state["failed_attempts"] += 1
                        if st.session_state["failed_attempts"] >= 3:
                            st.session_state["lockout_until"] = datetime.now() + timedelta(seconds=60)
                            st.session_state["feedback_msg"] = "Too many attempts, try again later."
                        else:
                            st.session_state["feedback_msg"] = "INVALID CREDENTIALS."
                        st.rerun()

            with tab2:
                new_email = st.text_input("New Email Address", key="reg_email")
                new_pass = st.text_input("Create Password", type="password", key="reg_pass")
                if st.button("CREATE NEW ACCOUNT", type="primary"):
                    if new_email and new_pass:
                        users = load_users()
                        if new_email in users:
                            st.warning("This email is already registered! Please login.")
                        else:
                            hv = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                            users[new_email] = {"hashed_password": hv}
                            save_users(users)
                            st.success("Account created successfully! You can now switch to the LOGIN tab to access your fresh dashboard.")
                            time.sleep(2)
                            st.rerun()

def main():
    # Initialize session state keys if they don't exist
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        render_login_page()
    else:
        # ---- EXPENSE TRACKER DASHBOARD ----
        st.title(f"💰 Expense Tracker – Welcome {st.session_state['user_email']}")

        # Initialize dataframe if not present
        if "live_df" not in st.session_state:
            st.session_state["live_df"] = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

        # Add expense form
        with st.form("expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date")
                category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Other"])
            with col2:
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.5)
                note = st.text_input("Note")
            submitted = st.form_submit_button("Add Expense")
            if submitted and amount > 0:
                new_row = pd.DataFrame([[date, category, amount, note]], columns=st.session_state["live_df"].columns)
                st.session_state["live_df"] = pd.concat([st.session_state["live_df"], new_row], ignore_index=True)
                st.success("Expense added!")

        st.subheader("📊 Your Expenses")
        st.dataframe(st.session_state["live_df"], use_container_width=True)

        # Logout button
        if st.button("🔓 Logout"):
            st.session_state["authenticated"] = False
            st.session_state.pop("user_email", None)
            st.rerun()

if __name__ == "__main__":
    main()
