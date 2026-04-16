import streamlit as st

def apply_dashboard_styles():
    """Injects professional, premium high-tech styling into the dashboard with a security alarm engine."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Orbitron:wght@600;800&family=Poppins:wght@600&display=swap');

            /* --- GLOBAL DARK THEME --- */
            html, body, [data-testid="stAppViewContainer"], .main {
                background-color: #050505 !important;
                background-image: 
                    radial-gradient(circle at 10% 20%, rgba(255, 77, 141, 0.05) 0%, transparent 40%),
                    radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 40%) !important;
                color: #ffffff !important;
                font-family: 'Inter', sans-serif;
                transition: background-color 0.3s;
            }

            /* --- FLASH RED ANIMATION (APP-WIDE) --- */
            .flash-red-alarm {
                animation: app-flash-red 0.8s ease-out infinite;
            }
            @keyframes app-flash-red {
                0% { background-color: rgba(255, 0, 0, 0); }
                50% { background-color: rgba(255, 0, 0, 0.2); }
                100% { background-color: rgba(255, 0, 0, 0); }
            }

            [data-testid="stHeader"] {
                background: rgba(0,0,0,0) !important;
            }

            /* --- TYPOGRAPHY --- */
            h1, h2, h3, .st-emotion-cache-10trblm {
                font-family: 'Orbitron', sans-serif !important;
                text-transform: uppercase;
                letter-spacing: 3px;
                color: #ffffff !important;
                text-shadow: 0 4px 15px rgba(255, 77, 141, 0.3);
            }

            /* --- SIDEBAR REFINEMENT (DARK) --- */
            [data-testid="stSidebar"] {
                background-color: rgba(10, 10, 10, 0.95) !important;
                border-right: 1px solid rgba(255, 77, 141, 0.2);
            }

            /* --- PREMIUM CARDS & CONTAINERS --- */
            .st-emotion-cache-1r6slb0, .st-emotion-cache-12w0qpk {
                background: rgba(20, 20, 20, 0.6) !important;
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 77, 141, 0.2);
                border-radius: 20px;
                padding: 25px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            }

            /* --- METRIC CARD OVERHAUL --- */
            .metric-card {
                background: rgba(30, 30, 30, 0.4);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 25px;
                border: 1px solid rgba(255, 77, 141, 0.1);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                transition: transform 0.3s ease;
                margin-bottom: 20px;
                position: relative;
                overflow: hidden;
            }
            .metric-card::before {
                content: "";
                position: absolute;
                top: 0; left: 0; width: 4px; height: 100%;
                background: linear-gradient(to bottom, #ff4d8d, #ec4899);
            }

            /* --- FORM INPUTS & BUTTONS --- */
            [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
                background: rgba(40, 40, 40, 0.8) !important;
                border: 1px solid rgba(255, 77, 141, 0.2) !important;
                color: #ffffff !important;
            }
            .stButton button {
                background: linear-gradient(90deg, #ff4d8d, #ec4899) !important;
                color: #fff !important;
                font-family: 'Orbitron', sans-serif !important;
                font-weight: 800 !important;
                border-radius: 12px !important;
                box-shadow: 0 8px 25px rgba(255, 77, 141, 0.3) !important;
            }

            /* --- ALARM BANNER SLIDE-IN --- */
            .alarm-slide-in {
                animation: slide-in-top 0.5s cubic-bezier(0.250, 0.460, 0.450, 0.940) both;
            }
            @keyframes slide-in-top {
                0% { transform: translateY(-100px); opacity: 0; }
                100% { transform: translateY(0); opacity: 1; }
            }
        </style>

        <script>
            // DASHBOARD ALARM SYSTEM
            const appSiren = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-police-siren-one-loop-1631.mp3");
            const appBeep = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-system-beep-buzz-952.mp3");

            window.triggerAppAlarm = function(type) {
                const body = document.querySelector('[data-testid="stAppViewContainer"]');
                if (type === 'siren') {
                    appSiren.currentTime = 0;
                    appSiren.volume = 0.6;
                    appSiren.play().catch(e => console.log("Audio blocked"));
                    body.classList.add('flash-red-alarm');
                    setTimeout(() => {
                        appSiren.pause();
                        body.classList.remove('flash-red-alarm');
                    }, 6000);
                }
                if (type === 'beep') {
                    appBeep.currentTime = 0;
                    appBeep.volume = 0.4;
                    appBeep.play().catch(e => console.log("Audio blocked"));
                }
            }

            // Global Monitor for "Budget exceeded!" message
            const appObs = new MutationObserver(() => {
                const text = document.body.innerText;
                if (text.includes("Budget exceeded!")) {
                    if (!window.budgetAlarmActive) {
                        window.triggerAppAlarm('siren');
                        window.budgetAlarmActive = true;
                        setTimeout(() => window.budgetAlarmActive = false, 10000);
                    }
                }
                if (text.includes("High spending detected")) {
                    if (!window.beepAlarmActive) {
                        window.triggerAppAlarm('beep');
                        window.beepAlarmActive = true;
                        setTimeout(() => window.beepAlarmActive = false, 5000);
                    }
                }
            });
            appObs.observe(document.body, { childList: true, subtree: true });
        </script>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None, delta_color="normal"):
    """Renders a high-tech KPI card with Sakura theme."""
    color_map = {
        "normal": "#ff4d8d",  # Pink
        "inverse": "#ef4444", # Red
        "off": "#8892b0"      # Muted
    }
    glow_color = color_map.get(delta_color, "#ff4d8d")
    
    delta_html = f"<div class='metric-delta' style='color:{glow_color}'>{delta}</div>" if delta else ""
    
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {glow_color};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)
