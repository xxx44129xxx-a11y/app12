import streamlit as st
import pandas as pd
from datetime import datetime
import os
from database import load_data, generate_payslip_no, HISTORY_FILE
EMP_FILE = "database_employees.csv"
from generate_payslip_pdf import generate_payslip_pdf_bytes

st.set_page_config(page_title="ระบบสลิปเงินเดือน", layout="wide")
load_data()

# ตรวจสอบคอลัมน์ใน db_employees ให้อัปเดตตามฟิลด์ใหม่
if st.session_state.db_employees.empty or "ชื่อ-นามสกุล" not in st.session_state.db_employees.columns:
    st.session_state.db_employees = pd.DataFrame(columns=[
        "รหัสพนักงาน", "ชื่อ-นามสกุล", "ตำแหน่ง", "แผนก", "วันที่เข้างาน", "เลขที่บัญชี", "ฐานเงินเดือน"
    ])

st.title("💸 ระบบออกใบแจ้งเงินเดือน")

tab1, tab2, tab3 = st.tabs(["สร้างสลิปเงินเดือน", "ประวัติการออกสลิป", "ฐานข้อมูลพนักงาน"])

with tab1:
    st.subheader("1. เลือกหรือกรอกข้อมูลพนักงาน")
    emp_list = st.session_state.db_employees["ชื่อ-นามสกุล"].tolist()
    name_option = st.selectbox("ค้นหารายชื่อพนักงานที่บันทึกไว้ (หรือพิมพ์ชื่อใหม่ด้านล่าง)", ["-- พิมพ์ชื่อใหม่ --"] + emp_list)
    
    saved_data = {}
    if name_option != "-- พิมพ์ชื่อใหม่ --":
        row = st.session_state.db_employees[st.session_state.db_employees["ชื่อ-นามสกุล"] == name_option].iloc[0]
        saved_data = {
            "id": row.get("รหัสพนักงาน", ""), "name": row.get("ชื่อ-นามสกุล", ""),
            "pos": row.get("ตำแหน่ง", ""), "dept": row.get("แผนก", ""),
            "start_date": row.get("วันที่เข้างาน", ""), "acc_no": row.get("เลขที่บัญชี", ""),
            "salary": float(row.get("ฐานเงินเดือน", 0)) if pd.notna(row.get("ฐานเงินเดือน")) else 0.0
        }

    with st.form("payslip_form"):
        # ข้อมูลส่วนตัวและบริษัท
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1: emp_id = st.text_input("รหัสพนักงาน", value=saved_data.get("id", ""))
        with col_e2: emp_name = st.text_input("ชื่อ-นามสกุล", value=saved_data.get("name", "") if name_option == "-- พิมพ์ชื่อใหม่ --" else name_option)
        with col_e3: position = st.text_input("ตำแหน่ง", value=saved_data.get("pos", ""))
        with col_e4: department = st.text_input("แผนก", value=saved_data.get("dept", ""))

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
        with col_d1: start_date = st.text_input("วันที่เข้างาน", value=saved_data.get("start_date", ""))
        with col_d2: account_no = st.text_input("เลขที่บัญชี", value=saved_data.get("acc_no", ""))
        with col_d3: pay_date = st.text_input("วันที่จ่าย (เช่น 31 มี.ค. 2569)", value=datetime.now().strftime("%d %b %Y"))
        with col_d4: period = st.text_input("งวดที่ (เช่น 03/2569)")

        st.markdown("---")
        
        # จัดเรียง 3 คอลัมน์ให้ตรงกับรูปแบบหน้า PDF
        col_inc, col_ded, col_ytd = st.columns(3)
        
        with col_inc:
            st.markdown("**รายได้ (INCOME)**")
            salary = st.number_input("เงินเดือนพื้นฐาน", min_value=0.0, step=1000.0, value=saved_data.get("salary", 0.0))
            
            # ระบบคำนวณ OT
            st.markdown("*--- คำนวณ OT ---*")
            daily_wage = st.number_input("รายได้/วัน", min_value=0.0, step=100.0, value=salary/30 if salary > 0 else 0.0)
            ot_hours = st.number_input("จำนวนชั่วโมง OT", min_value=0.0, step=1.0)
            ot_amount_auto = (daily_wage * 1.5 / 8) * ot_hours
            st.info(f"ยอด OT: **{ot_amount_auto:,.2f}**")
            
            position_allowance = st.number_input("ค่าตำแหน่ง", min_value=0.0, step=100.0)
            diligence = st.number_input("เบี้ยขยัน", min_value=0.0, step=100.0)
            shift_allowance = st.number_input("ค่ากะ", min_value=0.0, step=100.0)
            other_income = st.number_input("รายได้อื่นๆ", min_value=0.0, step=100.0)

        with col_ded:
            st.markdown("**รายการหัก (DEDUCTION)**")
            tax = st.number_input("หักภาษี", min_value=0.0, step=100.0)
            sso = st.number_input("หักประกันสังคม", min_value=0.0, step=100.0)
            absent = st.number_input("หักขาด/ลา/มาสาย", min_value=0.0, step=100.0)
            advance = st.number_input("เบิกล่วงหน้า", min_value=0.0, step=100.0)
            loan = st.number_input("เงินกู้", min_value=0.0, step=100.0)
            other_deduct = st.number_input("รายการหักอื่นๆ", min_value=0.0, step=100.0)

        with col_ytd:
            st.markdown("**ยอดสะสม (YTD)**")
            ytd_income = st.number_input("รายได้สะสม (YTD)", min_value=0.0, step=1000.0)
            ytd_tax = st.number_input("ภาษีสะสม (YTD)", min_value=0.0, step=100.0)
            ytd_sso = st.number_input("ประกันสังคมสะสม (YTD)", min_value=0.0, step=100.0)
            ytd_provident = st.number_input("กองทุนสำรองเลี้ยงชีพสะสม (YTD)", min_value=0.0, step=100.0)

        submit_btn = st.form_submit_button("บันทึกข้อมูลและสร้าง PDF", type="primary", use_container_width=True)

    if submit_btn:
        if not emp_name:
            st.error("กรุณากรอกชื่อ-นามสกุลของพนักงาน")
        else:
            new_emp_data = {
                "รหัสพนักงาน": emp_id, "ชื่อ-นามสกุล": emp_name, "ตำแหน่ง": position,
                "แผนก": department, "วันที่เข้างาน": start_date, "เลขที่บัญชี": account_no,
                "ฐานเงินเดือน": salary
            }
            
            if emp_name in st.session_state.db_employees["ชื่อ-นามสกุล"].values:
                st.session_state.db_employees = st.session_state.db_employees[st.session_state.db_employees["ชื่อ-นามสกุล"] != emp_name]
            
            st.session_state.db_employees = pd.concat([st.session_state.db_employees, pd.DataFrame([new_emp_data])], ignore_index=True)
            st.session_state.db_employees.to_csv(EMP_FILE, index=False, encoding='utf-8-sig')

            # รวมยอดทั้งหมดตามหัวข้อใหม่
            income_sum = salary + ot_amount_auto + position_allowance + diligence + shift_allowance + other_income
            deduction_sum = tax + sso + absent + advance + loan + other_deduct
            net_pay = income_sum - deduction_sum
            
            payslip_info = {
                "emp_id": emp_id, "employee_name": emp_name, "position": position, 
                "department": department, "start_date": start_date, "account_no": account_no,
                "pay_date": pay_date, "period": period,
                
                "salary": f"{salary:,.2f}", "ot_amount": f"{ot_amount_auto:,.2f}",
                "position_allowance": f"{position_allowance:,.2f}", "diligence": f"{diligence:,.2f}",
                "shift_allowance": f"{shift_allowance:,.2f}", "other_income": f"{other_income:,.2f}",
                
                "tax": f"{tax:,.2f}", "sso": f"{sso:,.2f}", "absent": f"{absent:,.2f}",
                "advance": f"{advance:,.2f}", "loan": f"{loan:,.2f}", "other_deduct": f"{other_deduct:,.2f}",
                
                "ytd_income": f"{ytd_income:,.2f}" if ytd_income > 0 else "-",
                "ytd_tax": f"{ytd_tax:,.2f}" if ytd_tax > 0 else "-",
                "ytd_sso": f"{ytd_sso:,.2f}" if ytd_sso > 0 else "-",
                "ytd_provident": f"{ytd_provident:,.2f}" if ytd_provident > 0 else "-",
                
                "income_sum": f"{income_sum:,.2f}", "deduction_sum": f"{deduction_sum:,.2f}", "net_pay": f"{net_pay:,.2f}"
            }
            
            with st.spinner("กำลังสร้างไฟล์ PDF และบันทึกข้อมูล..."):
                doc_no = generate_payslip_no()
                pdf_bytes = generate_payslip_pdf_bytes(payslip_info)
                
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
