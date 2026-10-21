import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

# ==========================================
# YAHAN APNI DETAILS DALNA
# ==========================================
YOUR_EMAIL = "usamazulfiqar121@gmail.com"       # <-- Yahan apna Gmail address likhein (quotes ke andar)
APP_PASSWORD = "imtjltarxccuiwfq"        # <-- Yahan wo 16-letters ka password likhein (bina spaces ke)
# ==========================================

URL = "https://pk-gr-services.gvcworld.eu/appointments/add"

def send_email_alert():
    print("Sending Email Alert...")
    msg = MIMEText("🚨 GVC Alert: Slot khula ho sakta hai! Foran website check karein.")
    msg['Subject'] = 'GVC Appointment Alert!'
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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Opening website...")
        
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(5000) 
            
            content = page.content().lower()
            
            if "no appointment" in content or "no slot" in content:
                print("Abhi koi slot available nahi hai.")
            else:
                print("Slot available lag raha hai! Email bhej rahe hain.")
                send_email_alert()
                
        except Exception as e:
            print("Error aya (shayad site block kar rahi hai):", e)
        
        browser.close()

if __name__ == "__main__":
    check_slots()
  
