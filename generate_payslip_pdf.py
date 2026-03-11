import os
import base64
from playwright.sync_api import sync_playwright

def get_base64_font(font_path):
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode("utf-8")

def generate_payslip_pdf_bytes(info):
    
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
            body {{ font-family: 'THSarabunNew', sans-serif; font-size: 16px; margin: 0; padding: 20px; color: #000; }}
            .header-title {{ text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
            
            /* ส่วนข้อมูลพนักงาน */
            .emp-info {{ width: 100%; margin-bottom: 15px; border-collapse: collapse; }}
            .emp-info td {{ padding: 4px; vertical-align: bottom; }}
            .border-bottom {{ border-bottom: 1px dotted #000; padding-left: 5px; }}

            /* ตารางหลัก 3 ส่วน */
            .main-table {{ width: 100%; border-collapse: collapse; border: 2px solid #000; }}
            .main-table th, .main-table td {{ border: 1px solid #000; padding: 6px 10px; vertical-align: top; }}
            .main-table th {{ background-color: #f0f0f0; text-align: center; font-weight: bold; }}
            
            .right {{ text-align: right; }}
            .center {{ text-align: center; }}
            .bold {{ font-weight: bold; }}
            
            /* โซนสรุปยอดสุทธิ */
            .summary-table {{ width: 100%; border-collapse: collapse; border: 2px solid #000; border-top: none; }}
            .summary-table td {{ padding: 10px; border: 1px solid #000; }}
            .net-pay-box {{ font-size: 20px; font-weight: bold; background-color: #e6e6e6; }}
            
            .footer {{ margin-top: 30px; display: flex; justify-content: space-between; text-align: center; }}
            .sign-box {{ width: 45%; }}
        </style>
    </head>
    <body>
        <div class="header-title">ใบแจ้งยอดเงินเดือน / PAY SLIP</div>
        
        <table class="emp-info">
            <tr>
                <td width="15%">รหัสพนักงาน:</td><td width="35%" class="border-bottom">{info.get("emp_id", "-")}</td>
                <td width="15%">ตำแหน่ง:</td><td width="35%" class="border-bottom">{info.get("position", "-")}</td>
            </tr>
            <tr>
                <td>ชื่อ-นามสกุล:</td><td class="border-bottom">{info.get("employee_name", "-")}</td>
                <td>แผนก:</td><td class="border-bottom">{info.get("department", "-")}</td>
            </tr>
            <tr>
                <td>วันที่จ่าย:</td><td class="border-bottom">{info.get("pay_date", "-")}</td>
                <td>งวดที่:</td><td class="border-bottom">{info.get("period", "-")}</td>
            </tr>
        </table>

        <table class="main-table">
            <thead>
                <tr>
                    <th colspan="2" width="34%">รายได้ (INCOME)</th>
                    <th colspan="2" width="33%">รายการหัก (DEDUCTION)</th>
                    <th colspan="2" width="33%">ยอดสะสม (YTD)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>เงินเดือน</td><td class="right">{info.get("salary","0.00")}</td>
                    <td>ภาษี</td><td class="right">{info.get("tax","0.00")}</td>
                    <td>รายได้สะสม</td><td class="right">{info.get("ytd_income","0.00")}</td>
                </tr>
                <tr>
                    <td>ค่าล่วงเวลา (OT)</td><td class="right">{info.get("ot_amount","0.00")}</td>
                    <td>ประกันสังคม</td><td class="right">{info.get("sso","0.00")}</td>
                    <td>ภาษีสะสม</td><td class="right">{info.get("ytd_tax","0.00")}</td>
                </tr>
                <tr>
                    <td>รายได้อื่นๆ</td><td class="right">{info.get("other_income","0.00")}</td>
                    <td>ขาด/ลา/มาสาย</td><td class="right">{info.get("absent","0.00")}</td>
                    <td>ประกันสังคมสะสม</td><td class="right">{info.get("ytd_sso","0.00")}</td>
                </tr>
                <tr>
                    <td></td><td class="right"></td>
                    <td>รายการหักอื่นๆ</td><td class="right">{info.get("other_deduct","0.00")}</td>
                    <td></td><td class="right"></td>
                </tr>
                <tr style="height: 40px;"> <td></td><td></td><td></td><td></td><td></td><td></td>
                </tr>
            </tbody>
        </table>
        
        <table class="summary-table">
            <tr class="bold">
                <td width="17%" class="center">รวมรายได้</td><td width="17%" class="right">{info.get("income_sum","0.00")}</td>
                <td width="16%" class="center">รวมรายการหัก</td><td width="17%" class="right">{info.get("deduction_sum","0.00")}</td>
                <td width="17%" class="center net-pay-box">เงินได้สุทธิ</td><td width="16%" class="right net-pay-box">{info.get("net_pay","0.00")}</td>
            </tr>
        </table>

        <div class="footer">
            <div class="sign-box">
                <br><br>
                ________________________________<br>
                ผู้จ่ายเงิน
            </div>
            <div class="sign-box">
                <br><br>
                ________________________________<br>
                ผู้รับเงิน / พนักงาน
            </div>
        </div>
    </body>
    </html>
    """

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4", print_background=True, margin={"top": "10px", "bottom": "10px", "left": "10px", "right": "10px"})
        browser.close()
        return pdf_bytes
