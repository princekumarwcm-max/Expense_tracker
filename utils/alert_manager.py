import streamlit as st
import pandas as pd
from datetime import datetime

def check_in_app_alerts(df, budget):
    """
    Analyzes current data and returns a list of alert dicts:
    {'type': 'error'|'warning'|'success', 'msg': str, 'sound': str}
    """
    alerts = []
    today_str = datetime.today().strftime('%d-%m-%Y')
    
    if df is None or df.empty:
        # Daily Reminder
        alerts.append({
            'type': 'warning',
            'msg': "⏰ Add today's expense",
            'sound': 'warning'
        })
        return alerts

    # 1. Daily Reminder Check
    today_data = df[df['date'] == today_str]
    if today_data.empty:
        alerts.append({
            'type': 'warning',
            'msg': "⏰ Add today's expense",
            'sound': 'warning'
        })

    # 2. Budget Logic
    total_debit = abs(df['debit'].sum())
    usage_pct = (total_debit / budget) * 100 if budget > 0 else 0

    if usage_pct >= 100:
        alerts.append({
            'type': 'error',
            'msg': f"🚫 Budget exceeded! ({usage_pct:.1f}%)",
            'sound': 'alarm'
        })
    elif usage_pct >= 80:
        alerts.append({
            'type': 'warning',
            'msg': f"⚠️ You used 80% of your budget! ({usage_pct:.1f}%)",
            'sound': 'warning'
        })

    # 3. High Spending Check (Anomaly)
    if not today_data.empty:
        today_spend = abs(today_data['debit'].sum())
        # Calculate last 7 days average
        past_data = df[df['date'] != today_str]
        if not past_data.empty:
            avg_daily = abs(past_data.groupby('date')['debit'].sum().mean())
            if today_spend > (avg_daily * 2) and today_spend > 500:
                alerts.append({
                    'type': 'error',
                    'msg': "💸 High spending detected today!",
                    'sound': 'error'
                })

    return alerts

def render_in_app_alerts(alerts):
    """Renders the alerts as beautiful floating slide-ins."""
    if not alerts:
        return

    # In-app alerts specific CSS
    st.markdown("""
        <style>
            .in_app_alert_container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                pointer-events: none;
            }
            .in_app_alert {
                padding: 15px 25px;
                border-radius: 12px;
                backdrop-filter: blur(10px);
                font-family: 'Orbitron', sans-serif;
                font-size: 0.8rem;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                animation: slide-in-alert 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
                border-left: 5px solid transparent;
                color: #fff;
            }
            .ia-error { background: rgba(239, 68, 68, 0.8); border-left-color: #ef4444; }
            .ia-warning { background: rgba(234, 179, 8, 0.8); border-left-color: #eab308; }
            .ia-success { background: rgba(34, 197, 94, 0.8); border-left-color: #22c55e; }

            @keyframes slide-in-alert {
                from { transform: translateX(120%) scale(0.8); opacity: 0; }
                to { transform: translateX(0) scale(1); opacity: 1; }
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="in_app_alert_container">', unsafe_allow_html=True)
    for alert in alerts:
        css_class = f"ia-{alert['type']}"
        st.markdown(f'<div class="in_app_alert {css_class}">{alert["msg"]}</div>', unsafe_allow_html=True)
        # Play sound using the already injected JS engine (we'll ensure it's in dashboard_styles)
        st.markdown(f'<script>if(window.playSound) {{ playSound("{alert["sound"]}"); }}</script>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
