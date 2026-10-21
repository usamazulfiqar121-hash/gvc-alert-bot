import smtplib
import os
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# ==========================================
# APNI DETAILS YAHAN HAIN
# ==========================================
YOUR_EMAIL = "usamazulfiqar121@gmail.com"       
APP_PASSWORD = "imtjltarxccuiwfq" 

SURNAME = "ALI"
NAME = "USAMA"
PASSPORT = "FX1838181"
PHONE = "3044295713" 

START_AFTER_DAYS = 6  
TOTAL_DAYS_TO_CHECK = 60 
# ==========================================

URL = "https://pk-gr-services.gvcworld.eu/appointments/add"
COUNTER_FILE = "date_counter.txt" 

def send_email_alert(date_checked):
    print(f"SLOT MIL GAYA! Email bhej rahe hain for date: {date_checked}")
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
        try:
            with open(COUNTER_FILE, "r") as f:
                days_ahead = int(f.read().strip())
        except:
            days_ahead = START_AFTER_DAYS
    
    if days_ahead >= (START_AFTER_DAYS + TOTAL_DAYS_TO_CHECK):
        days_ahead = START_AFTER_DAYS

    check_date = datetime.now() + timedelta(days=days_ahead)
    date_str_html = check_date.strftime("%Y-%m-%d") 
    
    print(f"Checking for date: {date_str_html} (Day {days_ahead} from today)")

    with sync_playwright() as p:
        # Hum bot ko insaan banane ke liye custom user-agent use kar rahe hain
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(8000) # Zyada wait taake security check clear ho jaye

            # Screenshot lein ke website ne kya dikhaya
            page.screenshot(path="website_view.png")
            print("Screenshot saved.")

            # Form fill karne ki koshish karein (agar form aya ho)
            try:
                # Email box
                page.locator("input[type='email']").fill(YOUR_EMAIL, timeout=5000)
                page.locator("input[type='tel']").fill(PHONE, timeout=5000)
                page.locator("input[type='text']").nth(0).fill(SURNAME, timeout=5000)
                page.locator("input[type='text']").nth(1).fill(NAME, timeout=5000)
                page.locator("input[type='text']").nth(2).fill(PASSPORT, timeout=5000) 
                print("✅ Form details filled successfully.")
            except Exception as e:
                print("❌ Form fill error. Website ne form nahi dikhaya (Block ho gaya shayad).")

            # Date dalna
            try:
                date_input = page.locator("input[type='date']").first
                date_input.fill(date_str_html)
                date_input.press("Enter") 
                page.wait_for_timeout(2000)
            except:
                print("Date field error.")

            # Search Button
            try:
                page.locator("button:has-text('Search')").first.click()
                page.wait_for_timeout(8000) 
            except:
                print("Search button error.")

            # Search ke baad screenshot
            page.screenshot(path="after_search.png")

            # Result check karna
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

    with open(COUNTER_FILE, "w") as f:
        f.write(str(days_ahead + 1))

if __name__ == "__main__":
    check_slots()
