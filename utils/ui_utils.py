import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils.data_utils import get_current_date_month, build_summary_df
from utils.gsheet_utils import update_data_to_gsheet
from utils.yearly_overview import plot_category_chart, apply_custom_style_row
from utils.alert_manager import check_in_app_alerts, render_in_app_alerts

# 🔁 Unified form logic
def _append_and_update(df, sheet, new_row, success_msg):
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    update_data_to_gsheet(sheet, df)
    st.toast(success_msg, icon="✅")
    time.sleep(1)
    st.rerun()

# ➕ Credit Entry Form
def show_credit_form(df, sheet):
    category_options = ["Salary", "Side Income", "Udemy Income","Youtube Earning" ]

    st.markdown('<div class="st-emotion-cache-1r6slb0">', unsafe_allow_html=True)
    st.markdown("### 📥 Add Credit (Income)")
    with st.form("credit_form", clear_on_submit=True):
        amount = st.number_input("Enter credited amount:", min_value=0, key="credit_amount")
        category = st.selectbox("Income Type:", category_options)
        source = st.text_input("Source description:")
        if st.form_submit_button("INITIALIZE CREDIT UPLINK") and amount > 0:
            date, month = get_current_date_month()
            new_row = {
                'date': date,
                'month': month,
                'credit': amount,
                'credit_details': source or 'NA',
                'debit': 0,
                'debit_details': 'NA',
                'category': category
            }
            _append_and_update(df, sheet, new_row, "Credit details added successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

# ➖ Debit Entry Form
def show_debit_form(df, sheet):
    category_options = [
        "Today's expense ", "Weekend expense", "Financial Support to Family",
        "Shopping", "Petrol", "Self Care", "Recharge", "SIP",
        "Veggies,Gas cylinder and Dmart", "Rent,Maid & Electricity bills",
        "Pune & village expense", "Travelling expense", "Trips", "Other"
    ]

    st.markdown('<div class="st-emotion-cache-1r6slb0" style="border-left: 4px solid #ff3131;">', unsafe_allow_html=True)
    st.markdown("### 📤 Add Debit (Expense)")
    with st.form("debit_form", clear_on_submit=True):
        amount = st.number_input("Enter debited amount:", min_value=0, key="debit_amount")
        category = st.selectbox("Expense Type:", category_options)
        note = st.text_input("Details/Source:")
        if st.form_submit_button("PROCESS DEBIT TRANSACTION") and amount > 0:
            date, month = get_current_date_month()
            new_row = {
                'date': date,
                'month': month,
                'credit': 0,
                'credit_details': 'NA',
                'debit': -abs(amount),
                'debit_details': note or 'NA',
                'category': category
            }
            _append_and_update(df, sheet, new_row, "Debit details added successfully!")
    st.markdown('</div>', unsafe_allow_html=True)
            

# 📊 Monthly Summary + Visuals
def show_summary(yearly_data):
    # Extract available years from the keys
    years = []
    for key in yearly_data.keys():
        year = key.split('-')[-1]
        if year.isdigit():
            years.append(int(year))
    years = sorted(years, reverse=True)

    if not years:
        st.warning("No data available.")
        return

    # --- 🔥 IN-APP SMART ALERTS ---
    budget = st.session_state.get("monthly_budget", 10000)
    current_year = datetime.now().year
    
    # Resolve exact key by user prefix dynamically
    latest_key = next((k for k in yearly_data if k.endswith(f"-{current_year}")), None)
    latest_df_raw = yearly_data.get(latest_key) if latest_key else None
    if latest_df_raw is not None:
        in_app_alerts = check_in_app_alerts(latest_df_raw, budget)
        render_in_app_alerts(in_app_alerts)

    st.markdown("## 🤖 AI Financial Coach Insights")
    if 'gemini_api_key' in st.session_state and st.session_state['gemini_api_key']:
        from utils.llm_insights import get_smart_alerts
        # We need ALL data for accurate total spending, but we can just use the latest year df
        latest_key_llm = next((k for k in yearly_data if k.endswith(f"-{years[0]}")), None)
        latest_df = yearly_data.get(latest_key_llm) if latest_key_llm else pd.DataFrame()
        budget = st.session_state.get("monthly_budget", 10000)
        alerts = get_smart_alerts(latest_df, budget=budget)
        if alerts:
            st.info(alerts)
    else:
        st.info("Configure your Gemini API key in the sidebar for 🔔 Smart Alerts.")
        
    st.markdown("---")

    # Select year dropdown (default latest year)
    selected_year = st.selectbox("Select Year:", years, index=0)
    sheet_key = next((k for k in yearly_data if k.endswith(f"-{selected_year}")), None)

    if not sheet_key or sheet_key not in yearly_data:
        st.warning("Data for the selected year is not available.")
        return

    df = yearly_data[sheet_key]
    df = build_summary_df(df)  # Now passing the correct DataFrame

    df['month'] = pd.to_datetime(df['month'], format='%B', errors='coerce')
    df = df.dropna(subset=['month']).sort_values('month', ascending=False)

    from utils.dashboard_styles import render_metric_card

    final_saving = 0
    total_by_category = {}

    for month in df['month'].dt.strftime('%B').unique():
        st.markdown(f"### 📅 {month}")
        month_df = df[df['month'].dt.strftime('%B') == month]

        credit = month_df.query("amount > 0")['amount'].sum()
        debit = abs(month_df.query("amount < 0")['amount'].sum())
        savings = credit - debit
        final_saving += savings

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            render_metric_card("Monthly Income", f"₹{credit:,.0f}", delta="Income Flow", delta_color="normal")
        with col_m2:
            render_metric_card("Monthly Expenses", f"₹{debit:,.0f}", delta="Spend Flow", delta_color="inverse")
        with col_m3:
            render_metric_card("Net Savings", f"₹{savings:,.0f}", delta="Net Balance", delta_color="normal" if savings >= 0 else "inverse")

        for cat in month_df['category'].dropna().unique():
            amt = abs(month_df[month_df['category'] == cat]['amount'].sum())
            total_by_category[cat] = total_by_category.get(cat, 0) + amt

        display_df = month_df[['date', 'amount', 'details', 'category']].sort_values('date')
        st.dataframe(display_df.style.apply(apply_custom_style_row, axis=1), use_container_width=True)
        plot_category_chart(month_df, debit)
        st.markdown("---")

    st.markdown('<div class="st-emotion-cache-1r6slb0" style="margin-top: 40px;">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Annual Performance</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        render_metric_card("Total Yearly Savings", f"₹{final_saving:,.0f}", delta="Year-to-Date", delta_color="normal" if final_saving >= 0 else "inverse")
    st.markdown('</div>', unsafe_allow_html=True)


    st.markdown('<div class="st-emotion-cache-1r6slb0" style="margin-top: 40px; border-left: 4px solid #ff3131;">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🚨 Danger Zone: Secure Data Wipe</h3>", unsafe_allow_html=True)
    st.error("Warning: This action will permanently delete all your expense and income history.")
    
    if st.button("🗑️ CLEAR ALL TRANSACTION HISTORY", key="wipe_btn"):
        st.session_state["confirm_wipe"] = True
        
    if st.session_state.get("confirm_wipe"):
        st.warning("⚠️ PROCEED WITH CAUTION: Are you absolutely sure? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ YES, DELETE EVERYTHING"):
                from utils.gsheet_utils import wipe_all_data
                if wipe_all_data(yearly_data[sheet_key]):
                    st.success("System wiped successfully. Syncing...")
                    st.markdown('<script>window.playSound("success");</script>', unsafe_allow_html=True)
                    st.session_state["confirm_wipe"] = False
                    time.sleep(2)
                    st.rerun()
        with c2:
            if st.button("❌ CANCEL"):
                st.session_state["confirm_wipe"] = False
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
