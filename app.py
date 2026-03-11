import streamlit as st
import pandas as pd
import os
from datetime import datetime
from generate_payslip_pdf import generate_payslip_pdf_bytes

EMP_FILE = "database_employees.csv"

# ชื่อผู้จ่ายเงิน (ลายเซ็นด้านล่างสลิป)
SIGNER_NAME = "นายพงศ์พิพัช ประสาท"

st.set_page_config(page_title="ระบบสร้างสลิปเงินเดือน", layout="wide")

st.title("ระบบสร้างใบแจ้งรายได้ PAY SLIP")

# =====================
# โหลดฐานข้อมูลพนักงาน
# =====================

if os.path.exists(EMP_FILE):
    db = pd.read_csv(EMP_FILE, encoding="utf-8-sig")
else:
    db = pd.DataFrame(columns=[
        "ชื่อ-นามสกุล",
        "ตำแหน่ง",
        "วันที่เริ่มงาน",
        "เลขบัญชี"
    ])

# =====================
# เลือกพนักงาน
# =====================

emp_list = db["ชื่อ-นามสกุล"].tolist()

emp_option = st.selectbox(
    "เลือกพนักงาน",
    ["พนักงานใหม่"] + emp_list
)

saved = {}

if emp_option != "พนักงานใหม่":
    row = db[db["ชื่อ-นามสกุล"] == emp_option].iloc[0]

    saved = {
        "name": row["ชื่อ-นามสกุล"],
        "position": row["ตำแหน่ง"],
        "start_date": row["วันที่เริ่มงาน"],
        "account": row["เลขบัญชี"]
    }

# =====================
# ข้อมูลพนักงาน
# =====================

st.subheader("ข้อมูลพนักงาน")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("ชื่อ-นามสกุล", value=saved.get("name", ""))
    position = st.text_input("ตำแหน่ง", value=saved.get("position", ""))
    start_date = st.text_input("วันที่เริ่มงาน", value=saved.get("start_date", ""))

with col2:
    month = st.text_input("ประจำเดือน")
    account = st.text_input("เลขบัญชี", value=saved.get("account", ""))
    pay_date = st.text_input("วันที่จ่ายเงิน", value=datetime.now().strftime("%d/%m/%Y"))

st.divider()

# =====================
# รายได้
# =====================

st.subheader("รายการรายได้")

daily_income = st.number_input("รายได้ต่อวัน", min_value=0.0)
ot_hours = st.number_input("จำนวนชั่วโมง OT", min_value=0.0)

ot = (daily_income * 1.5 / 8) * ot_hours

st.info(f"OT = {ot:,.2f} บาท")

wage = st.number_input("ค่าจ้างอื่น", min_value=0.0)
pos_allow = st.number_input("ค่าตำแหน่ง", min_value=0.0)
holiday = st.number_input("ค่าทำงานวันหยุด", min_value=0.0)
diligence = st.number_input("ค่าเบี้ยขยัน", min_value=0.0)
target = st.number_input("ค่าเป้า", min_value=0.0)
other_income = st.number_input("อื่นๆ", min_value=0.0)

# =====================
# รายการหัก
# =====================

st.subheader("รายการหัก")

advance = st.number_input("จ่ายล่วงหน้า", min_value=0.0)
uniform = st.number_input("ค่าประกันชุด", min_value=0.0)
absent = st.number_input("ขาดงาน", min_value=0.0)
leave = st.number_input("ลากิจ/ป่วย", min_value=0.0)
late = st.number_input("สาย", min_value=0.0)
tax = st.number_input("ภาษี", min_value=0.0)

st.divider()

ytd = st.number_input("เงินได้สะสม", min_value=0.0)

# =====================
# ปุ่มสร้าง PDF
# =====================

if st.button("สร้างสลิปเงินเดือน"):

    if name == "":
        st.error("กรุณากรอกชื่อพนักงาน")
        st.stop()

    income_sum = (
        wage + pos_allow + holiday + ot +
        diligence + target + other_income
    )

    deduct_sum = (
        advance + uniform + absent +
        leave + late + tax
    )

    net = income_sum - deduct_sum

    # บันทึกพนักงาน
    new_emp = {
        "ชื่อ-นามสกุล": name,
        "ตำแหน่ง": position,
        "วันที่เริ่มงาน": start_date,
        "เลขบัญชี": account
    }

    if name not in db["ชื่อ-นามสกุล"].values:
        db = pd.concat([db, pd.DataFrame([new_emp])], ignore_index=True)
        db.to_csv(EMP_FILE, index=False, encoding="utf-8-sig")

    data = {

        "name": name,
        "position": position,
        "start_date": start_date,
        "month": month,
        "account": account,
        "pay_date": pay_date,

        "wage": wage,
        "pos_allow": pos_allow,
        "holiday": holiday,
        "ot": ot,
        "diligence": diligence,
        "target": target,
        "other": other_income,

        "advance": advance,
        "uniform": uniform,
        "absent": absent,
        "leave": leave,
        "late": late,
        "tax": tax,

        "income_sum": income_sum,
        "deduct_sum": deduct_sum,
        "net": net,
        "ytd": ytd,

        # ชื่อคนเซ็น
        "signer": SIGNER_NAME
    }

    pdf = generate_payslip_pdf_bytes(data)

    st.download_button(
        "ดาวน์โหลด PDF",
        data=pdf,
        file_name=f"payslip_{name}.pdf",
        mime="application/pdf"
    )
