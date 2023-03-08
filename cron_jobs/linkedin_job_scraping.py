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
    elif "LINKEDIN_TABLE_URL" in line:
        linkedin_table_url = line[17:-1]
    elif "SLACK_BOT_TOKEN" in line:
        os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    elif "SLACK_SIGNING_SECRET" in line:
        os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]
    elif "NOTION_TOKEN" in line:
        os.environ["NOTION_TOKEN"] = line.split("=")[-1][:-1]
    elif "REFRESH_TOKEN" in line:
        os.environ["REFRESH_TOKEN"] = line.split("=")[-1][:-1]


from cron_jobs.helpers import (
    scroll_page_down,
    is_company_url_valid,
    transform_company_title,
    find_new_job_openings,
    remove_unactive_jobs_from_db,
    delete_arg_from_file,
    write_arg_to_env_file,
    post_slack_message
)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slack_bolt import App
from webdriver_manager.chrome import ChromeDriverManager

from notion.notion_table_scraper import scrape_notion_table
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client


slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)


def scrape_linkedin(company_url):
    """given linkedin company url scrape all its jobs and return them"""
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"

    chrome_options = webdriver.ChromeOptions()
    lat = round(random.uniform(-90, 90), 6)
    lng = round(random.uniform(-180, 180), 6)
    chrome_options.add_argument(f"--geolocation={lat},{lng}")   # provide geolocation to make requests out of random location
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-agent={USER_AGENT}")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.set_window_size(800, 600)   # tied to production window size (in docker the maximum window resolution is 800x600)
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
        # in case company doesn't have active jobs return empty string
        return ''

    jobs_page_link = driver.find_element(
        By.XPATH,
        "//a[@class='top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--primary btn-md btn-primary']",
    )
    driver.get(jobs_page_link.get_attribute("href"))

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
    )
    scroll_page_down(driver)
    
    ul_block = driver.find_element(By.CLASS_NAME, "jobs-search__results-list")
    jobs_block = ul_block.find_elements(By.XPATH, "./li")
    jobs = []
    for elem in jobs_block:
        job_url = elem.find_element(By.XPATH, "./div/a").get_attribute("href")
        job_title = elem.find_element(By.XPATH, ".//h3").get_attribute("innerText")
        jobs.append({"job_url": job_url, "job_title": job_title})
    return jobs


encountered_errors = []
companies_data = []
companies = []

projects_data = scrape_notion_table("https://www.notion.so/5d4eacbaa8dc46f1b51881f0c4b9461e?v=076d9f6f84854e15ada49ec3480cc3ce")
for company_data in projects_data:
    url = company_data["url"]
    if not is_company_url_valid(url):
        encountered_errors.append(f"{url} doesn't look like pattern http://www.linkedin.com/company/ + company name")
        continue
    title = company_data["title"]
    companies.append(transform_company_title(title))
    company_jobs = scrape_linkedin(url)
    if company_jobs == '':
        companies_data.append({"title": title, "jobs": "error during scraping"})
        continue
    new_company_jobs = find_new_job_openings(company_jobs, origin="linkedin")
    companies_data.append({"company_title": title, "company_url": url, "jobs": new_company_jobs})

remove_unactive_jobs_from_db(companies_data, origin="linkedin", companies=companies)

do_new_jobs_exist = False
for comp_data in companies_data:
    if comp_data['jobs'] != 'error during scraping':
        do_new_jobs_exist = True
        break

if do_new_jobs_exist:
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Hey! I have new *linkedin* job openings for you :eyes:",
            },
        }
    ]
    modal_window = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "action_id": "linkedin_handler",
                "text": {"type": "plain_text", "text": "Watch them"},
                "style": "primary",
            }
        ],
    }

    if len(str(companies_data)) > 2000:
        delete_arg_from_file("LINKEDIN_JOBS", file_path=level_up_directory_path + "/.env")
        write_arg_to_env_file("LINKEDIN_JOBS", companies_data, file_path=level_up_directory_path + "/.env")
    else:
        modal_window["elements"][0]["value"] = str(companies_data)
    blocks.append(modal_window)
    post_slack_message(channels, slack_bot_app, blocks, encountered_errors)

sys.path.pop(0)
