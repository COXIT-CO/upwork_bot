import ast
import os
import random
import selenium.common.exceptions
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()
current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

with open(f"{ROOT_DIR}/.env", "r") as file:
    lines = file.readlines()

for line in lines:
    if "SLACK_CHANNELS_DATA" in line:
        slack_channels_data = ast.literal_eval(line[20:-1])
        channels = [chan for chan in slack_channels_data]
    elif "SLACK_BOT_TOKEN" in line:
        os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    elif "SLACK_SIGNING_SECRET" in line:
        os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]
    elif "NOTION_TOKEN" in line:
        os.environ["NOTION_TOKEN"] = line.split("=")[-1][:-1]


from helpers.db import find_new_job_openings, remove_unactive_jobs_from_db
from helpers.slack import post_slack_message
from helpers.file import delete_arg_from_file, write_arg_to_file
from helpers.linkedin import paginate_jobs, scroll_page_down, is_company_url_valid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slack_bolt import App
from webdriver_manager.chrome import ChromeDriverManager
from helpers import linkedin

from notion.notion_table_scraper import scrape_notion_table

slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)


def scrape_linkedin_without_authentication(driver: webdriver.Chrome, company_url):
    """given linkedin company url scrape all its jobs and return them"""
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
        return ""

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
        job_url = (
            "https://www.linkedin.com/jobs/view/" + job_url.split("?")[0].split("-")[-1]
        )
        job_title = elem.find_element(By.XPATH, ".//h3").get_attribute("innerText")
        jobs.append({"job_url": job_url, "job_title": job_title})
    return jobs


def authenticate_in_linkedin(driver: webdriver.Chrome, email, password):
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']",
            )
        )
    )
    sigh_in_button = driver.find_element(
        By.XPATH,
        "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']",
    )
    sigh_in_button.click()

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//input[@autocomplete='username']",
            )
        )
    )
    email_input_field = driver.find_element(
        By.XPATH, "//input[@autocomplete='username']"
    )
    email_input_field.send_keys(email)

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//input[@autocomplete='current-password']",
            )
        )
    )
    password_field = driver.find_element(
        By.XPATH, "//input[@autocomplete='current-password']"
    )
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)


def extract_company_jobs(driver: webdriver.Chrome):
    jobs = []
    while True:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//div[@class='jobs-search-results-list\n    \n    ']",
                )
            )
        )
        time.sleep(2)

        active_page_jobs_div_elem = driver.find_element(
            By.XPATH, "//div[@class='jobs-search-results-list\n    \n    ']"
        )
        # scroll the div elements with jobs listing slowly to let all li elements be populated with job link and title
        for _ in range(15):
            driver.execute_script(
                "arguments[0].scrollTop += 500;", active_page_jobs_div_elem
            )
            time.sleep(0.1)

        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//div[@class='jobs-search-results-list\n    \n    ']//ul[@class='scaffold-layout__list-container']",
                )
            )
        )
        jobs_list_elem = active_page_jobs_div_elem.find_element(
            By.XPATH,
            "//div[@class='jobs-search-results-list\n    \n    ']//ul[@class='scaffold-layout__list-container']",
        )

        WebDriverWait(driver, 5).until(
            EC.visibility_of_all_elements_located(
                (
                    By.XPATH,
                    "//div[@class='jobs-search-results-list\n    \n    ']//ul[@class='scaffold-layout__list-container']/li[@class='ember-view   jobs-search-results__list-item occludable-update p0 relative scaffold-layout__list-item\n              \n              \n              ']",
                )
            )
        )
        job_li_elems = jobs_list_elem.find_elements(
            By.XPATH,
            "//li[@class='ember-view   jobs-search-results__list-item occludable-update p0 relative scaffold-layout__list-item\n              \n              \n              ']",
        )

        for li in job_li_elems:
            a_elem = li.find_element(By.TAG_NAME, "a")
            job_url = linkedin.extract_job_title(a_elem.get_attribute("href"))
            splitted_job_url = job_url.split("/")
            for i, val in enumerate(splitted_job_url):
                if val == "view":
                    break
            job_url = "https://www.linkedin.com/jobs/view/" + splitted_job_url[i + 1]
            jobs.append(
                {
                    "job_url": job_url,
                    "job_title": a_elem.text,
                }
            )

        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//ul[@class='artdeco-pagination__pages artdeco-pagination__pages--number']",
                    )
                )
            )
        except selenium.common.exceptions.TimeoutException:
            return jobs

        next_pages_ul_elem = driver.find_element(
            By.XPATH,
            "//ul[@class='artdeco-pagination__pages artdeco-pagination__pages--number']",
        )
        next_pages_li_elems = next_pages_ul_elem.find_elements(By.TAG_NAME, "li")
        for i, next_page_li in enumerate(next_pages_li_elems.copy()):
            class_name = next_page_li.get_attribute("class")
            if "active" in class_name:
                next_pages_li_elems = next_pages_li_elems[i + 1 :]
        if len(next_pages_li_elems) == 0:
            return jobs
        next_page_btn = next_pages_li_elems[0].find_element(By.TAG_NAME, "button")
        next_page_btn.click()


def scrape_linkedin_with_authentication(
    driver: webdriver.Chrome, company_url: str, email: str, password: str
):
    """given linkedin company url scrape all its jobs and return them"""
    driver.get(company_url)
    try:
        authenticate_in_linkedin(driver, email, password)
    except selenium.common.exceptions.TimeoutException:
        pass

    if "/jobs" not in company_url:
        company_url = company_url[:-1] if company_url.endswith("/") else company_url
        company_url += "/jobs"
    driver.get(company_url)

    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//div[@class='org-jobs-recently-posted-jobs-module__show-all-jobs-btn']",
                )
            )
        )
    except selenium.common.exceptions.TimeoutException:
        return ""
    see_all_jobs_div_elem = driver.find_element(
        By.XPATH,
        "//div[@class='org-jobs-recently-posted-jobs-module__show-all-jobs-btn']",
    )
    jobs_page_link_elem = see_all_jobs_div_elem.find_element(By.TAG_NAME, "a")
    all_jobs_page_link = jobs_page_link_elem.get_attribute("href")
    driver.get(all_jobs_page_link)

    jobs = extract_company_jobs(driver)
    return jobs


from selenium import webdriver
from selenium_stealth import stealth

options = webdriver.ChromeOptions()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
lat = round(random.uniform(-90, 90), 6)
lng = round(random.uniform(-180, 180), 6)
options.add_argument(
    f"--geolocation={lat},{lng}"
)  # provide geolocation to make requests out of random location
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument(f"--user-agent={USER_AGENT}")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.set_window_size(800, 600)

stealth(
    driver,
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
)

LINKEDIN_ACCOUNTS = {
    "lnkdnjobextract@gmail.com": "m@PNfFPP2hSTdAWv",
    "lnkdnjobextract3@gmail.com": "m@PNfFPP2hSTdAWv",
}

for chan in channels:
    channel_lookup_key = chan
    if isinstance(chan, tuple):
        channel_lookup_key = chan[0]
    elif isinstance(chan, str):
        channel_lookup_key = chan
    encountered_errors = []
    companies_data = []

    projects_data = scrape_notion_table(slack_channels_data[chan]["linkedin_table_url"])
    for company_data in projects_data:
        url = company_data["url"]
        if not is_company_url_valid(url):
            encountered_errors.append(
                f"{url} doesn't look like pattern http://www.linkedin.com/company/ + company name"
            )
            continue
        title = company_data["title"]
        for email, password in LINKEDIN_ACCOUNTS.items():
            company_jobs = scrape_linkedin_without_authentication(driver, url)
            if company_jobs == "":
                company_jobs = scrape_linkedin_with_authentication(
                    driver, url, email, password
                )
            if company_jobs == "":
                continue
            new_company_jobs = find_new_job_openings(
                channel_lookup_key, company_jobs, origin="linkedin"
            )
            if new_company_jobs != "":
                companies_data.append(
                    {
                        "company_title": title,
                        "company_url": url,
                        "jobs": new_company_jobs,
                    }
                )
            break

    splitted_jobs = paginate_jobs(companies_data)
    remove_unactive_jobs_from_db(channel_lookup_key, companies_data, origin="linkedin")

    are_there_new_jobs = False
    for item in splitted_jobs:
        for company_data in item:
            if len(company_data["jobs"]):
                are_there_new_jobs = True
                break
        if are_there_new_jobs:
            break

    if are_there_new_jobs:
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

        if len(str(splitted_jobs)) > 2000:
            slack_channels_data[chan]["linkedin_jobs"] = splitted_jobs
            slack_channels_data[chan]["current_linkedin_jobs_page"] = "0"
        else:
            modal_window["elements"][0]["value"] = str(splitted_jobs)
        blocks.append(modal_window)
        post_slack_message(
            channel_lookup_key, slack_bot_app, blocks, encountered_errors
        )

delete_arg_from_file("SLACK_CHANNELS_DATA", file_path=f"{ROOT_DIR}/.env")
write_arg_to_file(
    "SLACK_CHANNELS_DATA", slack_channels_data, file_path=f"{ROOT_DIR}/.env"
)
sys.path.pop(0)
