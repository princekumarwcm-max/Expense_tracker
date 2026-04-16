# utils/voice_utils.py

import streamlit as st
import re
import pandas as pd
from datetime import datetime
import tempfile
import numpy as np
import os
import time

# ============================================
# WHISPER INIT (Cached) — lazy import
# ============================================
@st.cache_resource
def load_whisper_model():
    """Load Whisper model (cached) — lazy import so app starts without whisper"""
    try:
        import whisper
        model = whisper.load_model("base", device="cpu")  # force CPU for stability
        return model, None
    except ImportError:
        return None, "Whisper not installed. Run: pip install openai-whisper"
    except Exception as e:
        return None, str(e)

# ============================================
# RECORD AUDIO FROM MICROPHONE
# ============================================
def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone"""
    try:
        import sounddevice as sd
        st.info(f"🎤 Recording for {duration} seconds... Speak now!")
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        return recording.flatten(), sample_rate

    except ImportError:
        st.error("❌ sounddevice not installed. Run: pip install sounddevice")
        return None, None
    except Exception as e:
        st.error(f"Microphone error: {e}")
        return None, None

# ============================================
# TRANSCRIBE WITH WHISPER
# ============================================
def transcribe_audio(audio_data, sample_rate, model):
    """Convert audio to text bypassing FFmpeg"""
    import numpy as np
    
    if audio_data is None or model is None:
        return None

    try:
        # Convert np.int16 to np.float32 which whisper natively expects
        audio_float32 = audio_data.astype(np.float32) / 32768.0
        
        # Bypass ffmpeg directly
        result = model.transcribe(audio_float32)
        return result["text"].strip()

    except Exception as e:
        st.error(f"Transcription error: {e}")
        return None

# ============================================
# NLP PARSER  —  BUG FIX #2: Better credit detection
# ============================================
def parse_natural_command(text):
    text_lower = text.lower().strip()

    # Amount
    amounts = re.findall(r'(\d+(?:\.\d+)?)', text_lower)
    amount = float(amounts[0]) if amounts else None

    # ✅ FIX: Added more credit phrases including "given me", "add it into credit", etc.
    credit_keywords = [
        'salary', 'mila', 'aaya', 'income', 'credited', 'received', 'refund',
        'bonus', 'deposit', 'given me', 'gave me', 'credit', 'add it into my credit',
        'credit up', 'credit amount', 'into credit', 'add to credit', 'added to credit',
        'earning', 'earned', 'payment received', 'got paid', 'transferred to me'
    ]
    debit_keywords = [
        'kharcha', 'gaya', 'spent', 'paid', 'bill', 'purchase', 'petrol',
        'shopping', 'food', 'expense', 'debit', 'debited', 'charged', 'bought'
    ]

    is_credit = any(kw in text_lower for kw in credit_keywords)
    is_debit = any(kw in text_lower for kw in debit_keywords)

    if is_credit and not is_debit:
        trans_type = "credit"
    elif is_debit and not is_credit:
        trans_type = "debit"
    else:
        # ✅ FIX: If both or neither match, check credit first before defaulting to debit
        trans_type = "credit" if is_credit else "debit"

    # Category
    categories = {
        "Food": ['khana', 'food', 'restaurant', 'lunch', 'dinner'],
        "Shopping": ['shopping', 'amazon', 'flipkart', 'cloth', 'shoe'],
        "Travel": ['travel', 'cab', 'ola', 'uber', 'bus', 'train'],
        "Petrol": ['petrol', 'diesel', 'fuel'],
        "Bills": ['bill', 'electricity', 'wifi', 'recharge'],
        "Entertainment": ['movie', 'netflix', 'party'],
        "Self Care": ['gym', 'doctor', 'medicine'],
        "Salary": ['salary', 'income', 'given me', 'gave me'],
        "Side Income": ['bonus', 'gift', 'earned', 'earning']
    }

    detected_category = "Other"
    for cat, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            detected_category = cat
            break

    # Details — remove the raw number tokens
    details = text_lower
    for word in amounts:
        details = details.replace(word, "")

    return {
        'amount': amount,
        'type': trans_type,
        'category': detected_category,
        'details': details.strip()
    }

# ============================================
# MAIN VOICE INTERFACE  —  BUG FIX #1: session_state for parsed data + confirm button
# ============================================
def show_voice_interface(df, sheet):
    st.markdown("# 🎤 Smart Voice Assistant")
    st.markdown("---")

    model, error = load_whisper_model()
    if error:
        st.error(f"Whisper load failed: {error}")
        return

    # ✅ FIX: Initialize all required session_state keys
    if 'voice_mode' not in st.session_state:
        st.session_state.voice_mode = False
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = None
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎤 Start Voice", type="primary", use_container_width=True):
            st.session_state.voice_mode = True

    with col2:
        if st.button("⏹️ Stop Voice", use_container_width=True):
            st.session_state.voice_mode = False
            st.session_state.parsed_data = None
            st.session_state.transcribed_text = None

    if st.session_state.voice_mode:
        # ✅ Add awesome AI Animation for voice mode
        st.markdown("""
            <style>
            .pulse-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 20px 0;
            }
            .pulse-circle {
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
                border-radius: 50%;
                box-shadow: 0 0 0 0 rgba(79, 172, 254, 0.7);
                animation: pulse 1.5s infinite;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 40px;
            }
            @keyframes pulse {
                0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(79, 172, 254, 0.7); }
                70% { transform: scale(1); box-shadow: 0 0 0 30px rgba(79, 172, 254, 0); }
                100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(79, 172, 254, 0); }
            }
            </style>
            <div class="pulse-container">
                <div class="pulse-circle">🤖🎤</div>
            </div>
            <div style="text-align:center; color:#00f2fe; font-weight:bold; font-size:1.2rem; margin-bottom:15px;">
                Voice Mode ACTIVE
            </div>
        """, unsafe_allow_html=True)

        duration = st.slider(
            "Recording duration (seconds)",
            min_value=5,
            max_value=30,
            value=10
        )

        if st.button("🔴 Speak Now", type="primary", use_container_width=True):
            audio_data, sample_rate = record_audio(duration)

            if audio_data is not None:
                with st.spinner("🔍 Processing..."):
                    text = transcribe_audio(audio_data, sample_rate, model)

                    if text:
                        parsed = parse_natural_command(text)
                        if parsed['amount'] is None:
                            st.warning("❌ Amount not detected. Please try again.")
                        else:
                            # ✅ FIX: Store parsed result in session_state so it survives re-runs
                            st.session_state.transcribed_text = text
                            st.session_state.parsed_data = parsed
                    else:
                        st.warning("No speech detected. Please try again.")
            else:
                st.error("Microphone issue. Check your microphone settings.")

    # ✅ FIX: Show parsed result + Confirm button OUTSIDE the "Speak Now" block
    #         so it persists across Streamlit re-runs
    if st.session_state.parsed_data is not None:
        st.markdown("---")
        st.info(f"📝 You said: **{st.session_state.transcribed_text}**")

        parsed = st.session_state.parsed_data

        # Show detected type with colour
        type_color = "green" if parsed['type'] == 'credit' else "red"
        st.markdown(
            f"**Type detected:** <span style='color:{type_color}; font-weight:bold;'>"
            f"{parsed['type'].upper()}</span>",
            unsafe_allow_html=True
        )
        st.json(parsed)

        # ✅ FIX: Allow user to override type if AI got it wrong
        override_type = st.radio(
            "Correct the type if wrong:",
            ["credit", "debit"],
            index=0 if parsed['type'] == 'credit' else 1,
            horizontal=True,
            key="type_override"
        )
        st.session_state.parsed_data['type'] = override_type

        # ✅ FIX: Confirm button is now at the TOP LEVEL — not nested inside another button
        if st.button("✅ Confirm Entry", type="primary"):
            date = datetime.now().strftime('%d-%m-%Y')
            month = datetime.now().strftime('%B')

            final = st.session_state.parsed_data

            if final['type'] == 'credit':
                new_row = {
                    'date': date,
                    'month': month,
                    'credit': final['amount'],
                    'credit_details': final['details'],
                    'debit': 0,
                    'debit_details': 'NA',
                    'category': final['category']
                }
            else:
                new_row = {
                    'date': date,
                    'month': month,
                    'credit': 0,
                    'credit_details': 'NA',
                    'debit': -final['amount'],
                    'debit_details': final['details'],
                    'category': final['category']
                }

            from utils.gsheet_utils import update_data_to_gsheet
            new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            update_data_to_gsheet(sheet, new_df)

            # ✅ FIX: Clear session_state after saving so form resets
            st.session_state.parsed_data = None
            st.session_state.transcribed_text = None

            st.success("✅ Transaction saved successfully!")
            st.balloons()
            time.sleep(1.5)
            st.rerun()


    # Fallback manual input
    st.markdown("---")
    manual_text = st.text_input("✍️ Or type manually:")

    if st.button("Process Text"):
        if manual_text:
            result = parse_natural_command(manual_text)
            st.session_state.transcribed_text = manual_text
            st.session_state.parsed_data = result
            st.rerun()