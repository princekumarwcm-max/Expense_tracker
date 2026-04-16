import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu

from utils.voice_utils import show_voice_interface
from utils.ocr_utils import show_ocr_page
from utils.gsheet_utils import load_data_from_gsheet, load_yearly_data
from utils.data_utils import filter_old_records
from utils.ui_utils import show_credit_form, show_debit_form, show_summary
from utils.yearly_overview import show_yearly_overview
from utils.monthly_insights import generate_monthly_insights
from utils.weekly_insights import generate_weekly_insights
from utils.filter_data import filter_data
from utils.ai_insights import show_ai_insights
from utils.alerts import send_emergency_call
from utils.alarm_system import check_budget_alarm

from utils.dashboard_styles import apply_dashboard_styles

def run():
    # Inject Professional Styling
    apply_dashboard_styles()
    
    # 📂 Top horizontal menu
    selected = option_menu(
        menu_title=None,
        options=[
            "Credit", "Debit", "Summary", "Scan Receipt",  
            "Voice", "Weekly Insights", "Monthly Insights", 
            "Yearly Overview", "Filter", "AI Insights"
        ],
        icons=[
            "cash", "credit-card", "bar-chart-line", "camera", 
            "mic", "calendar-week", "graph-up", "calendar-range", "search", "robot"
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    # Load and prepare data
    df, sheet, spreadsheet = load_data_from_gsheet()
    df = filter_old_records(df)

    # --- REAL-TIME ALARM ENGINE ---
    budget = st.session_state.get("monthly_budget", 10000)
    total_expenses = abs(df[df['debit'] < 0]['debit'].sum())
    
    # Budget Exceeded Trigger 🚨
    check_budget_alarm(total_expenses, budget)
    
    # High Spending Trigger (e.g. > 2000 in one day) ⚠️
    today_str = datetime.now().strftime("%d-%m-%Y")
    today_spent = abs(df[(df['debit'] < 0) & (df['date'] == today_str)]['debit'].sum())
    if today_spent > 2000:
         st.warning(f"⚠️ High spending detected! You spent ₹{today_spent:,.2f} today.")

    # 📦 Route to selected feature
    if selected == "Credit":
        show_credit_form(df, sheet)
    elif selected == "Debit":
        show_debit_form(df, sheet)
    elif selected == "Summary":
        show_summary(load_yearly_data(spreadsheet))
    elif selected == "Scan Receipt":  # 👈 SIRF EK BAAR
        show_ocr_page(df, sheet)
    elif selected == "Weekly Insights":
        generate_weekly_insights(df)
    elif selected == "Monthly Insights":
        generate_monthly_insights(df)
    elif selected == "Yearly Overview":
        show_yearly_overview(load_yearly_data(spreadsheet))
    elif selected == "Filter":
        filter_data(load_yearly_data(spreadsheet))
    elif selected == "AI Insights":
        show_ai_insights(load_yearly_data(spreadsheet))
    elif selected == "Voice":
        show_voice_interface(df, sheet)