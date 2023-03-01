import ast
import os
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
#     elif "CLIENT_EMAIL" in line:
#         os.environ["CLIENT_EMAIL"] = line.split("=")[-1][:-1]
#     elif "CLIENT_PASSWORD" in line:
#         os.environ["CLIENT_PASSWORD"] = line.split("=")[-1][:-1]
#     elif "SLACK_BOT_TOKEN" in line:
#         os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
#     elif "SLACK_SIGNING_SECRET" in line:
#         os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]
#     elif "LOGIN_ANSWER" in line:
#         os.environ["LOGIN_ANSWER"] = line.split("=")[-1][:-1]

from bs4 import BeautifulSoup
from cron_jobs.helpers import find_new_invitations, remove_unactive_invitations_from_db, scroll_page_down, authorize_user
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"

chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(f"--user-agent={USER_AGENT}")

driver = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=chrome_options
)
# this is default maximum window size opening on digitalocean, so use this as a constant
driver.set_window_size(800, 600)

url = "https://www.linkedin.com/company/job-extractor-test/"
# url = "https://www.linkedin.com/company/xperi-inc/"
url = url + "/" if not url.endswith("/") else url
# url = "https://www.linkedin.com/company/xperi-inc/"
if not (url.endswith("jobs/") or url.endswith("jobs")):
    url += "jobs/"


driver.get(url)
input()
cookies = driver.get_cookies()
driver.quit()

driver = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=chrome_options
)
for cookie in cookies:
    driver.add_cookie(cookie)

driver.get(url)
input()
# input()

# driver.get(url)
authorize_user(driver)
input()
driver.get(url)
authorize_user(driver)
driver.get(url)

try:
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "org-jobs-recently-posted-jobs-module__show-all-jobs-btn"))
    )
    see_jobs_link = driver.find_element(By.CLASS_NAME, "org-jobs-recently-posted-jobs-module__show-all-jobs-btn")
    see_job_link = see_jobs_link.find_elements(By.TAG_NAME, "a")[-1].get_attribute("href")
    driver.get(see_job_link)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "jobs-search-results-list\n    \n    "))
    )
    div_to_scroll = driver.find_element(By.CLASS_NAME, "jobs-search-results-list\n    \n    ")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "artdeco-pagination__pages"))
    )
    ul_list = driver.find_element(By.CLASS_NAME, "artdeco-pagination__pages")
    # print(div_to_scroll)
    # driver.execute_script("window.scrollBy(0, 1000)")
    # input()
    # driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", div_to_scroll)
    # scroll_page_down(driver)
    print("ok")
    li_elems = ul_list.find_elements(By.CLASS_NAME, "artdeco-pagination__indicator")
    for li in li_elems[1:]:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "./button[@type='button']"))
        )
        print("here")
        next_page_button = li.find_element(By.TAG_NAME, "button")
        next_page_button.click()
        # pass
    input()
    print(li_elems)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "artdeco-pagination__pages artdeco-pagination__pages--number"))
    )
    print(driver.find_element(By.CLASS_NAME, "artdeco-pagination__pages artdeco-pagination__pages--number"))
    # print(see_jobs_link.get_attribute("href"))
    print("ok")
    # input()
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']"))
    )
    sign_in_button = driver.find_element(By.XPATH, "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']")
    sign_in_button.click()

    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@class='input__input' and @id='session_key']"))
    )
    email_field = driver.find_element(By.XPATH, "//input[@class='input__input' and @id='session_key']")
    email_field.send_keys("lnkdnjobextract@gmail.com")
    # email_field.send_keys(Keys.RETURN)

    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@class='input__input' and @id='session_password']"))
    )
    password_field = driver.find_element(By.XPATH, "//input[@class='input__input' and @id='session_password']")
    password_field.send_keys("m@PNfFPP2hSTdAWv")
    password_field.send_keys(Keys.RETURN)
except selenium.common.exceptions.TimeoutException:
    pass
input()


# try:
#     WebDriverWait(driver, 20).until(
#         EC.visibility_of_element_located((By.CLASS_NAME, "focus-page"))
#     )
#     # input()
#     WebDriverWait(driver, 20).until(
#         EC.visibility_of_element_located((By.XPATH, "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']"))
#     )
#     sign_in_button = driver.find_element(By.XPATH, "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']")
#     sign_in_button.click()

#     WebDriverWait(driver, 20).until(
#         EC.visibility_of_element_located((By.XPATH, "//input[@class='input__input' and @id='session_key']"))
#     )
#     email_field = driver.find_element(By.XPATH, "//input[@class='input__input' and @id='session_key']")
#     email_field.send_keys("lnkdnjobextract@gmail.com")
#     # email_field.send_keys(Keys.RETURN)

#     WebDriverWait(driver, 20).until(
#         EC.visibility_of_element_located((By.XPATH, "//input[@class='input__input' and @id='session_password']"))
#     )
#     password_field = driver.find_element(By.XPATH, "//input[@class='input__input' and @id='session_password']")
#     password_field.send_keys("m@PNfFPP2hSTdAWv")
#     password_field.send_keys(Keys.RETURN)
# except selenium.common.exceptions.TimeoutException:
#     pass

# driver.get(url)

print("1")
WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "top-card-layout__cta-container"))
)
print("2")
see_jobs_link = driver.find_element(By.XPATH, "//a[@class='top-card-layout__cta mt-2 ml-1.5 h-auto babybear:flex-auto top-card-layout__cta--primary btn-md btn-primary']")
print(see_jobs_link.get_attribute("href"))
driver.get(see_jobs_link.get_attribute("href"))
print("2")


# driver.get(url)


jobs = []
with open("log_next.html", "w") as f:
    f.write(driver.page_source)
print("1")
# input()
WebDriverWait(driver, 20).until(
    # EC.visibility_of_element_located((By.XPATH, "//section[@class='core-rail mx-auto papabear:w-core-rail-width mamabear:max-w-[790px] babybear:max-w-[790px]']/div[@class='details mx-details-container-padding']"))
    EC.presence_of_element_located((By.XPATH, "//section[@class='core-rail mx-auto papabear:w-core-rail-width mamabear:max-w-[790px] babybear:max-w-[790px]']/div[@class='details mx-details-container-padding']//div[@class='core-section-container__content break-words']"))
    # EC.visibility_of_element_located((By.XPATH, "//div[@class='core-section-container__content break-words']"))
)
print("ok")
scroll_page_down(driver)
ul_elem = driver.find_elements(By.XPATH, "//section[@class='core-rail mx-auto papabear:w-core-rail-width mamabear:max-w-[790px] babybear:max-w-[790px]']/div[@class='details mx-details-container-padding']//div[@class='core-section-container__content break-words']/ul/li")
for elem in ul_elem:
    job_link = elem.find_element(By.XPATH, "./div/a")
    # WebDriverWait(driver, 20).until(
    #     # EC.visibility_of_element_located((By.XPATH, "./div/div/h3"))
    #     EC.presence_of_element_located((By.XPATH, ".//h3"))
    #     # EC.visibility_of_element_located((By.XPATH, "//div[@class='core-section-container__content break-words']"))
    # )
    # WebDriverWait(driver, 20).until(
    #     # EC.visibility_of_element_located((By.XPATH, "./div/div/h3"))
    #     EC.visibility_of_element_located((By.XPATH, ".//h3"))
    #     # EC.visibility_of_element_located((By.XPATH, "//div[@class='core-section-container__content break-words']"))
    # )
    job_title = elem.find_element(By.XPATH, ".//h3")
    # print(job_link.screenshot())
    # print(job_title.text)
    print(job_title.get_attribute("innerText"))
    # print(type(job_title))
    # break
    # print(job_title)
print("ok")

try:
    input()
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "core-section-container__content break-words"))
    )
    print("2")
    jobs_list = driver.find_element(By.CLASS_NAME, "core-section-container__content break-words")
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # scroll down the page until all the elements are loaded
    scroll_page_down(driver)
    print("3")

    # ul_element = driver.find_element_by_xpath("//ul[@class='jobs-search__results-list']")
    ul_element = driver.find_element(By.XPATH, "//div[@class='core-section-container__content break-words']/ul")
    print(ul_element)
    li_elements = ul_element.find_elements(By.XPATH, "./li")
    for li in li_elements:
        job_link = li.find_element(By.XPATH, "./div/a")
        job_title = li.find_element(By.XPATH, "./div/div/h3")
    jobs_block = soup.find("ul", {"class": "jobs-search__results-list"})
    for job in jobs_block:
        div_element = job.find_element()
        a_element = div_element.find_element_by_xpath(".//a")
        link = a_element.get_attribute("href")
        # print(invitation.find("a"))
        break
        # invitation_content = invitation.contents[0]
        # print(invitation_content)
        # div_with_link = [item for item in invitation_content.contents if item != " "][-1]
        # a_tag = div_with_link.find("a")
        # invitation_link = "https://www.upwork.com" + a_tag.get("href")
        # link_text = a_tag.text
        # invitations.append({"link": invitation_link, "text": link_text})
    # print("ok")
except selenium.common.exceptions.TimeoutException:
    pass





input()
WebDriverWait(driver, 10)
print(driver.window_handles)

WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "org-jobs-recently-posted-jobs-module__show-all-jobs-btn"))
)
print("abc")
see_all_jobs_link = driver.find_element(By.CLASS_NAME, "org-jobs-recently-posted-jobs-module__show-all-jobs-btn")
print(see_all_jobs_link.text)


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
        slack_bot_app.client.chat_postMessage(channel=chan, blocks=blocks)

sys.path.pop(0)
