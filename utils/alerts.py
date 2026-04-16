import os
import streamlit as st
from twilio.rest import Client
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# Safe Secrets Access
try:
    TWILIO_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID", "PASTE_YOUR_SID_HERE")
    TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "PASTE_YOUR_TOKEN_HERE")
    # If the user mistakenly put their own number in the TWILIO_PHONE_NUMBER field, we show a warning
    TWILIO_PHONE_NUMBER = st.secrets.get("TWILIO_PHONE_NUMBER", "+12025550111")
except Exception:
    TWILIO_ACCOUNT_SID = "PASTE_YOUR_SID_HERE"
    TWILIO_AUTH_TOKEN = "PASTE_YOUR_TOKEN_HERE"
    TWILIO_PHONE_NUMBER = "+12025550111"

TARGET_PHONE_NUMBER = "+919058416934" 

# Safety Check: If From and To are the same, Twilio fails. 
# Also, most users don't have a purchased Twilio number yet and try using their own.
if TWILIO_PHONE_NUMBER == TARGET_PHONE_NUMBER or TWILIO_PHONE_NUMBER.startswith("+91"):
    # Fallback to a generic placeholder or the user's previously working number if any
    # Without a REAL Twilio purchased number, this will likely give a 400 error.
    pass

def start_background_scheduler():
    """Starts the background scheduler for periodic threshold checks."""
    if "scheduler_started" not in st.session_state:
        try:
            scheduler = BackgroundScheduler()
            # Add a heartbeat job or a placeholder for background monitoring
            scheduler.add_job(lambda: print(f"Background Guardian Heartbeat: {datetime.now()}"), 'interval', hours=1)
            scheduler.start()
            st.session_state["scheduler_started"] = True
            return True
        except Exception as e:
            print(f"Scheduler failed: {e}")
    return False

def generate_smart_alarm(df, budget=10000):
    """
    Interface for AI Insights page.
    Generates a smart message based on data.
    """
    from utils.llm_insights import get_smart_alerts
    return get_smart_alerts(df, budget)

def send_sms_alert(message="🚨 High spending detected in your Expense Tracker!"):
    """Alias for send_emergency_sms to maintain compatibility with AI Insights."""
    return send_emergency_sms(message)

def send_emergency_call():
    """Triggers a Twilio phone call with a specific security message requested by the user."""
    # Use global variables
    global TWILIO_PHONE_NUMBER
    
    print(f"DEBUG: Attempting Twilio Call from {TWILIO_PHONE_NUMBER} to {TARGET_PHONE_NUMBER}")
    
    # Auto-fix: If user put their own number as the sender, use a dummy fallback
    current_from = TWILIO_PHONE_NUMBER
    if current_from == TARGET_PHONE_NUMBER or current_from.startswith("+91"):
        current_from = "+12025550111" # Dummy fallback
    
    # Validation
    if "PASTE" in TWILIO_ACCOUNT_SID:
        return "❌ Error: Twilio SID is missing. Please add it to secrets.toml."


    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Custom message as requested by the user
        msg_text = "Attention! This is a security alert from your Expense Tracker. Someone is attempting to access or tampering with your expenses. Please check your dashboard immediately."
        
        call = client.calls.create(
            twiml=f'<Response><Say voice="alice" language="en-US">{msg_text}</Say></Response>',
            to=TARGET_PHONE_NUMBER,
            from_=current_from
        )

        return f"🚨 Security Call triggered to {TARGET_PHONE_NUMBER}"
    except Exception as e:
        print(f"Twilio Call Error: {e}")
        error_msg = str(e)
        if "not a Twilio phone number" in error_msg:
            return "❌ Twilio Error: The 'From' number is not a valid Twilio Virtual Number. You must purchase a number from Twilio to make calls."
        if "not yet verified" in error_msg:
            return "❌ Twilio Error: The target number is not verified in your Twilio Console."
        return f"Failed to place Twilio Call: {error_msg}"

def send_emergency_sms(message="🚨 High spending detected in your Expense Tracker!"):
    """Sends an emergency SMS."""
    if "PASTE" in TWILIO_ACCOUNT_SID: return "❌ Twilio not configured."
    
    # Auto-fix: fallback if needed
    current_from = TWILIO_PHONE_NUMBER
    if current_from == TARGET_PHONE_NUMBER or current_from.startswith("+91"):
        current_from = "+12025550111"

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            to=TARGET_PHONE_NUMBER,
            from_=current_from
        )
        return f"📲 Alert SMS sent to {TARGET_PHONE_NUMBER}"
    except Exception as e:
        print(f"Twilio SMS Error: {e}")
        return f"Failed to send SMS: {e}"


def send_whatsapp_alert(message="🚨 High spending detected in your Expense Tracker!"):
    """
    Sends a WhatsApp message via Twilio Sandbox.
    """
    if "PASTE" in TWILIO_ACCOUNT_SID: return "❌ Twilio not configured."
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        whatsapp_from = "whatsapp:+14155238886"  # Official Twilio WhatsApp Sandbox (free)
        whatsapp_to   = f"whatsapp:{TARGET_PHONE_NUMBER}"
        msg = client.messages.create(
            body=message,
            from_=whatsapp_from,
            to=whatsapp_to
        )
        return f"💬 WhatsApp Alert sent to {TARGET_PHONE_NUMBER}"
    except Exception as e:
        return f"WhatsApp Alert failed: {e}"

def send_telegram_alert(message="🚨 High spending detected!"):
    """Sends a FREE Telegram alert."""
    import requests
    try:
        token = st.secrets.get("TELEGRAM_BOT_TOKEN")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
        # Guard against placeholder
        if not token or not chat_id or "PASTE" in token: 
            return "❌ Telegram setup required (Bot Token is missing)."
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, data={"chat_id": chat_id, "text": message})
        return f"✈️ Telegram sent" if response.status_code == 200 else f"❌ Telegram failed: {response.text}"
    except Exception as e: return f"❌ Telegram error: {e}"

def send_phone_notification(message="🚨 SECURITY ALERT!"):
    """
    Sends a 100% FREE, ZERO-CONFIG alert to your phone via ntfy.sh.
    """
    import requests
    topic = "prince_expense_9058"
    try:
        requests.post(f"https://ntfy.sh/{topic}", 
                      data=message.encode('utf-8'),
                      headers={"Title": "Expense Tracker Alert", "Priority": "high", "Tags": "rotating_light,warning"})
        return f"🔔 Instant Alert sent to ntfy.sh/{topic}"
    except Exception as e:
        return f"❌ Notification failed: {e}"

def trigger_twilio_verification():
    """
    Attempts to trigger a verification call/SMS via Twilio.
    Note: For trial accounts, you usually have to do this manually in the console.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # This will attempt to add the number to Verified Caller IDs
        # Twilio will call the number and provide a 6-digit code.
        validation_request = client.validation_requests.create(
            friendly_name='My Home Phone',
            phone_number=TARGET_PHONE_NUMBER
        )
        return f"📞 Twilio is calling you now! Please listen for the 6-digit code and enter it in your Twilio Console."
    except Exception as e:
        return f"❌ Verification Trigger Failed: {e}. Please verify manually at: https://www.twilio.com/console/phone-numbers/verified"


