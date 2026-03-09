import os
import base64
from playwright.sync_api import sync_playwright

def get_base64_font(font_path):
    # แปลงฟอนต์เป็น Base64 เพื่อฝังลงใน HTML ป้องกันปัญหาฟอนต์หายบน Render
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode("utf-8")

def generate_payslip_pdf_bytes(info):
    
    # เช็คว่ามีไฟล์ฟอนต์อยู่ในโฟลเดอร์เดียวกันไหม (ตอนเอาขึ้น GitHub ต้องอัปโหลดไฟล์ THSarabunNew.ttf ไปด้วยนะ)
    font_base64 = ""
    if os.path.exists("THSarabunNew.ttf"):
        font_base64 = get_base64_font("THSarabunNew.ttf")
    
    font_face = f"""
    @font-face {{
        font-family: 'THSarabunNew';
        src: url(data:font/truetype;charset=utf-8;base64,{font_base64}) format('truetype');
    }}
    """ if font_base64 else ""

    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8" />
        <style>
            {font_face}
            body {{ font-family: 'THSarabunNew', sans-serif; font-size: 18px; }}
            h2 {{ text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #000; padding: 8px; }}
            .right {{ text-align: right; }}
            .yellow {{ background-color: #ffffcc; font-weight: bold; }}
            .footer {{ margin-top: 40px; display: flex; justify-content: space-between; }}
        </style>
    </head>
    <body>
        <h2>ใบสลิปเงินเดือน</h2>
        <p>ชื่อพนักงาน: {info.get("employee_name", "")}</p>
        
        <table>
            <tr>
                <td>เงินเดือน</td><td class="right">{info.get("salary","0")}</td>
                <td>หักภาษี</td><td class="right">{info.get("tax","0")}</td>
                <td>รวมรายรับ</td><td class="right">{info.get("income_sum","0")}</td>
            </tr>
            <tr>
                <td>โบนัส</td><td class="right">{info.get("bonus","0")}</td>
                <td>ขาดลามาสาย</td><td class="right">{info.get("absent","0")}</td>
                <td>รวมรายการหัก</td><td class="right">{info.get("deduction_sum","0")}</td>
            </tr>
            <tr>
                <td>รายได้อื่นๆ</td><td class="right">{info.get("other_income","0")}</td>
                <td>รายการหักอื่นๆ</td><td class="right">{info.get("other_deduct","0")}</td>
                <td class="yellow">เงินได้สุทธิ</td>
                <td class="right yellow">{info.get("net_pay","0")}</td>
            </tr>
        </table>

        <div class="footer">
            <div>หมายเหตุ: {info.get("remark","-")}</div>
            <div>ลายเซ็นนายจ้าง ___________________________</div>
        </div>
    </body>
    </html>
    """

    with sync_playwright() as pw:
        # โค้ดสำหรับรัน Playwright บน Render
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
        page.set_content(html)
        
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()
        
        return pdf_bytes
