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

    # โหลดฟอนต์ไทย
    pdf.add_font("THSarabun", "", "THSarabunNew.ttf", uni=True)

    pdf.set_font("THSarabun", "", 20)
    pdf.cell(0, 10, "PAY SLIP", 0, 1, "C")

    pdf.ln(5)

    pdf.set_font("THSarabun", "", 16)

    # ข้อมูลพนักงาน
    pdf.cell(95, 8, f"ชื่อพนักงาน: {data['name']}", 0, 0)
    pdf.cell(95, 8, f"ตำแหน่ง: {data['position']}", 0, 1)

    pdf.cell(95, 8, f"วันที่เริ่มงาน: {data['start_date']}", 0, 0)
    pdf.cell(95, 8, f"เลขบัญชี: {data['account']}", 0, 1)

    pdf.cell(95, 8, f"ประจำเดือน: {data['month']}", 0, 0)
    pdf.cell(95, 8, f"วันที่จ่าย: {data['pay_date']}", 0, 1)

    pdf.ln(5)

    pdf.set_font("THSarabun", "", 16)

    def row(title, value):
        pdf.cell(95, 8, title, 1, 0)
        pdf.cell(95, 8, f"{value:,.2f}", 1, 1, "R")

    row("ค่าจ้าง", data["wage"])
    row("ค่าตำแหน่ง", data["pos_allow"])
    row("ค่าทำงานวันหยุด", data["holiday"])
    row("OT", data["ot"])
    row("เบี้ยขยัน", data["diligence"])
    row("ค่าเป้า", data["target"])
    row("อื่นๆ", data["other"])

    pdf.cell(95, 8, "รวมรายได้", 1, 0)
    pdf.cell(95, 8, f"{data['income_sum']:,.2f}", 1, 1, "R")

    pdf.ln(5)

    row("จ่ายล่วงหน้า", data["advance"])
    row("ค่าประกันชุด", data["uniform"])
    row("ขาดงาน", data["absent"])
    row("ลากิจ/ป่วย", data["leave"])
    row("สาย", data["late"])
    row("ภาษี", data["tax"])

    pdf.cell(95, 8, "รวมรายการหัก", 1, 0)
    pdf.cell(95, 8, f"{data['deduct_sum']:,.2f}", 1, 1, "R")

    pdf.ln(5)

    pdf.cell(95, 10, "เงินสุทธิ", 1, 0)
    pdf.cell(95, 10, f"{data['net']:,.2f}", 1, 1, "R")

    pdf.ln(10)

    pdf.cell(0, 8, f"เงินได้สะสม: {data['ytd']:,.2f}", 0, 1)

    # ลายเซ็น
    pdf.ln(25)

    signature_x = 140
    signature_y = pdf.get_y()

    pdf.image(SIGNATURE_IMAGE, x=signature_x, y=signature_y, w=40)

    pdf.set_y(signature_y + 25)
    pdf.set_x(signature_x)

    pdf.cell(40, 8, SIGNER_NAME, 0, 1, "C")

    buffer = BytesIO()
    pdf.output(buffer)

    return buffer.getvalue()
