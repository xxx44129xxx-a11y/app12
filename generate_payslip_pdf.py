from playwright.sync_api import sync_playwright

def generate_payslip_pdf_bytes(info):
    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8" />
        <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Sarabun', sans-serif;
                font-size: 16px;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            .container {{ width: 100%; max-width: 800px; margin: auto; }}
            h2 {{ text-align: center; margin-bottom: 5px; }}
            h3 {{ text-align: center; margin-top: 0; font-weight: normal; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
            .right {{ text-align: right; }}
            .yellow {{ background-color: #ffffcc; font-weight: bold; }}
            .footer {{ margin-top: 40px; display: flex; justify-content: space-between; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>ใบแจ้งเงินเดือน (Payslip)</h2>
            <h3>ประจำเดือน {info.get("month", "")}</h3>
            
            <p><strong>ชื่อพนักงาน:</strong> {info.get("employee_name", "")}</p>
            
            <table>
                <tr>
                    <th>รายรับ (Income)</th>
                    <th class="right">จำนวนเงิน (บาท)</th>
                    <th>รายการหัก (Deduction)</th>
                    <th class="right">จำนวนเงิน (บาท)</th>
                </tr>
                <tr>
                    <td>เงินเดือนพื้นฐาน</td><td class="right">{info.get("salary","0")}</td>
                    <td>หักภาษี ณ ที่จ่าย</td><td class="right">{info.get("tax","0")}</td>
                </tr>
                <tr>
                    <td>โบนัส / ค่าคอมมิชชั่น</td><td class="right">{info.get("bonus","0")}</td>
                    <td>ขาดลามาสาย</td><td class="right">{info.get("absent","0")}</td>
                </tr>
                <tr>
                    <td>รายได้อื่นๆ</td><td class="right">{info.get("other_income","0")}</td>
                    <td>รายการหักอื่นๆ</td><td class="right">{info.get("other_deduct","0")}</td>
                </tr>
                <tr>
                    <td class="yellow">รวมรายรับ</td><td class="right yellow">{info.get("income_sum","0")}</td>
                    <td class="yellow">รวมรายการหัก</td><td class="right yellow">{info.get("deduction_sum","0")}</td>
                </tr>
                <tr>
                    <td colspan="2" style="border: none;"></td>
                    <td class="yellow" style="font-size: 18px;">เงินได้สุทธิ (Net Pay)</td>
                    <td class="right yellow" style="font-size: 18px;">{info.get("net_pay","0")}</td>
                </tr>
            </table>

            <div class="footer">
                <div><strong>หมายเหตุ:</strong> {info.get("remark","-")}</div>
                <div>ลายเซ็นนายจ้าง ___________________________</div>
            </div>
        </div>
    </body>
    </html>
    """

    with sync_playwright() as pw:
        # โค้ดสำหรับรันบน Render (Linux)
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
        page.set_content(html)
        
        # ปริ้นท์เป็นไฟล์ PDF ในหน่วยความจำ (Bytes)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "20px", "bottom": "20px"})
        browser.close()
        
        return pdf_bytes
