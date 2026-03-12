from fpdf import FPDF
from io import BytesIO

SIGNER_NAME = "นายพงศ์พิพัช ประสาท"
SIGNATURE_IMAGE = "547.png"


class PayslipPDF(FPDF):
    pass


def generate_payslip_pdf_bytes(data):

    pdf = PayslipPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_font("THSarabun", "", "THSarabunNew.ttf", uni=True)
    pdf.set_font("THSarabun", "", 16)

    # ======================
    # หัวเอกสาร (แก้ตามที่สั่ง)
    # ======================

    pdf.set_font("THSarabun", "", 18)

    pdf.cell(100, 10, data["company"], 0, 0, "L")  # ชื่อบริษัทซ้าย
    pdf.cell(0, 10, "สลิปเงินเดือน / Pay Slip", 0, 1, "R")  # ชื่อเอกสารขวา

    pdf.ln(3)

    pdf.cell(95, 8, f"ชื่อ-สกุล : {data['name']}", 0, 0)
    pdf.cell(95, 8, f"ประจำเดือน : {data['month']}", 0, 1)

    pdf.cell(95, 8, f"ตำแหน่ง : {data['position']}", 0, 0)
    pdf.cell(95, 8, f"เลขที่บัญชี : {data['account']}", 0, 1)

    pdf.cell(95, 8, f"วันที่เริ่มงาน : {data['start_date']}", 0, 0)
    pdf.cell(95, 8, f"วันที่จ่ายเงิน : {data['pay_date']}", 0, 1)

    pdf.ln(3)

    # ======================
    # ตั้งค่าความกว้างตาราง
    # ======================

    w1 = 45
    w2 = 20
    w3 = 15
    w4 = 30
    w5 = 40
    w6 = 30

    table_width = w1 + w2 + w3 + w4 + w5 + w6

    page_width = 210
    start_x = (page_width - table_width) / 2

    pdf.set_x(start_x)

    # ======================
    # หัวตาราง
    # ======================

    pdf.cell(w1 + w2 + w3, 8, "รายการเงินได้", 1, 0, "C")
    pdf.cell(w4, 8, "จำนวนเงิน", 1, 0, "C")
    pdf.cell(w5, 8, "รายการเงินหัก", 1, 0, "C")
    pdf.cell(w6, 8, "จำนวนเงิน", 1, 1, "C")

    def row(l1="", l2="", l3="", l4="", r1="", r2=""):

        pdf.set_x(start_x)

        pdf.cell(w1, 8, l1, 1)
        pdf.cell(w2, 8, l2, 1, 0, "R")
        pdf.cell(w3, 8, l3, 1, 0, "C")
        pdf.cell(w4, 8, l4, 1, 0, "R")
        pdf.cell(w5, 8, r1, 1)
        pdf.cell(w6, 8, r2, 1, 1, "R")

    row("ค่าจ้าง", f"{data['wage_rate']}", "ชม.", f"{data['wage']:,.2f}", "จ่ายล่วงหน้า", f"{data['advance']:,.2f}")
    row("ค่าตำแหน่ง", "", "", f"{data['pos_allow']:,.2f}", "ค่าประกันชุด", f"{data['uniform']:,.2f}")
    row("ค่าทำงานในวันหยุด", "", "", f"{data['holiday']:,.2f}", "ขาดงาน", f"{data['absent']:,.2f}")
    row("ค่าล่วงเวลา OT.", f"{data['ot_hours']}", "ชม.", f"{data['ot']:,.2f}", "ลากิจ+ป่วย", f"{data['leave']:,.2f}")
    row("ค่าเบี้ยขยัน", "", "", f"{data['diligence']:,.2f}", "สาย - นาที", f"{data['late']:,.2f}")
    row("ค่าเป้าหมาย", "", "", f"{data['target']:,.2f}", "ภาษี", f"{data['tax']:,.2f}")
    row("อื่นๆ", "", "", f"{data['other']:,.2f}", "", "")

    pdf.set_x(start_x)

    pdf.cell(w1 + w2 + w3, 8, "รวมรายรับ", 1, 0, "C")
    pdf.cell(w4, 8, f"{data['income_sum']:,.2f}", 1, 0, "R")
    pdf.cell(w5, 8, "รวมรายการหัก", 1, 0, "C")
    pdf.cell(w6, 8, f"{data['deduct_sum']:,.2f}", 1, 1, "R")

    pdf.ln(6)

    # ======================
    # เงินสุทธิ
    # ======================

    pdf.set_font("THSarabun", "", 18)

    pdf.cell(120, 10, "รวมรับเงินสุทธิ", 0, 0, "C")
    pdf.cell(60, 10, f"{data['net']:,.2f}", "B", 1, "R")

    pdf.ln(5)

    pdf.set_font("THSarabun", "", 16)
    pdf.cell(60, 8, "เงินได้สะสม", 0, 0)
    pdf.cell(60, 8, f"{data['ytd']:,.2f}", 0, 1)

    # ======================
    # ลายเซ็น
    # ======================

    pdf.ln(15)

    sig_x = 140
    sig_y = pdf.get_y()

    pdf.image(SIGNATURE_IMAGE, sig_x, sig_y, 40)

    pdf.set_y(sig_y + 25)
    pdf.set_x(sig_x)

    pdf.cell(40, 8, SIGNER_NAME, 0, 1, "C")

    buffer = BytesIO()
    pdf.output(buffer)

    return buffer.getvalue()
