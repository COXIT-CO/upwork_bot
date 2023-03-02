import ast
import os
import random
import selenium.common.exceptions
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

with open(f"{level_up_directory_path}/.env", "r") as file:
    lines = file.readlines()

for line in lines:
    if "SLACK_CHANNEL_ID" in line:
        channels = ast.literal_eval(line.split("=")[-1][:-1])
    elif "SLACK_BOT_TOKEN" in line:
        os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    elif "SLACK_SIGNING_SECRET" in line:
        os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]

from cron_jobs.helpers import scroll_page_down
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = webdriver.ChromeOptions()
lat = round(random.uniform(-90, 90), 6)
lng = round(random.uniform(-180, 180), 6)
chrome_options.add_argument(f"--geolocation={lat},{lng}")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.set_window_size(800, 600)

url = "https://www.linkedin.com/company/pelico-io/"
driver.get(url)

try:
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//a[@class='top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--primary btn-md btn-primary']",
            )
        )
    )
except selenium.common.exceptions.TimeoutException:
    sys.exit()

see_jobs_link = driver.find_element(
    By.XPATH,
    "//a[@class='top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--primary btn-md btn-primary']",
)
driver.get(see_jobs_link.get_attribute("href"))

WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
)
scroll_page_down(driver)
jobs_ul_block = driver.find_element(By.CLASS_NAME, "jobs-search__results-list")
jobs_block = jobs_ul_block.find_elements(By.XPATH, "./li")
jobs = []
for elem in jobs_block:
    job_link = elem.find_element(By.XPATH, "./div/a").get_attribute("href")
    job_title = elem.find_element(By.XPATH, ".//h3").get_attribute("innerText")
    jobs.append({"link": job_link, "title": job_title})

sys.path.pop(0)
