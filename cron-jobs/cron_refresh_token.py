import os
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

with open(level_up_directory_path + "/.env", "r") as file:
    lines = file.readlines()

for line in lines:
    if "CLIENT_ID" in line:
        os.environ["CLIENT_ID"] = line.split("=")[-1][:-1]
    elif "CLIENT_SECRET" in line:
        os.environ["CLIENT_SECRET"] = line.split("=")[-1][:-1]
    elif "CLIENT_EMAIL" in line:
        os.environ["CLIENT_EMAIL"] = line.split("=")[-1][:-1]
    elif "CLIENT_PASSWORD" in line:
        os.environ["CLIENT_PASSWORD"] = line.split("=")[-1][:-1]
    elif "REDIRECT_URI" in line:
        os.environ["REDIRECT_URI"] = line.split("=")[-1][:-1]

import upwork
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"--user-agent={USER_AGENT}")

driver = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=chrome_options
)

upwork_config = upwork.Config(
    {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "redirect_uri": os.getenv("REDIRECT_URI"),
    }
)

client = upwork.Client(upwork_config)
authorization_url, _ = client.get_authorization_url()

driver.get(authorization_url)

# Find the email form element and fill it in
email = driver.find_element(By.ID, "login_username")
email.send_keys(os.getenv("CLIENT_EMAIL"))
email.send_keys(Keys.RETURN)

# # Find the next button and click it
email_submit_button = driver.find_element(By.ID, "login_password_continue")
email_submit_button.click()

password_field = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.ID, "password"))
)

password = driver.find_element(By.ID, "login_password")
password.send_keys(os.getenv("CLIENT_PASSWORD"))

password_submit_button = driver.find_element(By.ID, "login_control_continue")
password_submit_button.click()
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "header__logo"))
)

token_data = dict(client.get_access_token(driver.current_url))


with open(level_up_directory_path + "/.env", "r") as file:
    lines = file.readlines()

filtered_lines = [line for line in lines if "REFRESH_TOKEN" not in line]

with open(level_up_directory_path + "/.env", "w") as file:
    file.writelines(filtered_lines)
    file.write(f"REFRESH_TOKEN={token_data['refresh_token']}\n")


with open(level_up_directory_path + "/.env", "r") as file:
    lines = file.readlines()

# Close the browser
driver.quit()

sys.path.pop(0)
