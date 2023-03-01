import os
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

from app.app import flask_app
from upwork_part.schema.controllers import JobController
from upwork_part.schema.controllers import InvitationController
from upwork_part.schema.models import Job as JobModel
from upwork_part.schema.models import Invitation
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
from selenium.webdriver.common.keys import Keys

job_controller = JobController()
invitation_controller = InvitationController()


def find_new_job_openings(opened_jobs, origin):
    new_job_openings = []
    for job in opened_jobs:
        job_url = job["job_url"]
        with flask_app.app_context():
            job_object = job_controller.get(job_url)
        if not job_object:
            # job is new, so save it to db
            with flask_app.app_context():
                job_controller.create(job_url, origin=origin)
            new_job_openings.append(job)
    return new_job_openings


def remove_unactive_jobs_from_db(active_jobs, origin):
    with flask_app.app_context():
        db_jobs = JobModel.query.filter_by(origin=origin).all()

    for job in db_jobs:
        url = job.job_url
        origin = job.origin
        is_job_available = False
        for job_url in active_jobs:
            if url == job_url:
                is_job_available = True

        if not is_job_available:
            with flask_app.app_context():
                job_controller.delete(url)


def remove_job_from_db(job_url: str):
    with flask_app.app_context():
        return job_controller.delete(job_url)


def find_new_invitations(invitations):
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


def remove_unactive_invitations_from_db(invitations):
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



def scroll_page_down(driver):
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        import time
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
    time.sleep(1)


def authorize_user(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "focus-page"))
        )
        # input()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']"))
        )
        sign_in_button = driver.find_element(By.XPATH, "//button[@class='authwall-join-form__form-toggle--bottom form-toggle']")
        sign_in_button.click()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@class='input__input' and @id='session_key']"))
        )
        email_field = driver.find_element(By.XPATH, "//input[@class='input__input' and @id='session_key']")
        email_field.send_keys("lnkdnjobextract@gmail.com")
        # email_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@class='input__input' and @id='session_password']"))
        )
        password_field = driver.find_element(By.XPATH, "//input[@class='input__input' and @id='session_password']")
        password_field.send_keys("m@PNfFPP2hSTdAWv")
        password_field.send_keys(Keys.RETURN)
    except selenium.common.exceptions.TimeoutException:
        pass
