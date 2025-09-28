from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string
import requests
import re
import base64
from datetime import datetime

MAILOSAUR_API_KEY = "rYLQU89mwhfgpbtKF1MPsjfUyhlDrYbK"
MAILOSAUR_SERVER_ID = "ku2qi8ie"
MAILOSAUR_BASE_URL = "https://mailosaur.com/api/messages"

def write_test_report_txt(file_name="test_report.txt", content=None):
    if content is None:
        content = []
    with open(file_name, "w", encoding="utf-8") as f:
        f.write("Selenium Test Report\n")
        f.write("="*50 + "\n\n")
        for line in content:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {line}\n")
    print(f"Test report saved as {file_name}")

def generate_password():
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*?")
    remaining = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
    password_list = list(upper + lower + digit + special + remaining)
    random.shuffle(password_list)
    return ''.join(password_list)

def generate_phone():
    return f"+977{random.randint(9848000000, 9999999999)}"

def generate_temp_email():
    username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    return f"{username}@{MAILOSAUR_SERVER_ID}.mailosaur.net"

def get_verification_code():
    auth_str = f"{MAILOSAUR_API_KEY}:"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_auth}"}

    for _ in range(72):
        try:
            resp = requests.get(f"{MAILOSAUR_BASE_URL}?server={MAILOSAUR_SERVER_ID}", headers=headers, timeout=10)
            if resp.status_code != 200:
                time.sleep(5)
                continue
            data = resp.json()
            if data["items"]:
                email = data["items"][0]
                body = email.get("text", {}).get("body") or email.get("html", {}).get("body", "")
                match = re.search(r"\b(\d{6})\b", body)
                if match:
                    return match.group(1)
        except:
            time.sleep(5)
    raise Exception("Verification code not received in time")

def signup_test():
    logs = []
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = ChromeService(executable_path="./chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        wait = WebDriverWait(driver, 30)

        email = generate_temp_email()
        password = generate_password()
        phone = generate_phone()
        logs.append(f"Generated credentials:\nEmail: {email}\nPhone: {phone}\nPassword: {password}")

        driver.get("https://authorized-partner.netlify.app/login")
        time.sleep(2)
        logs.append("Opened login page")

        signup_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign Up")))
        signup_link.click()
        time.sleep(1)
        logs.append("Clicked Sign Up link")

        terms_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='checkbox']")))
        driver.execute_script("arguments[0].click();", terms_checkbox)
        time.sleep(0.5)
        logs.append("Checked Terms and Conditions")

        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Continue')]")))
        continue_button.click()
        time.sleep(1)
        logs.append("Clicked Continue button")

        wait.until(EC.visibility_of_element_located((By.NAME, "firstName"))).send_keys("Test")
        driver.find_element(By.NAME, "lastName").send_keys("User")
        driver.find_element(By.NAME, "email").send_keys(email)

        try:
            phone_field = driver.find_element(By.NAME, "phoneNumber")
        except:
            phone_field = driver.find_element(By.NAME, "phone")
        phone_field.send_keys(phone)

        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "confirmPassword").send_keys(password)
        logs.append("Filled signup form (first name, last name, email, phone, password, confirm password)")

        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Next')]")))
        next_button.click()
        logs.append("Clicked Next button")

        try:
            confirmation = wait.until(
                EC.visibility_of_element_located((By.XPATH, "//p[contains(text(),'verification') or contains(text(),'email')]"))
            )
            logs.append(f"UI confirmation: {confirmation.text}")
        except:
            logs.append("No UI confirmation found, proceeding anyway")

        verification_code = get_verification_code()
        logs.append(f"Verification code received: {verification_code}")

        code_field = wait.until(EC.element_to_be_clickable((By.NAME, "verificationCode")))
        driver.execute_script("arguments[0].value = '';", code_field)
        for digit in verification_code:
            code_field.send_keys(digit)
            time.sleep(0.3)

        verify_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Verify Code')]")))
        driver.execute_script("arguments[0].click();", verify_button)
        logs.append("Entered verification code and clicked Verify")

        wait.until(EC.visibility_of_element_located((By.NAME, "email"))).send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]")))
        login_button.click()
        logs.append("Logged in with new credentials")

        wait.until(EC.url_contains("dashboard"))
        logs.append("Successfully landed on dashboard page")

    except Exception as e:
        logs.append(f"Error during signup/login: {e}")
    finally:
        driver.quit()
        write_test_report_txt(content=logs)

if __name__ == "__main__":
    signup_test()
