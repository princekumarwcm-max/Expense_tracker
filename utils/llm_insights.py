import streamlit as st
from openai import OpenAI
import pandas as pd
from datetime import datetime

# xAI Grok Integration Logic

def get_xai_client():
    if 'xai_api_key' not in st.session_state or not st.session_state['xai_api_key']:
        st.warning("Please configure your xAI (Grok) API Key in the sidebar to use True AI Coach.")
        return None
    try:
        # xAI is OpenAI compatible
        client = OpenAI(
            api_key=st.session_state['xai_api_key'],
            base_url="https://api.xai.com/v1",
        )
        return client
    except Exception as e:
        st.error(f"Error configuring xAI API: {e}")
        return None

def _get_df_summary(df):
    """Summarize data to feed to prompt"""
    if df.empty:
        return 0, 0, {}
    
    total_income = df[df['credit'] > 0]['credit'].sum()
    total_expenses = abs(df[df['debit'] < 0]['debit'].sum())
    
    # Calculate category spending
    expense_df = df[df['debit'] < 0].copy()
    expense_df['abs_debit'] = abs(expense_df['debit'])
    category_summary = expense_df.groupby('category')['abs_debit'].sum().to_dict()
    
    return total_income, total_expenses, category_summary

def run_financial_coach(df):
    client = get_xai_client()
    if not client: return
    
    total_income, total_expenses, category_summary = _get_df_summary(df)
    
    # Formatting category breakdown
    cat_str = "\n".join([f"- {k}: ₹{v:,.2f}" for k, v in category_summary.items()])
    
    prompt = f"""You are an intelligent financial coach AI powered by Grok.
Analyze the user's expense data and provide helpful advice.

User Data:
Income: ₹{total_income}
Total Expenses: ₹{total_expenses}

Category Breakdown:
{cat_str}

Output format:
✔ Good habits:
❌ Problem areas:
📊 Insights:
💡 Suggestions:
"""
    
    with st.spinner("Grok is analyzing your finances..."):
        try:
            completion = client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are a professional financial coach."},
                    {"role": "user", "content": prompt},
                ],
            )
            st.markdown(completion.choices[0].message.content)
        except Exception as e:
            st.error(f"xAI API Error: {e}")

def run_financial_prediction(df, budget=10000):
    client = get_xai_client()
    if not client: return
    
    _, total_expenses, _ = _get_df_summary(df)
    days_passed = min(datetime.now().day, 30)
    
    prompt = f"""Analyze current spending and predict future expenses.
Current Spent: ₹{total_expenses}
Days Passed: {days_passed}
Monthly Budget: ₹{budget}

Output format:
📊 Average daily spend:
🔮 Predicted monthly spend:
⚠️ Warning (if any):
💡 Suggestion:
"""
    with st.spinner("Predicting your monthly spending..."):
        try:
            completion = client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are a financial prediction expert."},
                    {"role": "user", "content": prompt},
                ],
            )
            st.markdown(completion.choices[0].message.content)
        except Exception as e:
            st.error(f"xAI API Error: {e}")

def get_smart_alerts(df, budget=10000):
    client = get_xai_client()
    if not client: return "⚠️ xAI Client not configured."
    
    _, total_expenses, _ = _get_df_summary(df)
    
    today_spent = 0
    if not df.empty and 'date' in df.columns:
        today_str = datetime.now().strftime("%d-%m-%Y")
        today_spent = abs(df[(df['debit'] < 0) & (df['date'] == today_str)]['debit'].sum())

    prompt = f"""Generate 1-2 short, engaging smart alerts (with emojis).
Budget: ₹{budget}
Spent: ₹{total_expenses}
Today Spending: ₹{today_spent}
"""
    try:
        completion = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You generate short, helpful financial alerts."},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ xAI Alert Error: {e}"

def run_emotional_spending_check(df):
    client = get_xai_client()
    if not client: return
    
    if df.empty: return
        
    expense_df = df[df['debit'] < 0].copy()
    transactions = []
    for _, row in expense_df.head(30).iterrows():
        transactions.append(f"{row.get('date')} - {row.get('category')} - ₹{abs(row.get('debit'))}")
        
    tx_str = "\n".join(transactions)
    
    prompt = f"""Detect emotional or impulsive spending patterns from these transactions:
{tx_str}

Output:
🧠 Behavior Insight:
⚠️ Risk:
💡 Advice:
"""
    with st.spinner("Analyzing your spending behavior..."):
        try:
            completion = client.chat.completions.create(
                model="grok-beta",
                messages=[
                    {"role": "system", "content": "You are a behavioral economist analyzing spending habits."},
                    {"role": "user", "content": prompt},
                ],
            )
            st.markdown(completion.choices[0].message.content)
        except Exception as e:
            st.error(f"xAI API Error: {e}")
