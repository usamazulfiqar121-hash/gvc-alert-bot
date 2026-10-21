import time
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright

# ==========================================
# APNI DETAILS YAHAN HAIN
# ==========================================
YOUR_EMAIL = "usamazulfiqar121@gmail.com"       
APP_PASSWORD = "imtjltarxccuiwfq" # <-- Yahan apna Gmail App Password dalein

SURNAME = "ALI"
NAME = "USAMA"
DOB = "10/04/2000"  # Screenshot mein date month/day format mein lag rahi thi, agar 4 October hai to 04/10/2000 kar lein
PASSPORT = "FX1838181"
# ==========================================

URL = "https://pk-gr-services.gvcworld.eu/appointments/add"

# Categories jo check karni hain (Schengen Short Term nikal diya gaya hai)
CATEGORIES_TO_CHECK = [
    "Long-Term Type D (Seasonal/Dependent Employment)",
    "National visa (Long-term - type D)",
    "Premium Lounge (optional service at an additional charge)",
    "Prime Time (optional service at an additional charge)"
]

def send_email_alert(category_name):
    print(f"Slot Mila! Email bhej rahe hain for: {category_name}")
    msg = MIMEText(f"🚨 GVC Alert: Slot khula hai!\n\nCategory: {category_name}\nForan website check karein: {URL}")
    msg['Subject'] = f'GVC Alert: {category_name}'
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
        print("Website open ho rahi hai...")
        
        try:
            page.goto(URL, timeout=60000)
            page.wait_for_timeout(5000) # 5 second wait

            for category in CATEGORIES_TO_CHECK:
                print(f"Checking category: {category}...")
                
                try:
                    # 1. Category select karein (Dropdown)
                    page.select_option("select", label=category)
                    page.wait_for_timeout(2000)

                    # 2. Details bharein (Selectors may vary, using placeholder/text logic)
                    # Surname, Name, DOB, Passport fill karne ki koshish
                    inputs = page.query_selector_all("input")
                    text_inputs = [i for i in inputs if i.get_attribute("type") == "text" or i.get_attribute("type") == "date"]
                    
                    # Note: Website ke design ke mutabiq in fields ko fill karna thoda tricky hai, 
                    # hum basic fill kar rahe hain
                    if len(text_inputs) >= 3:
                        text_inputs[0].fill(SURNAME)
                        text_inputs[1].fill(NAME)
                        # Date field alag hoti hai, skip for now
                        text_inputs[-1].fill(PASSPORT)

                    page.wait_for_timeout(1000)

                    # 3. Search Button dabayein
                    search_btn = page.locator("text=Search").first
                    if search_btn:
                        search_btn.click()
                        page.wait_for_timeout(5000) # Result ka wait
                    
                    # 4. Result check karein
                    content = page.content().lower()
                    
                    if "cannot book an appointment" in content or "please choose another date" in content:
                        print(f"Nahi hai slot yahan: {category}")
                    elif "available appointments" in content or "please select time slot" in content:
                        print(f"🚨 SLOT MIL GAYA: {category}")
                        send_email_alert(category)
                        break # Slot mil gaya to loop rok dein
                    else:
                        print(f"Website ka response samajh nahi aya: {category}")

                except Exception as e:
                    print(f"Error in category {category}: {e}")
                    continue # Agli category try karein
                
        except Exception as e:
            print("Main Page Error:", e)
        
        browser.close()

if __name__ == "__main__":
    check_slots()
