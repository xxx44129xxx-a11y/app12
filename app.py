import streamlit as st
import pandas as pd
import os
from datetime import date

from generate_payslip_pdf import generate_payslip_pdf_bytes

EMP_FILE = "database_employees.csv"


# =============================
# โหลดฐานข้อมูลพนักงาน
# =============================

def load_employees():

    if os.path.exists(EMP_FILE):
        return pd.read_csv(EMP_FILE, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(
            columns=[
                "name",
                "position",
                "account",
                "start_date"
            ]
        )
        df.to_csv(EMP_FILE, index=False, encoding="utf-8-sig")
        return df


employees = load_employees()

st.title("โปรแกรมออกใบ Pay Slip")


# =============================
# เลือกพนักงาน
# =============================

name = st.selectbox(
    "เลือกพนักงาน",
    employees["name"] if not employees.empty else []
)

employee = employees[employees["name"] == name]

if not employee.empty:
    employee = employee.iloc[0]

    position = employee["position"]
    account = employee["account"]
    start_date = employee["start_date"]

else:
    position = ""
    account = ""
    start_date = ""


# =============================
# ข้อมูลสลิป
# =============================

month = st.text_input("ประจำเดือน", "มีนาคม 2569")
pay_date = st.date_input("วันที่จ่ายเงิน", date.today())


# =============================
# รายได้
# =============================

st.subheader("รายการรายได้")

wage_rate = st.number_input("ค่าแรงต่อชั่วโมง", 0.0)
wage = st.number_input("ค่าจ้างรวม", 0.0)

pos_allow = st.number_input("ค่าตำแหน่ง", 0.0)
holiday = st.number_input("ค่าทำงานวันหยุด", 0.0)

ot_hours = st.number_input("OT ชั่วโมง", 0.0)
ot = st.number_input("ค่า OT", 0.0)

diligence = st.number_input("เบี้ยขยัน", 0.0)
target = st.number_input("ค่าเป้า", 0.0)
other = st.number_input("อื่นๆ", 0.0)


# =============================
# รายการหัก
# =============================

st.subheader("รายการหัก")

advance = st.number_input("จ่ายล่วงหน้า", 0.0)
uniform = st.number_input("ค่าประกันชุด", 0.0)
absent = st.number_input("ขาดงาน", 0.0)
leave = st.number_input("ลากิจ / ป่วย", 0.0)
late = st.number_input("สาย", 0.0)
tax = st.number_input("ภาษี", 0.0)


# =============================
# คำนวณ
# =============================

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

st.subheader("สรุป")

st.write("รวมรายได้:", income_sum)
st.write("รวมรายการหัก:", deduct_sum)
st.write("เงินสุทธิ:", net)


# =============================
# เงินสะสม
# =============================

ytd = st.number_input("เงินได้สะสม", 0.0)


# =============================
# สร้าง PDF
# =============================

if st.button("สร้าง Pay Slip"):

    data = {
        "name": name,
        "position": position,
        "account": account,
        "start_date": start_date,
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
