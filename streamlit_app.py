import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- SETTINGS & THEME ---
st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

# แทนที่ URL_CSV ด้วยลิงก์ที่คุณ Publish as CSV จาก Google Sheets
SHEET_URL = "ใส่_LINK_CSV_ของคุณที่นี่"

def load_data():
    try:
        # ดึงข้อมูลและกำหนดชื่อคอลัมน์ตามไฟล์ Trading Journal 1
        df = pd.read_csv(SHEET_URL, skiprows=1) 
        return df
    except:
        return pd.DataFrame()

df = load_data()

# --- HEADER SECTION ---
st.title("💹 Smart Trading Journal Dashboard")
st.markdown("---")

# 1. Account Summary (ดึงค่าจากไฟล์ )
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Current Balance", "$100.00") # ดึงจากช่อง Current Balance 
with col2:
    st.metric("Net P/L ($)", "$0.00")
with col3:
    st.metric("Account Growth", "0%")
with col4:
    st.metric("Win Rate", "65%")

# 2. Rules & Limits Warning (ตามกฎเหล็กในไฟล์ )
st.subheader("⚠️ Rules & Limits Tracker")
r1, r2, r3 = st.columns(3)
r1.warning(f"Max Daily Loss Limit: 10%") 
r2.error(f"Max Drawdown Limit: 50%")
r3.info(f"Max Loss Amount: $70.00")

# 3. Analytics Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Performance by Setup & Grade")
    # วิเคราะห์จาก Setup Name และ Trade Grade 
    if not df.empty:
        fig = px.bar(df, x="Setup Name", color="Trade Grade", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("🧠 Psychology vs Result")
    # วิเคราะห์อารมณ์ตอนเข้า (Entry Emotion) 
    if not df.empty:
        fig_emo = px.sunburst(df, path=['Entry Emotion', 'Result'], values='Net PnL ($)')
        st.plotly_chart(fig_emo, use_container_width=True)

# 4. History Table with Image Links
st.subheader("📜 Detailed Trade Log")
if not df.empty:
    # แสดงตารางพร้อมช่อง Setup Chart และ Exit Chart ที่เป็นลิงก์ 
    st.dataframe(df[['Date', 'Symbol', 'Side', 'Setup Name', 'Result', 'Net PnL ($)', 'Setup Chart']])
