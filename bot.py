import smtplib
import os
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# ==========================================
# APNI DETAILS YAHAN HAIN
# ==========================================
YOUR_EMAIL = "usamazulfiqar121@gmail.com"       
APP_PASSWORD = "imtjltarxccuiwfq" # <-- Yahan apna Gmail App Password dalein

SURNAME = "ALI"
NAME = "USAMA"
PASSPORT = "FX1838181"
DOB = "10/04/2000" 
PHONE = "3044295713" 

START_AFTER_DAYS = 6 # Aaj se 6 din baad ki date se check karna shuru karega
# ==========================================

URL = "https://pk-gr-services.gvcworld.eu/appointments/add"
COUNTER_FILE = "date_counter.txt" 

def send_email_alert(date_checked):
    print(f"SLOT MIL GAYA! Email bhej rahe hain for date: {date_checked}")
    # Date ko acha format dena (e.g. 28-10-2026)
    date_obj = datetime.strptime(date_checked, "%Y-%m-%d")
    display_date = date_obj.strftime("%d-%m-%Y")
    
    msg = MIMEText(f"🚨 GVC Alert: Slot khula hai!\n\nDate: {display_date}\nForan website check karein: {URL}")
    msg['Subject'] = f'GVC Alert: Slot on {display_date}'
    msg['From'] = YOUR_EMAIL
    msg['To'] = YOUR_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(YOUR_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print("Email send nahi hui:", e)

def check_slots():
    days_ahead = START_AFTER_DAYS
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            days_ahead = int(f.read().strip())
    
    if days_ahead >= 60:
        days_ahead = START_AFTER_DAYS

    check_date = datetime.now() + timedelta(days=days_ahead)
    date_str_html = check_date.strftime("%Y-%m-%d") 
    
    print(f"Checking for date: {date_str_html}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(6000) # Page load hone ka wait

            # 1. Visa Type Select karna
            try:
                page.locator("select").first.select_option(label="Long-Term Type D (Seasonal/Dependent Employment)")
                page.wait_for_timeout(2000)
            except:
                pass # Agar default selected hai to koi masla nahi

            # 2. Details fill karna
            try:
                page.locator("input[type='email']").fill(YOUR_EMAIL)
                page.locator("input[type='tel']").fill(PHONE)
                
                text_inputs = page.locator("input[type='text']")
                if text_inputs.count() >= 3:
                    text_inputs.nth(0).fill(SURNAME)
                    text_inputs.nth(1).fill(NAME)
                    text_inputs.nth(2).fill(PASSPORT) 
                print("Form details filled.")
            except Exception as e:
                print("Form fill error:", e)

            # 3. Date dalna
            try:
                date_input = page.locator("input[type='date']").first
                date_input.fill(date_str_html)
                page.wait_for_timeout(1000)
            except:
                print("Date field error.")

            # 4. Search Button dabana
            try:
                page.locator("text=Search").first.click()
                page.wait_for_timeout(6000) # Result load hone ka wait
            except:
                print("Search button error.")

            # 5. Result check karna (Green Box)
            content = page.content().lower()
            
            if "available appointments" in content:
                print(f"✅ SLOT AVAILABLE: {date_str_html}")
                send_email_alert(date_str_html)
            elif "cannot book an appointment" in content or "please choose another date" in content:
                print(f"❌ Nahi hai slot yahan: {date_str_html}")
            else:
                print(f"⚠️ Page load hua lekin status samajh nahi aya.")

        except Exception as e:
            print("Main Error:", e)
        
        browser.close()

    # Counter update karein taake agle 15 min baad agli date check ho
    with open(COUNTER_FILE, "w") as f:
        f.write(str(days_ahead + 1))

if __name__ == "__main__":
    check_slots()
