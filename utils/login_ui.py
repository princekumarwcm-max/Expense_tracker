import streamlit as st

def render_login_page():

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    st.markdown("<h1 style='text-align:center;'>💸 EXPENSE TRACKER</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🔐 SECURE ACCESS</h3>", unsafe_allow_html=True)

    email = st.text_input("RECOGNITION ID (EMAIL)")
    password = st.text_input("CRYPTOGRAPHIC KEY", type="password")

    if st.button("LOGIN"):
        if email == "princekumar.wcm@gmail.com" and password == "admin123":
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = email
            st.success("✅ ACCESS GRANTED")
            st.rerun()
        else:
            st.error("❌ INVALID CREDENTIALS")
