import streamlit as st
import pandas as pd
import os
from datetime import date
from generate_payslip_pdf import generate_payslip_pdf_bytes

EMP_FILE = "database_employees.csv"


# =========================
# โหลดฐานข้อมูล
# =========================

def load_employees():

    if os.path.exists(EMP_FILE):
        return pd.read_csv(EMP_FILE, encoding="utf-8-sig")

    df = pd.DataFrame(columns=[
        "name",
        "position",
        "account",
        "start_date"
    ])

    df.to_csv(EMP_FILE, index=False, encoding="utf-8-sig")

    return df


employees = load_employees()

st.title("โปรแกรมออกสลิปเงินเดือน")


# =========================
# เลือก / กรอกพนักงาน
# =========================

st.subheader("ข้อมูลพนักงาน")

if "name_input" not in st.session_state:
    st.session_state.name_input = ""

colA, colB = st.columns(2)

with colA:

    name = st.text_input(
        "ชื่อพนักงาน",
        key="name_input"
    )

with colB:

    selected = st.selectbox(
        "เลือกจากฐานข้อมูล",
        [""] + employees["name"].tolist()
    )

    if selected:
        st.session_state.name_input = selected
        name = selected


# =========================
# ข้อมูลบริษัท
# =========================

company = st.text_input("บริษัท")

col1, col2 = st.columns(2)

with col1:
    month = st.text_input("ประจำเดือน", "มีนาคม 2569")

with col2:
    pay_date = st.date_input("วันที่จ่ายเงิน", date.today())


# =========================
# รายได้
# =========================

st.subheader("รายการรายได้")

c1, c2 = st.columns(2)

with c1:

    wage_rate = st.number_input("ค่าแรงต่อชั่วโมง", 0.0)

    wage = st.number_input("ค่าจ้างรวม", 0.0)

    pos_allow = st.number_input("ค่าตำแหน่ง", 0.0)

    holiday = st.number_input("ค่าทำงานวันหยุด", 0.0)

with c2:

    ot_hours = st.number_input("OT ชั่วโมง", 0.0)

    ot = st.number_input("ค่า OT", 0.0)

    diligence = st.number_input("เบี้ยขยัน", 0.0)

    target = st.number_input("ค่าเป้า", 0.0)

    other = st.number_input("อื่นๆ", 0.0)


# =========================
# รายการหัก
# =========================

st.subheader("รายการหัก")

c3, c4 = st.columns(2)

with c3:

    advance = st.number_input("จ่ายล่วงหน้า", 0.0)

    uniform = st.number_input("ค่าประกันชุด", 0.0)

    absent = st.number_input("ขาดงาน", 0.0)

with c4:

    leave = st.number_input("ลากิจ / ป่วย", 0.0)

    late = st.number_input("สาย", 0.0)

    tax = st.number_input("ภาษี", 0.0)


# =========================
# เงินสะสม
# =========================

ytd = st.number_input("เงินได้สะสม", 0.0)


# =========================
# คำนวณ
# =========================

income_sum = (
    wage
    + pos_allow
    + holiday
    + ot
    + diligence
    + target
    + other
)

deduct_sum = (
    advance
    + uniform
    + absent
    + leave
    + late
    + tax
)

net = income_sum - deduct_sum


# =========================
# สรุป
# =========================

st.subheader("สรุป")

s1, s2, s3 = st.columns(3)

with s1:
    st.metric("รวมรายได้", f"{income_sum:,.2f}")

with s2:
    st.metric("รวมรายการหัก", f"{deduct_sum:,.2f}")

with s3:
    st.metric("เงินสุทธิ", f"{net:,.2f}")


# =========================
# สร้าง PDF
# =========================

if st.button("สร้าง Pay Slip"):

    data = {

        "company": company,

        "name": name,
        "position": "",
        "account": "",
        "start_date": "",

        "month": month,
        "pay_date": pay_date.strftime("%d-%m-%Y"),

        "wage_rate": wage_rate,
        "wage": wage,

        "pos_allow": pos_allow,
        "holiday": holiday,

        "ot_hours": ot_hours,
        "ot": ot,

        "diligence": diligence,
        "target": target,
        "other": other,

        "advance": advance,
        "uniform": uniform,
        "absent": absent,

        "leave": leave,
        "late": late,
        "tax": tax,

        "income_sum": income_sum,
        "deduct_sum": deduct_sum,

        "net": net,
        "ytd": ytd
    }

    pdf = generate_payslip_pdf_bytes(data)

    st.download_button(
        "ดาวน์โหลด PDF",
        pdf,
        file_name=f"payslip_{name}.pdf",
        mime="application/pdf"
    )
