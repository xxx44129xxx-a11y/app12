import streamlit as st
import pandas as pd
import os
from datetime import date
from generate_payslip_pdf import generate_payslip_pdf_bytes

st.set_page_config(layout="wide")

EMP_FILE = "database_employees.csv"


# =========================
# DATABASE FUNCTIONS
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


def save_employees(df):
    df.to_csv(EMP_FILE, index=False, encoding="utf-8-sig")


employees = load_employees()


# =========================
# SESSION STATE
# =========================

if "name_input" not in st.session_state:
    st.session_state.name_input = ""

if "employee_select" not in st.session_state:
    st.session_state.employee_select = ""


def sync_name():
    st.session_state.name_input = st.session_state.employee_select


st.title("โปรแกรมออกสลิปเงินเดือน")

tab1, tab2 = st.tabs(["ออกสลิปเงินเดือน", "จัดการพนักงาน"])


# ======================================================
# TAB 1 : PAYSLIP
# ======================================================

with tab1:

    st.subheader("ข้อมูลพนักงาน")

    colA, colB = st.columns(2)

    with colA:

        name = st.text_input(
            "ชื่อพนักงาน",
            key="name_input"
        )

    with colB:

        selected = st.selectbox(
            "เลือกจากฐานข้อมูล",
            [""] + employees["name"].tolist(),
            key="employee_select",
            on_change=sync_name
        )

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


# ======================================================
# TAB 2 : EMPLOYEE MANAGEMENT
# ======================================================

with tab2:

    st.subheader("เพิ่มพนักงาน")

    name_new = st.text_input("ชื่อพนักงานใหม่")
    position_new = st.text_input("ตำแหน่ง")
    account_new = st.text_input("เลขบัญชี")
    start_date_new = st.text_input("วันที่เริ่มงาน")

    if st.button("บันทึกพนักงาน"):

        if name_new.strip() == "":
            st.warning("กรุณากรอกชื่อพนักงาน")

        else:

            new_row = pd.DataFrame([{
                "name": name_new,
                "position": position_new,
                "account": account_new,
                "start_date": start_date_new
            }])

            employees_updated = pd.concat([employees, new_row], ignore_index=True)

            save_employees(employees_updated)

            st.success("บันทึกพนักงานแล้ว")

            st.rerun()

    st.divider()

    st.subheader("ลบพนักงาน")

    if len(employees) > 0:

        delete_name = st.selectbox(
            "เลือกพนักงานที่จะลบ",
            employees["name"]
        )

        if st.button("ลบพนักงาน"):

            employees_updated = employees[employees["name"] != delete_name]

            save_employees(employees_updated)

            st.success("ลบพนักงานแล้ว")

            st.rerun()

    else:
        st.info("ยังไม่มีพนักงานในระบบ")
