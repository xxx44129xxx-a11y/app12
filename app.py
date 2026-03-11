import streamlit as st
import pandas as pd
from datetime import datetime
import os
from database import load_data, generate_payslip_no, HISTORY_FILE
EMP_FILE = "database_employees.csv"
from generate_payslip_pdf import generate_payslip_pdf_bytes

st.set_page_config(page_title="ระบบสลิปเงินเดือน", layout="wide")
load_data()

# ตรวจสอบคอลัมน์ใน db_employees ให้ครบถ้วน
if st.session_state.db_employees.empty or "ชื่อ-นามสกุล" not in st.session_state.db_employees.columns:
    st.session_state.db_employees = pd.DataFrame(columns=["รหัสพนักงาน", "ชื่อ-นามสกุล", "ตำแหน่ง", "แผนก", "ฐานเงินเดือน"])

st.title("💸 ระบบออกใบแจ้งเงินเดือน")

tab1, tab2, tab3 = st.tabs(["สร้างสลิปเงินเดือน", "ประวัติการออกสลิป", "ฐานข้อมูลพนักงาน"])

with tab1:
    # --- ส่วนการดึงข้อมูลที่จดจำไว้ ---
    st.subheader("1. เลือกหรือกรอกข้อมูลพนักงาน")
    emp_list = st.session_state.db_employees["ชื่อ-นามสกุล"].tolist()
    
    # ตัวเลือกการกรอกชื่อ
    name_option = st.selectbox("ค้นหารายชื่อพนักงานที่บันทึกไว้ (หรือพิมพ์ชื่อใหม่ด้านล่าง)", ["-- พิมพ์ชื่อใหม่ --"] + emp_list)
    
    # ดึงข้อมูลเดิมมาใส่ใน Default Value ถ้ามีการเลือกชื่อ
    saved_data = {}
    if name_option != "-- พิมพ์ชื่อใหม่ --":
        row = st.session_state.db_employees[st.session_state.db_employees["ชื่อ-นามสกุล"] == name_option].iloc[0]
        saved_data = {
            "id": row.get("รหัสพนักงาน", ""),
            "name": row.get("ชื่อ-นามสกุล", ""),
            "pos": row.get("ตำแหน่ง", ""),
            "dept": row.get("แผนก", ""),
            "salary": float(row.get("ฐานเงินเดือน", 0))
        }

    with st.form("payslip_form"):
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1: emp_id = st.text_input("รหัสพนักงาน", value=saved_data.get("id", ""))
        with col_e2: emp_name = st.text_input("ชื่อ-นามสกุล", value=saved_data.get("name", "") if name_option == "-- พิมพ์ชื่อใหม่ --" else name_option)
        with col_e3: position = st.text_input("ตำแหน่ง", value=saved_data.get("pos", ""))
        with col_e4: department = st.text_input("แผนก", value=saved_data.get("dept", ""))

        col_d1, col_d2 = st.columns(2)
        with col_d1: pay_date = st.text_input("วันที่จ่าย (เช่น 31 มี.ค. 2569)", value=datetime.now().strftime("%d %b %Y"))
        with col_d2: period = st.text_input("งวดที่ (เช่น 03/2569)")

        st.markdown("---")
        st.subheader("2. รายได้ และ OT")
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1: 
            salary = st.number_input("เงินเดือนพื้นฐาน", min_value=0.0, step=1000.0, value=saved_data.get("salary", 0.0))
            other_income = st.number_input("รายได้อื่นๆ / โบนัส", min_value=0.0, step=500.0)
        with col_i2:
            daily_wage = st.number_input("รายได้/วัน (สำหรับคิด OT)", min_value=0.0, step=100.0, value=salary/30 if salary > 0 else 0.0)
            ot_hours = st.number_input("จำนวนชั่วโมง OT", min_value=0.0, step=1.0)
        with col_i3:
            ot_amount_auto = (daily_wage * 1.5 / 8) * ot_hours
            st.info(f"💰 ยอดเงิน OT ที่คำนวณได้:\n\n **{ot_amount_auto:,.2f} บาท**")

        st.markdown("---")
        st.subheader("3. รายการหัก และ ยอดสะสม (YTD)")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            tax = st.number_input("หักภาษี", min_value=0.0, step=100.0)
            sso = st.number_input("หักประกันสังคม", min_value=0.0, step=100.0)
            absent = st.number_input("หักขาด/ลา/มาสาย", min_value=0.0, step=100.0)
            other_deduct = st.number_input("รายการหักอื่นๆ", min_value=0.0, step=100.0)
        with col_d2:
            ytd_income = st.number_input("รายได้สะสม (YTD)", min_value=0.0, step=1000.0)
            ytd_tax = st.number_input("ภาษีสะสม (YTD)", min_value=0.0, step=100.0)
            ytd_sso = st.number_input("ประกันสังคมสะสม (YTD)", min_value=0.0, step=100.0)

        submit_btn = st.form_submit_button("บันทึกข้อมูลและสร้าง PDF", type="primary", use_container_width=True)

    if submit_btn:
        if not emp_name:
            st.error("กรุณากรอกชื่อ-นามสกุลของพนักงาน")
        else:
            # --- ระบบจดจำและอัปเดตข้อมูลพนักงาน ---
            new_emp_data = {
                "รหัสพนักงาน": emp_id,
                "ชื่อ-นามสกุล": emp_name,
                "ตำแหน่ง": position,
                "แผนก": department,
                "ฐานเงินเดือน": salary
            }
            
            # ถ้ามีชื่อเดิมอยู่แล้วให้ลบของเก่าออกก่อนแล้วใส่ของใหม่ (อัปเดต)
            if emp_name in st.session_state.db_employees["ชื่อ-นามสกุล"].values:
                st.session_state.db_employees = st.session_state.db_employees[st.session_state.db_employees["ชื่อ-นามสกุล"] != emp_name]
            
            st.session_state.db_employees = pd.concat([st.session_state.db_employees, pd.DataFrame([new_emp_data])], ignore_index=True)
            st.session_state.db_employees.to_csv(EMP_FILE, index=False, encoding='utf-8-sig')

            # คำนวณยอดรวมเพื่อส่งไปทำ PDF
            income_sum = salary + ot_amount_auto + other_income
            deduction_sum = tax + sso + absent + other_deduct
            net_pay = income_sum - deduction_sum
            
            payslip_info = {
                "emp_id": emp_id, "employee_name": emp_name, "position": position, 
                "department": department, "pay_date": pay_date, "period": period,
                "salary": f"{salary:,.2f}", "ot_amount": f"{ot_amount_auto:,.2f}", "other_income": f"{other_income:,.2f}",
                "tax": f"{tax:,.2f}", "sso": f"{sso:,.2f}", "absent": f"{absent:,.2f}", "other_deduct": f"{other_deduct:,.2f}",
                "ytd_income": f"{ytd_income:,.2f}" if ytd_income > 0 else "-",
                "ytd_tax": f"{ytd_tax:,.2f}" if ytd_tax > 0 else "-",
                "ytd_sso": f"{ytd_sso:,.2f}" if ytd_sso > 0 else "-",
                "income_sum": f"{income_sum:,.2f}", "deduction_sum": f"{deduction_sum:,.2f}", "net_pay": f"{net_pay:,.2f}"
            }
            
            with st.spinner("กำลังสร้างไฟล์ PDF และบันทึกข้อมูล..."):
                doc_no = generate_payslip_no()
                pdf_bytes = generate_payslip_pdf_bytes(payslip_info)
                
                # บันทึกลงประวัติสลิป
                new_hist = pd.DataFrame([{"วันที่": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "เลขที่สลิป": doc_no, "ชื่อพนักงาน": emp_name, "ยอดสุทธิ": net_pay}])
                st.session_state.db_history = pd.concat([st.session_state.db_history, new_hist], ignore_index=True)
                st.session_state.db_history.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')
                
                st.success(f"บันทึกข้อมูลและสร้างเอกสารของคุณ {emp_name} เรียบร้อยแล้ว")
                st.download_button("📥 ดาวน์โหลดสลิป (PDF)", data=pdf_bytes, file_name=f"Payslip_{emp_name}.pdf", mime="application/pdf")

with tab2:
    st.subheader("ประวัติการออกสลิป")
    st.dataframe(st.session_state.db_history, use_container_width=True)
with tab3:
    st.subheader("รายชื่อพนักงานที่บันทึกไว้")
    st.dataframe(st.session_state.db_employees, use_container_width=True)
