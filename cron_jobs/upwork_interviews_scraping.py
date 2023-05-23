import ast
import os
import selenium.common.exceptions
import sys
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
    elif "CLIENT_EMAIL" in line:
        os.environ["CLIENT_EMAIL"] = line.split("=")[-1][:-1]
    elif "CLIENT_PASSWORD" in line:
        os.environ["CLIENT_PASSWORD"] = line.split("=")[-1][:-1]
    elif "SLACK_BOT_TOKEN" in line:
        os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    elif "SLACK_SIGNING_SECRET" in line:
        os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]
    elif "LOGIN_ANSWER" in line:
        os.environ["LOGIN_ANSWER"] = line.split("=")[-1][:-1]

from bs4 import BeautifulSoup
from helpers.db import find_new_invitations, remove_unactive_invitations_from_db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slack.app import slack_bot_app
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
# this is default maximum window size opening on digitalocean, so use this as a constant
driver.set_window_size(800, 600)

driver.get("https://www.upwork.com/ab/proposals/")


email_input_field = driver.find_element(By.ID, "login_username")
email_input_field.send_keys(os.getenv("CLIENT_EMAIL"))
email_input_field.send_keys(Keys.RETURN)

try:
    email_submit_button = driver.find_element(By.ID, "login_password_continue")
    try:
        email_submit_button.click()
    except selenium.common.exceptions.ElementClickInterceptedException:
        # execute this script if some element covers button
        driver.execute_script("arguments[0].click();", email_submit_button)
except (
    selenium.common.exceptions.NoSuchElementException,
    selenium.common.exceptions.StaleElementReferenceException,
):
    pass


WebDriverWait(driver, 90).until(
    EC.visibility_of_element_located((By.ID, "login_password"))
)
password_input_field = driver.find_element(By.ID, "login_password")
password_input_field.send_keys(os.getenv("CLIENT_PASSWORD"))
password_input_field.send_keys(Keys.RETURN)

try:
    password_submit_button = driver.find_element(By.ID, "login_control_continue")
    try:
        password_submit_button.click()
    except selenium.common.exceptions.ElementClickInterceptedException:
        # execute this script if some element covers button
        driver.execute_script("arguments[0].click();", password_submit_button)
except (
    selenium.common.exceptions.NoSuchElementException,
    selenium.common.exceptions.StaleElementReferenceException,
):
    pass


try:
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.ID, "login_answer"))
    )
    login_answer = driver.find_element(By.ID, "login_answer")
    login_answer.send_keys(os.getenv("LOGIN_ANSWER"))
    login_answer.send_keys(Keys.RETURN)

    login_answer_button = driver.find_element(By.ID, "login_control_continue")
    try:
        login_answer_button.click()
    except selenium.common.exceptions.ElementClickInterceptedException:
        # execute this script if some element covers button
        driver.execute_script("arguments[0].click();", login_answer_button)
except (
    selenium.common.exceptions.NoSuchElementException,
    selenium.common.exceptions.TimeoutException,
    selenium.common.exceptions.StaleElementReferenceException,
):
    pass


try:
    WebDriverWait(driver, 90).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "up-proposals-list__block"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    invitations_block = soup.find("div", {"data-qa": "card-invitations"}).find(
        "div", {"class": "up-proposals-list__block"}
    )
    if invitations_block is None:
        raise selenium.common.exceptions.TimeoutException()
except selenium.common.exceptions.TimeoutException:
    # do nothing if there ae no invitations available
    sys.exit()

invitations = []

for invitation in invitations_block.contents:
    invitation_content = invitation.contents[0]
    div_with_link = [item for item in invitation_content.contents if item != " "][-1]
    a_tag = div_with_link.find("a")
    invitation_link = "https://www.upwork.com" + a_tag.get("href")
    link_text = a_tag.text
    invitations.append({"link": invitation_link, "text": link_text})

new_invitations = find_new_invitations(invitations)
remove_unactive_invitations_from_db(invitations)


blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hey! I have new invitations to an interview for you :eyes:",
        },
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "action_id": "invitations_handler",
                "text": {"type": "plain_text", "text": "Watch them"},
                "style": "primary",
                "value": str(new_invitations),
            }
        ],
    },
]

if len(new_invitations) != 0:
    for chan in channels:
        if "upwork_jobs" in slack_channels_data[chan]:
            channel_lookup_key = chan
            if isinstance(chan, tuple):
                channel_lookup_key = chan[0]
            elif isinstance(chan, str):
                channel_lookup_key = chan
            slack_bot_app.client.chat_postMessage(
                channel=channel_lookup_key, blocks=blocks
            )

sys.path.pop(0)
