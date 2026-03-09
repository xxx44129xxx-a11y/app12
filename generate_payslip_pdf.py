from playwright.sync_api import sync_playwright

def generate_payslip_pdf_bytes(info):
    # วาง HTML Template ดีไซน์สลิปของคุณตรงนี้ (เหมือนไฟล์ที่ส่งมา)
    html = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8" />
        <style>
            body {{ font-family: 'THSarabunNew', sans-serif; }}
            /* ใส่ CSS สลิปเงินเดือนของคุณ */
        </style>
    </head>
    <body>
        <h2>ใบสลิปเงินเดือน ประจำเดือน {info.get("month", "")}</h2>
        <p>ชื่อพนักงาน: {info.get("employee_name", "")}</p>
        <p>เงินเดือน: {info.get("salary", "0")}</p>
        <p>รับสุทธิ: {info.get("net_pay", "0")}</p>
    </body>
    </html>
    """

    with sync_playwright() as pw:
        # เปิด Browser แบบ Headless ให้รองรับเซิร์ฟเวอร์ Linux ของ Render
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
        page.set_content(html)
        
        # ปริ้นท์เป็น PDF แล้วส่งเป็น bytes กลับไปให้ Streamlit
        pdf_bytes = page.pdf(format="A4", print_background=True)
        browser.close()
        
        return pdf_bytes