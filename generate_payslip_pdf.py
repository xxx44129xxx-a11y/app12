import os
from fpdf import FPDF

def generate_payslip_pdf_bytes(info):
    pdf = FPDF(unit='mm', format='A4')
    pdf.add_page()
    
    # ตั้งค่าฟอนต์ THSarabunNew
    font_path = "THSarabunNew.ttf"
    if os.path.exists(font_path):
        pdf.add_font('THSarabunNew', '', font_path, uni=True)
        pdf.set_font('THSarabunNew', '', 16)
    else:
        # หากหาไฟล์ฟอนต์ไม่เจอ จะใช้ฟอนต์พื้นฐานแทน
        pdf.set_font('Arial', '', 12)
        
    # --- ส่วนหัวเอกสาร ---
    pdf.set_font('THSarabunNew', '', 24)
    pdf.cell(0, 10, 'ใบแจ้งยอดเงินเดือน / PAY SLIP', ln=True, align='C')
    pdf.ln(5)
    
    # --- ส่วนข้อมูลพนักงาน ---
    pdf.set_font('THSarabunNew', '', 16)
    
    # บรรทัดที่ 1
    pdf.cell(30, 8, 'รหัสพนักงาน:', 0, 0)
    pdf.cell(60, 8, str(info.get("emp_id", "-")), border='B', ln=0)
    pdf.cell(30, 8, 'ตำแหน่ง:', 0, 0)
    pdf.cell(60, 8, str(info.get("position", "-")), border='B', ln=1)
    
    # บรรทัดที่ 2
    pdf.cell(30, 8, 'ชื่อ-นามสกุล:', 0, 0)
    pdf.cell(60, 8, str(info.get("employee_name", "-")), border='B', ln=0)
    pdf.cell(30, 8, 'แผนก:', 0, 0)
    pdf.cell(60, 8, str(info.get("department", "-")), border='B', ln=1)
    
    # บรรทัดที่ 3
    pdf.cell(30, 8, 'วันที่จ่าย:', 0, 0)
    pdf.cell(60, 8, str(info.get("pay_date", "-")), border='B', ln=0)
    pdf.cell(30, 8, 'งวดที่:', 0, 0)
    pdf.cell(60, 8, str(info.get("period", "-")), border='B', ln=1)
    
    pdf.ln(8)
    
    # --- ส่วนตารางรายละเอียด ---
    # ความกว้างของแต่ละคอลัมน์ (รวม 180 mm)
    col_w = [35, 25, 35, 25, 35, 25]
    h = 8
    
    # หัวตาราง
    pdf.set_fill_color(240, 240, 240) # สีเทาอ่อน
    pdf.cell(col_w[0]+col_w[1], h, 'รายได้ (INCOME)', border=1, align='C', fill=True)
    pdf.cell(col_w[2]+col_w[3], h, 'รายการหัก (DEDUCTION)', border=1, align='C', fill=True)
    pdf.cell(col_w[4]+col_w[5], h, 'ยอดสะสม (YTD)', border=1, ln=1, align='C', fill=True)
    
    # ฟังก์ชันตัวช่วยสำหรับวาดแถวข้อมูล
    def draw_row(c1, v1, c2, v2, c3, v3):
        pdf.cell(col_w[0], h, f' {c1}', border=1)
        pdf.cell(col_w[1], h, f'{v1} ', border=1, align='R')
        pdf.cell(col_w[2], h, f' {c2}', border=1)
        pdf.cell(col_w[3], h, f'{v2} ', border=1, align='R')
        pdf.cell(col_w[4], h, f' {c3}', border=1)
        pdf.cell(col_w[5], h, f'{v3} ', border=1, ln=1, align='R')

    # ข้อมูลในตาราง
    draw_row('เงินเดือน', info.get('salary','0.00'), 'ภาษี', info.get('tax','0.00'), 'รายได้สะสม', info.get('ytd_income','-'))
    draw_row('ค่าล่วงเวลา (OT)', info.get('ot_amount','0.00'), 'ประกันสังคม', info.get('sso','0.00'), 'ภาษีสะสม', info.get('ytd_tax','-'))
    draw_row('รายได้อื่นๆ', info.get('other_income','0.00'), 'ขาด/ลา/มาสาย', info.get('absent','0.00'), 'ประกันสังคมสะสม', info.get('ytd_sso','-'))
    draw_row('', '', 'รายการหักอื่นๆ', info.get('other_deduct','0.00'), '', '')
    
    # แถวสรุปยอดสุทธิ
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(col_w[0], h+2, ' รวมรายได้', border=1, align='C', fill=True)
    pdf.cell(col_w[1], h+2, f"{info.get('income_sum','0.00')} ", border=1, align='R', fill=True)
    pdf.cell(col_w[2], h+2, ' รวมรายการหัก', border=1, align='C', fill=True)
    pdf.cell(col_w[3], h+2, f"{info.get('deduction_sum','0.00')} ", border=1, align='R', fill=True)
    pdf.cell(col_w[4], h+2, ' เงินได้สุทธิ', border=1, align='C', fill=True)
    pdf.cell(col_w[5], h+2, f"{info.get('net_pay','0.00')} ", border=1, align='R', fill=True)
    
    pdf.ln(25)
    
    # --- ส่วนลายเซ็น ---
    pdf.cell(90, 8, '________________________________', 0, 0, 'C')
    pdf.cell(90, 8, '________________________________', 0, 1, 'C')
    pdf.cell(90, 8, 'ผู้จ่ายเงิน', 0, 0, 'C')
    pdf.cell(90, 8, 'ผู้รับเงิน / พนักงาน', 0, 1, 'C')
    
    return bytes(pdf.output())
