import streamlit as st
import pandas as pd
from datetime import datetime
import os
from database import load_data, generate_payslip_no, HISTORY_FILE
from generate_payslip_pdf import generate_payslip_pdf_bytes

st.set_page_config(page_title="ระบบสลิปเงินเดือน", layout="wide")

load_data()

st.title("💸 ระบบออกใบแจ้งเงินเดือน (Payslip Generator)")

tab1, tab2 = st.tabs(["สร้างสลิปเงินเดือน", "ประวัติการออกสลิป"])

with tab1:
    doc_no = generate_payslip_no()
    st.info(f"📄 เลขที่เอกสาร: {doc_no}")
    
    with st.form("payslip_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("ชื่อ-นามสกุลพนักงาน")
            month = st.text_input("ประจำเดือน/ปี (เช่น มีนาคม 2569)")
            st.markdown("---")
            st.markdown("**รายรับ (Income)**")
            salary = st.number_input("เงินเดือนพื้นฐาน", min_value=0.0, step=1000.0)
            bonus = st.number_input("โบนัส / ค่าคอมมิชชั่น", min_value=0.0, step=500.0)
            other_income = st.number_input("รายได้อื่นๆ", min_value=0.0, step=100.0)
            
        with col2:
            remark = st.text_input("หมายเหตุเพิ่มเติม")
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("**รายการหัก (Deduction)**")
            tax = st.number_input("หักภาษี ณ ที่จ่าย", min_value=0.0, step=100.0)
            absent = st.number_input("หักขาดลามาสาย", min_value=0.0, step=100.0)
            other_deduct = st.number_input("หักอื่นๆ (เช่น ประกันสังคม)", min_value=0.0, step=100.0)
            
        submit_btn = st.form_submit_button("สร้าง PDF สลิปเงินเดือน", type="primary", use_container_width=True)

    if submit_btn:
        if not emp_name:
            st.warning("กรุณากรอกชื่อพนักงาน")
        else:
            # คำนวณยอดรวม
            income_sum = salary + bonus + other_income
            deduction_sum = tax + absent + other_deduct
            net_pay = income_sum - deduction_sum
            
            # เตรียมข้อมูลส่งให้ PDF
            payslip_info = {
                "month": month,
                "employee_name": emp_name,
                "salary": f"{salary:,.2f}",
                "bonus": f"{bonus:,.2f}",
                "other_income": f"{other_income:,.2f}",
                "tax": f"{tax:,.2f}",
                "absent": f"{absent:,.2f}",
                "other_deduct": f"{other_deduct:,.2f}",
                "income_sum": f"{income_sum:,.2f}",
                "deduction_sum": f"{deduction_sum:,.2f}",
                "net_pay": f"{net_pay:,.2f}",
                "remark": remark if remark else "-"
            }
            
            with st.spinner("กำลังสร้างไฟล์ PDF..."):
                # สร้าง PDF
                pdf_bytes = generate_payslip_pdf_bytes(payslip_info)
                
                # บันทึกลงประวัติ (CSV)
                new_record = pd.DataFrame([{
                    "วันที่": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "เลขที่สลิป": doc_no,
                    "ชื่อพนักงาน": emp_name,
                    "ยอดสุทธิ": net_pay
                }])
                st.session_state.db_history = pd.concat([st.session_state.db_history, new_record], ignore_index=True)
                st.session_state.db_history.to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')
                
                st.success("สร้างสำเร็จ! บันทึกประวัติเรียบร้อยแล้ว")
                st.download_button("📥 ดาวน์โหลดสลิป (PDF)", data=pdf_bytes, file_name=f"{doc_no}_{emp_name}.pdf", mime="application/pdf")

with tab2:
    st.subheader("ประวัติการออกสลิปเงินเดือน")
    st.dataframe(st.session_state.db_history, use_container_width=True)
