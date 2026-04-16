import streamlit as st
import streamlit.components.v1 as components
import bcrypt
import time
from utils.alerts import send_emergency_call, send_emergency_sms, send_whatsapp_alert, send_telegram_alert, send_phone_notification

# Configuration
DEFAULT_PASSWORD = "admin123"

# ============================================================
# SIREN ENGINE — Uses components.v1.html() to run JS properly
# ============================================================
def play_police_siren(duration_ms=10000):
    """Plays a police siren sound and browser voice alert for the specified duration."""
    components.html(f"""
        <script>
            // 1. Play Police Siren Sound
            const siren = new Audio("https://assets.mixkit.co/sfx/preview/mixkit-police-siren-one-loop-1631.mp3");
            siren.volume = 0.9;
            siren.loop = true;
            siren.play().then(() => {{
                setTimeout(() => {{
                    siren.pause();
                    siren.currentTime = 0;
                }}, {duration_ms});
            }}).catch(e => {{
                console.log("Audio play failed, falling back to beeps.");
            }});

            // 2. Browser Voice Alert (Speech Synthesis)
            if ('speechSynthesis' in window) {{
                const msg = new SpeechSynthesisUtterance();
                msg.text = "SECURITY BREACH! EMERGENCY ALERT SENT TO NINE ZERO FIVE EIGHT FOUR ONE SIX NINE THREE FOUR";
                msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }}

            // 3. Fallback: Web Audio API beep pattern (for siren effect)
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function beep(freq, dur, delay) {{
                setTimeout(() => {{
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.frequency.value = freq;
                    osc.type = 'sawtooth';
                    gain.gain.value = 0.5;
                    osc.start();
                    setTimeout(() => osc.stop(), dur);
                }}, delay);
            }}
            // Police siren wig-wag pattern (beeps)
            for(let i = 0; i < 10; i++) {{
                beep(880, 400, i * 900);
                beep(660, 400, i * 900 + 450);
            }}
        </script>
    """, height=0)

def password_gate(gate_name="System"):
    """
    Futuristic password gate.
    Wrong password → Police siren + WhatsApp alert.
    Default password: admin123
    """
    if f"gate_unlocked_{gate_name}" not in st.session_state:
        st.session_state[f"gate_unlocked_{gate_name}"] = False

    if st.session_state[f"gate_unlocked_{gate_name}"]:
        return True

    st.markdown(f"### 🔐 {gate_name} Security Gate")
    password = st.text_input("Enter Dashboard Key:", type="password", key=f"gate_pw_{gate_name}")

    if st.button("UNLOCK SYSTEM", key=f"gate_btn_{gate_name}"):
        if password == DEFAULT_PASSWORD:
            st.session_state[f"gate_unlocked_{gate_name}"] = True
            st.success("✅ Access Granted. Initializing dashboard...")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("🚨 SECURITY PROTOCOL INITIATED.")
            
            # 🔊 Play siren + Browser Voice (10 seconds)
            play_police_siren(10000)
            
            alert_msg = f"⚠️ SECURITY BREACH: Unauthorized access attempt detected on {gate_name}!"
            # We trigger the alerts but don't show individual technical logs to avoid clutter
            send_emergency_sms(alert_msg)
            send_emergency_call()
            send_whatsapp_alert(alert_msg)
            send_telegram_alert(alert_msg)
            send_phone_notification(alert_msg)
            
            st.success("📢 Emergency protocols initiated. Security alerted.")
    
    return False

def check_budget_alarm(total_spent, budget):
    """
    Budget monitor — plays siren + Twilio alert when budget exceeded.
    """
    if total_spent > budget:
        st.error(f"🚨 BUDGET EXCEEDED! Spent ₹{total_spent:,.0f} > Budget ₹{budget:,.0f}")
        
        # Play siren (10 seconds)
        play_police_siren(10000)
        
        if "budget_alert_sent" not in st.session_state:
            msg = f"🚨 BUDGET ALERT: You spent ₹{total_spent:,.2f}, exceeding your budget of ₹{budget:,.2f}!"
            send_emergency_sms(msg)
            send_emergency_call()
            send_whatsapp_alert(msg)
            send_telegram_alert(msg)
            st.session_state["budget_alert_sent"] = True
