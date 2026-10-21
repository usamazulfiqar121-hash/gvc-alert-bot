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
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(6000) 

            # SABSE AHEM: Screenshot lein taake hum dekh sakein website kaisi khul rahi hai
            page.screenshot(path="website_view.png")
            print("Screenshot saved as website_view.png")

            # 1. Visa Type Select karna
            try:
                page.locator("select").first.select_option(label="Long-Term Type D (Seasonal/Dependent Employment)")
                page.wait_for_timeout(2000)
            except:
                pass 

            # 2. Details fill karna (Aasan tareeqa)
            try:
                # Placeholder ya name se dhoondne ki koshish
                page.get_by_placeholder("E-mail").fill(YOUR_EMAIL)
            except:
                print("Email field nahi mili.")
                
            try:
                page.locator("input[type='text']").nth(0).fill(SURNAME)
                page.locator("input[type='text']").nth(1).fill(NAME)
                page.locator("input[type='text']").nth(2).fill(PASSPORT) 
                print("Form details filled.")
            except Exception as e:
                print("Form fill error:", e)

            # 3. Date dalna aur Enter dabana
            try:
                date_input = page.locator("input[type='date']").first
                date_input.fill(date_str_html)
                date_input.press("Enter") 
                page.wait_for_timeout(1000)
            except:
                print("Date field error.")

            # 4. Search Button dabana 
            try:
                # Text ke bajaye button tag se dhoondna
                page.locator("button:has-text('Search')").first.click()
                page.wait_for_timeout(8000) 
            except:
                print("Search button error.")

            # 5. Search ke baad dobara screenshot lein
            page.screenshot(path="after_search.png")
            print("After search screenshot saved.")

            # 6. Result check karna (Green Box)
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

    # Counter update karein
    with open(COUNTER_FILE, "w") as f:
        f.write(str(days_ahead + 1))

if __name__ == "__main__":
    check_slots()
