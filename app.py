import streamlit as st
import pandas as pd
from database import load_data, generate_payslip_no
from generate_payslip_pdf import generate_payslip_pdf_bytes

st.set_page_config(page_title="ระบบสลิปเงินเดือน", layout="wide")

# โหลดฐานข้อมูล
load_data()

st.title("ระบบออกใบแจ้งเงินเดือน (Payslip Generator)")

# ทำ UI แบ่ง Tab คล้ายๆ ระบบใบเสนอราคา
tab1, tab2, tab3 = st.tabs(["สร้างสลิปเงินเดือน", "ฐานข้อมูลพนักงาน", "ประวัติการออกสลิป"])

with tab1:
    st.subheader("รายละเอียดสลิปเงินเดือน")
    doc_no = generate_payslip_no()
    st.info(f"เลขที่เอกสาร: {doc_no}")
    
    with st.form("payslip_form"):
        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("ชื่อ-นามสกุลพนักงาน")
            salary = st.number_input("เงินเดือนพื้นฐาน", min_value=0.0)
            bonus = st.number_input("โบนัส / ค่าคอมมิชชั่น", min_value=0.0)
        with col2:
            month = st.text_input("ประจำเดือน/ปี")
            absent = st.number_input("หักขาดลามาสาย", min_value=0.0)
            tax_ss = st.number_input("หักประกันสังคม/ภาษี", min_value=0.0)
            
        submit_btn = st.form_submit_button("สร้าง PDF สลิปเงินเดือน", type="primary")

    if submit_btn:
        net_pay = (salary + bonus) - (absent + tax_ss)
        
        # จัดเตรียม dict สำหรับโยนให้ไฟล์ PDF
        payslip_info = {
            "doc_no": doc_no,
            "month": month,
            "employee_name": emp_name,
            "salary": f"{salary:,.2f}",
            "bonus": f"{bonus:,.2f}",
            "absent": f"{absent:,.2f}",
            "other_deduct": f"{tax_ss:,.2f}",
            "net_pay": f"{net_pay:,.2f}"
        }
        
        with st.spinner("กำลังสร้างไฟล์ PDF..."):
            pdf_bytes = generate_payslip_pdf_bytes(payslip_info)
            st.success("สร้างสำเร็จ!")
            st.download_button("📥 ดาวน์โหลดสลิป (PDF)", data=pdf_bytes, file_name=f"{doc_no}_{emp_name}.pdf", mime="application/pdf")

with tab2:
    st.subheader("จัดการฐานข้อมูลพนักงาน")
    st.dataframe(st.session_state.db_employees)
    # ใส่โค้ดเพิ่ม/ลบ พนักงานตรงนี้

with tab3:
    st.subheader("ประวัติการออกสลิปเงินเดือน")
    st.dataframe(st.session_state.db_history)