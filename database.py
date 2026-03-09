import pandas as pd
import os
import streamlit as st
from datetime import datetime

EMP_FILE = "database_employees.csv"
HISTORY_FILE = "history_payslips.csv"

def load_data():
    if "db_employees" not in st.session_state:
        if os.path.exists(EMP_FILE):
            st.session_state.db_employees = pd.read_csv(EMP_FILE, encoding='utf-8-sig')
        else:
            st.session_state.db_employees = pd.DataFrame(columns=["รหัสพนักงาน", "ชื่อ-นามสกุล", "ตำแหน่ง", "แผนก", "ฐานเงินเดือน"])
            
    if "db_history" not in st.session_state:
        if os.path.exists(HISTORY_FILE):
            st.session_state.db_history = pd.read_csv(HISTORY_FILE, encoding='utf-8-sig')
        else:
            st.session_state.db_history = pd.DataFrame(columns=["วันที่", "เลขที่สลิป", "ชื่อพนักงาน", "ยอดสุทธิ"])

def generate_payslip_no():
    today_str = datetime.now().strftime('%Y%m')
    prefix = f"PS-{today_str}"
    
    if st.session_state.db_history.empty:
        return f"{prefix}-001"
        
    hist_df = st.session_state.db_history.copy()
    matched_docs = hist_df[hist_df['เลขที่สลิป'].str.startswith(prefix, na=False)]
    
    if matched_docs.empty:
        return f"{prefix}-001"
    else:
        last_no = matched_docs['เลขที่สลิป'].sort_values().iloc[-1]
        last_run = int(last_no.split('-')[-1])
        return f"{prefix}-{last_run + 1:03d}"