import ast
import os
import random
import selenium.common.exceptions
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

# with open(f"{level_up_directory_path}/.env", "r") as file:
#     lines = file.readlines()

# for line in lines:
#     if "SLACK_CHANNEL_ID" in line:
#         channels = ast.literal_eval(line.split("=")[-1][:-1])
    # elif "LINKEDIN_TABLE_URL" in line:
    #     linkedin_table_url = line[17:-1]
    # elif "CLIENT_ID" in line:
    #     os.environ["CLIENT_ID"] = line.split("=")[-1][:-1]
    # elif "CLIENT_SECRET" in line:
    #     os.environ["CLIENT_SECRET"] = line.split("=")[-1][:-1]
    # elif "CLIENT_EMAIL" in line:
    #     os.environ["CLIENT_EMAIL"] = line.split("=")[-1][:-1]
    # elif "CLIENT_PASSWORD" in line:
    #     os.environ["CLIENT_PASSWORD"] = line.split("=")[-1][:-1]
    # elif "REDIRECT_URI" in line:
    #     os.environ["REDIRECT_URI"] = line.split("=")[-1][:-1]
    # elif "SLACK_BOT_TOKEN" in line:
    #     os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    # elif "SLACK_SIGNING_SECRET" in line:
    #     os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]
    # elif "NOTION_TOKEN" in line:
    #     os.environ["NOTION_TOKEN"] = line.split("=")[-1][:-1]
    # elif "REFRESH_TOKEN" in line:
    #     os.environ["REFRESH_TOKEN"] = line.split("=")[-1][:-1]

os.environ["NOTION_TOKEN"] = 'secret_o1kyubNpJ5XKD5pSVq8OLmq8KC2F64wAAa1GVWdczyQ'
os.environ["CLIENT_ID"] = '1c3cc82d1b899a9ee1e44681f1c43514'
os.environ["CLIENT_PASSWORD"] = 'MTA3NjQ2NjkxNC4x'
os.environ["CLIENT_SECRET"] = 'fe9bec427ad322bf'
os.environ["REFRESH_TOKEN"] = 'oauth2v2_a3bad6b405587c05889a6d8b2b6ec9aa'

from cron_jobs.helpers import scroll_page_down
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from notion.notion_table_scraper import scrape_notion_table
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client
from cron_jobs.helpers import (
    find_new_job_openings,
    remove_unactive_jobs_from_db,
    remove_job_from_db,
)


def scrape_linkedin(company_url):
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
    driver.get(company_url)

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
        return ''

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
    return jobs


def is_company_url_valid(url: str):
    url = url[:-1] if url.endswith("/") else url
    if 'https://www.linkedin.com/company' in url:
        pattern = 'https://www.linkedin.com/company'
    elif 'http://www.linkedin.com/company' in url:
        pattern = 'http://www.linkedin.com/company'
    else:
        return False
    if '/' in url.replace(pattern, ''):
        return False
    return True



chrome_options = webdriver.ChromeOptions()
lat = round(random.uniform(-90, 90), 6)
lng = round(random.uniform(-180, 180), 6)
chrome_options.add_argument(f"--geolocation={lat},{lng}")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.set_window_size(800, 600)

url = "https://www.linkedin.com/company/pelico-io/"
# url = "https://www.linkedin.com/company/job-extractor-test/"
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



encountered_errors = []
projects_data = scrape_notion_table("https://www.notion.so/5d4eacbaa8dc46f1b51881f0c4b9461e?v=076d9f6f84854e15ada49ec3480cc3ce")

jobs = []
for company_data in projects_data:
    company_url = company_data["url"]
    if not is_company_url_valid(company_url):
        encountered_errors.append(f"Url {company_url} doesn't look like pattern http://www.linkedin.com/company/ + company name")
        continue
    company_title = company_data["title"]
    company_jobs = scrape_linkedin(company_url)
    if company_jobs == '':
        jobs.append({"company": company_title, "jobs": "error during scraping"})
        continue
    new_company_jobs = find_new_job_openings(company_jobs, origin="linkedin")
    jobs.append({"company": company_title, "jobs": new_company_jobs})

remove_unactive_jobs_from_db(jobs, origin="linkedin")

sys.path.pop(0)
