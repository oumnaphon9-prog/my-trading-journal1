import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Pro Trading Journal Dashboard", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .risk-warning { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE (Database Simulation) ---
if 'trades' not in st.session_state:
    st.session_state.trades = pd.DataFrame(columns=[
        'Date', 'Asset', 'Side', 'Entry_Price', 'Exit_Price', 'SL_Price', 'Lot', 
        'Entry_Time', 'Exit_Time', 'Duration', 'Emotion_Entry', 'Emotion_Exit',
        'Setup_Name', 'Setup_Grade', 'Exit_Reason', 'Profit', 'RR_Actual', 'Image_Url'
    ])

if 'account_balance' not in st.session_state:
    st.session_state.account_balance = 10000.0  # เงินเริ่มต้นตัวอย่าง

# --- SIDEBAR: INPUT ZONE ---
with st.sidebar:
    st.header("📥 Log New Trade")
    with st.form("trade_form", clear_on_submit=True):
        asset = st.selectbox("Currency Pair", ["EUR/USD", "GBP/USD", "AUD/USD", "USD/JPY", "USD/CHF"])
        side = st.radio("Side", ["Buy", "Sell"], horizontal=True)
        
        col1, col2 = st.columns(2)
        entry_p = col1.number_input("Entry Price", format="%.5f")
        exit_p = col2.number_input("Exit Price", format="%.5f")
        sl_p = col1.number_input("Stop Loss", format="%.5f")
        lot = col2.number_input("Lot Size", min_value=0.01, step=0.01)
        
        t_entry = st.time_input("Entry Time")
        t_exit = st.time_input("Exit Time")
        
        setup = st.text_input("Setup Name (e.g. Breakout)")
        grade = st.select_slider("Setup Grade", options=["D", "C", "B", "A"])
        
        emo_in = st.selectbox("Emotion (Entry)", ["Calm", "Greedy", "Fear", "Revenge"])
        emo_out = st.selectbox("Emotion (Exit)", ["Satisfied", "Anxious", "Regret"])
        
        exit_res = st.selectbox("Exit Reason", ["Take Profit", "Stop Loss", "Trailing Stop", "Manual Cut"])
        img_url = st.text_input("Chart Image URL")
        
        submit = st.form_submit_button("Add Trade to Journal")
        
        if submit:
            # Simple P/L Calculation (Simplified for demo)
            multiplier = 100000 if "JPY" not in asset else 1000
            diff = (exit_p - entry_p) if side == "Buy" else (entry_p - exit_p)
            profit = diff * lot * multiplier
            
            # RR Calculation
            risk = abs(entry_p - sl_p)
            reward = abs(exit_p - entry_p)
            rr = reward / risk if risk != 0 else 0
            
            # Time Duration
            duration = datetime.combine(datetime.today(), t_exit) - datetime.combine(datetime.today(), t_entry)
            duration_str = str(duration)

            new_data = {
                'Date': datetime.now().strftime("%Y-%m-%d"),
                'Asset': asset, 'Side': side, 'Entry_Price': entry_p, 'Exit_Price': exit_p,
                'SL_Price': sl_p, 'Lot': lot, 'Entry_Time': t_entry, 'Exit_Time': t_exit,
                'Duration': duration_str, 'Emotion_Entry': emo_in, 'Emotion_Exit': emo_out,
                'Setup_Name': setup, 'Setup_Grade': grade, 'Exit_Reason': exit_res,
                'Profit': profit, 'RR_Actual': round(rr, 2), 'Image_Url': img_url
            }
            st.session_state.trades = pd.concat([st.session_state.trades, pd.DataFrame([new_data])], ignore_index=True)
            st.session_state.account_balance += profit
            st.success("Trade Recorded!")

# --- MAIN DASHBOARD ---
st.title("📈 Professional Trading Journal")

# 1. Summary Cards (Top Row)
total_p = st.session_state.trades['Profit'].sum()
win_rate = (len(st.session_state.trades[st.session_state.trades['Profit'] > 0]) / len(st.session_state.trades) * 100) if not st.session_state.trades.empty else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Balance", f"${st.session_state.account_balance:,.2f}")
m2.metric("Total Net P/L", f"${total_p:,.2f}", delta=f"{total_p:,.2f}")
m3.metric("Win Rate", f"{win_rate:.1f}%")
m4.metric("Total Trades", len(st.session_state.trades))

st.divider()

# 2. Risk Management Guard (Alerts)
st.subheader("🛡️ Risk Management Guard")
c1, c2, c3, c4 = st.columns(4)
daily_loss_limit = st.session_state.account_balance * 0.15
max_risk_per_trade = st.session_state.account_balance * 0.10

with c1:
    st.write("Daily Loss Limit (15%)")
    st.progress(0.15) # Example
with c2:
    st.write("Max Drawdown (50%)")
    st.progress(0.1)
with c3:
    st.write("Risk/Trade (10%)")
    st.info(f"Limit: ${max_risk_per_trade:,.2f}")

st.divider()

# 3. Visual Analytics
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Equity Curve")
    if not st.session_state.trades.empty:
        st.session_state.trades['Cumulative_PnL'] = st.session_state.trades['Profit'].cumsum()
        fig_equity = px.line(st.session_state.trades, x=st.session_state.trades.index, y='Cumulative_PnL', 
                             title="Account Growth Over Time", template="plotly_dark")
        st.plotly_chart(fig_equity, use_container_width=True)
    else:
        st.info("No data yet. Start logging trades!")

with col_right:
    st.subheader("🎯 Performance by Asset (Win Rate Curve)")
    if not st.session_state.trades.empty:
        asset_stats = st.session_state.trades.groupby('Asset').apply(
            lambda x: (x['Profit'] > 0).sum() / len(x) * 100
        ).reset_index(name='WinRate')
        fig_asset = px.area(asset_stats, x='Asset', y='WinRate', title="Win Rate per Pair", template="plotly_dark")
        st.plotly_chart(fig_asset, use_container_width=True)

# 4. Deep Dive Analytics
st.divider()
st.subheader("🔍 Deep Dive Analysis")
d1, d2, d3 = st.columns(3)

with d1:
    st.write("**Performance by Setup**")
    if not st.session_state.trades.empty:
        setup_pnl = st.session_state.trades.groupby('Setup_Name')['Profit'].sum()
        st.bar_chart(setup_pnl)

with d2:
    st.write("**Win Rate by Side (Buy vs Sell)**")
    if not st.session_state.trades.empty:
        side_pnl = st.session_state.trades.groupby('Side')['Profit'].count()
        fig_pie = px.pie(values=side_pnl.values, names=side_pnl.index, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with d3:
    st.write("**Average RR Used**")
    if not st.session_state.trades.empty:
        avg_rr = st.session_state.trades['RR_Actual'].mean()
        st.metric("Avg Risk:Reward", f"1:{avg_rr:.2f}")

# 5. Trade History Table
st.divider()
st.subheader("📜 Recent Trade History")
st.dataframe(st.session_state.trades.sort_index(ascending=False), use_container_width=True)

if not st.session_state.trades.empty:
    last_trade = st.session_state.trades.iloc[-1]
    if last_trade['Image_Url']:
        st.subheader("🖼️ Latest Trade Screenshot")
        st.image(last_trade['Image_Url'], caption=f"Setup: {last_trade['Setup_Name']}")
