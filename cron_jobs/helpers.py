import os
import re
import selenium.webdriver
import sys
import time

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
from slack_bolt import App

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


def remove_unactive_jobs_from_db(companies_data, origin, companies: list[str] = None):
    with flask_app.app_context():
        db_jobs = JobModel.query.filter_by(origin=origin).all()
    
    if origin == "linkedin":
        # remove jobs which were posted by companies currently not having active jobs
        for job in db_jobs:
            url = job.job_url
            title = transform_company_title(extract_company_title(url))
            for company in companies:
                if title == company:
                    break
            else:
                with flask_app.app_context():
                    job_controller.delete(url)

        with flask_app.app_context():
            db_jobs = JobModel.query.filter_by(origin=origin).all()

        for job in db_jobs:
            url = job.job_url
            job_company_title = transform_company_title(extract_company_title(url))
            for comp_data in companies_data:
                if comp_data['company_title'] == job_company_title:
                    comp_jobs = comp_data['jobs']
                    for job in comp_jobs:
                        job_url = job['job_url']
                        if job_url == url:
                            break
                    else:
                        if comp_jobs == 'error during scraping':
                            continue
                        with flask_app.app_context():
                            job_controller.delete(url)
        return ""

    for job in db_jobs:
        url = job.job_url
        origin = job.origin
        is_job_available = False
        for job_url in companies_data:
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


def scroll_page_down(driver: selenium.webdriver):
    """given selenium webdriver instance scroll the current html page driver is on down"""
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
    time.sleep(1)


def transform_company_title(title: str):
    title = re.sub(r'[-.]', '', title.lower())
    return title


def extract_company_title(url: str):
    """given a link on linkedin job extract a company title"""
    url = url[:-1] if url.endswith("/") else url
    title = url.replace('https://www.linkedin.com/company/', '').replace('http://www.linkedin.com/company/', '')
    return title


def transform_job_url(url: str):
    """given linkedin job url change the company name to that one without special symbols like - or ."""
    url = url[:-1] if url.endswith("/") else url
    title = extract_company_title(url)
    # title = url.replace('https://www.linkedin.com/company/', '').replace('http://www.linkedin.com/company/', '')
    if 'https://www.linkedin.com/company/' in url:
        url = 'http://www.linkedin.com/company/' + title
    elif 'http://www.linkedin.com/company/' in url:
        url = 'http://www.linkedin.com/company/' + title
    return url


def is_company_url_valid(url: str):
    """given link to a linkedin company validate it and return the result of whether the link is correct or not"""
    url = url[:-1] if url.endswith("/") else url
    if 'https://www.linkedin.com/company/' in url:
        pattern = 'https://www.linkedin.com/company/'
    elif 'http://www.linkedin.com/company' in url:
        pattern = 'http://www.linkedin.com/company/'
    else:
        return False
    if '/' in url.replace(pattern, ''):
        return False
    return True


def delete_arg_from_file(arg_name, file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    filtered_lines = [line for line in lines if arg_name not in line]

    with open(file_path, "w") as file:
        file.writelines(filtered_lines)


def write_arg_to_env_file(arg_name, data_to_write, file_path):
    with open(file_path, "r") as file:
            lines = file.readlines()
    with open(file_path, "w") as file:
        lines.append(f"{arg_name}={str(data_to_write)}\n")
        file.writelines(lines)


def post_slack_message(channels, slack_bot_app: App, blocks, encountered_errors):
    for chan in channels:
        response = slack_bot_app.client.chat_postMessage(
            channel=chan, blocks=blocks, thread_ts=""
        )
        response_timestamp = response["ts"]
        for err in encountered_errors:
            slack_bot_app.client.chat_postMessage(
                channel=chan, text=err, thread_ts=response_timestamp
            )
