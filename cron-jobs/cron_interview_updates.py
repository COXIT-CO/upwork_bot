import ast
import os
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

with open(f"{level_up_directory_path}/.env", "r") as file:
    lines = file.readlines()

for line in lines:
    if "SLACK_CHANNEL_ID" in line:
        channels = ast.literal_eval(line.split("=")[-1][:-1])
    elif "CLIENT_EMAIL" in line:
        os.environ["CLIENT_EMAIL"] = line.split("=")[-1][:-1]
    elif "CLIENT_PASSWORD" in line:
        os.environ["CLIENT_PASSWORD"] = line.split("=")[-1][:-1]
    elif "SLACK_BOT_TOKEN" in line:
        os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    elif "SLACK_SIGNING_SECRET" in line:
        os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]

from app.app import flask_app
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slack.app import slack_bot_app
from upwork_part.schema.controllers import InvitationController
from upwork_part.schema.models import Invitation
from webdriver_manager.chrome import ChromeDriverManager

invitation_controller = InvitationController()


def find_new_invitations(invitation_controller, invitations):
    new_invitations = []
    for inv in invitations:
        invitation_link = inv["link"]
        with flask_app.app_context():
            invitation = invitation_controller.get(invitation_link)
        if not invitation:
            # invitation is new, so save it to db
            with flask_app.app_context():
                invitation_controller.create(invitation_link)
            new_invitations.append(inv)
    return new_invitations


def remove_unavailable_invitations_from_db(invitation_controller, invitations):
    with flask_app.app_context():
        invitations_from_bd = Invitation.query.all()

    for inv_db in invitations_from_bd:
        inv_db_link = inv_db.url
        for inv in invitations:
            inv_link = inv["link"]
            if inv_db_link == inv_link:
                break
        else:
            with flask_app.app_context():
                invitation_controller.delete(inv_db_link)


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

driver.get("https://www.upwork.com/ab/proposals/")

# Find the email form element and fill it in
email = driver.find_element(By.ID, "login_username")
email.send_keys(os.getenv("CLIENT_EMAIL"))
email.send_keys(Keys.RETURN)

# # Find the next button and click it
submit_button = driver.find_element(By.ID, "login_password_continue")
submit_button.click()

password_field = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.ID, "password"))
)

password = driver.find_element(By.ID, "login_password")
password.send_keys(os.getenv("CLIENT_PASSWORD"))

next_button = driver.find_element(By.ID, "login_control_continue")
next_button.click()

WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "up-proposals-list__block"))
)

soup = BeautifulSoup(driver.page_source, "html.parser")
invitations_block = soup.find("div", {"data-qa": "card-active-proposals"}).find(
    "div", {"class": "up-proposals-list__block"}
)

invitations = []

for invitation in invitations_block.contents:
    invitation_content = invitation.contents[0]
    div_with_link = [item for item in invitation_content.contents if item != " "][-1]
    a_tag = div_with_link.find("a")
    link = "https://www.upwork.com" + a_tag.get("href")
    text = a_tag.text
    invitations.append({"link": link, "text": text})


new_invitations = find_new_invitations(invitation_controller, invitations)
remove_unavailable_invitations_from_db(invitation_controller, invitations)


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
        slack_bot_app.client.chat_postMessage(channel=chan, blocks=blocks)

sys.path.pop(0)
