import os

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
import dotenv

dotenv.load_dotenv(level_up_directory_path + "/.env")
import sys

sys.path.insert(0, level_up_directory_path)
from app.app import flask_app
from notion.notion_table_scraper import scrape_notion_table
from slack.app import slack_bot_app
from helpers import exceptions
from upwork_part.schema.controllers import JobController
from upwork_part.schema.models import Job as JobModel
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client


def delete_jobs_from_env_file():
    with open(level_up_directory_path + "/.env", "r") as file:
        lines = file.readlines()
    with open(level_up_directory_path + "/.env", "w") as file:
        for line in lines:
            if "JOBS" not in line:
                file.write(line)


def find_new_job_openings(job_controller, opened_jobs):
    new_job_openings = []
    for job in opened_jobs:
        job_url = job["job_url"]
        with flask_app.app_context():
            job_object = job_controller.get(job_url)
        if not job_object:
            # job is new, so save it to db
            with flask_app.app_context():
                job_controller.create(job_url)
            new_job_openings.append(job)
    return new_job_openings


def remove_unavailable_jobs_from_db(job_controller, currently_available_jobs):
    with flask_app.app_context():
        jobs_in_db = JobModel.query.all()

    for job in jobs_in_db:
        job_key = job.job_key
        is_db_job_available = False
        for job_url in currently_available_jobs:
            if job_key in job_url:
                is_db_job_available = True

        if not is_db_job_available:
            with flask_app.app_context():
                job_controller.delete(job_key)


def remove_job_from_db(job_controller: JobController, job_url: str):
    job_key = job_url.split("~")[-1]
    with flask_app.app_context():
        job_controller.delete(job_key)


def run():
    upwork_client.refresh_access_token_data()

    projects_data = scrape_notion_table(os.getenv("NOTION_TABLE_URL"))
    job_controller = JobController()
    jobs = []
    currently_available_jobs = []
    for job_data in projects_data:
        job_url = job_data["url"]
        job_title = job_data["title"]
        try:
            job = Job(job_url).get_job(
                upwork_client.receive_upwork_client()
            )  # line potentially causing error
            serialized_job_info = job.serialize_job()
            serialized_job_info["job_title"] = job_title
            other_opened_jobs = serialized_job_info["other_opened_jobs"]
            # remove origin job from database as it doesn't have other jobs opened
            if len(other_opened_jobs) == 0:
                remove_job_from_db(job_controller, job_url)
            else:
                currently_available_jobs.append(job_url)
                for job in other_opened_jobs:
                    currently_available_jobs.append(job["job_url"])

                new_job_openings = find_new_job_openings(
                    job_controller, other_opened_jobs
                )
                if len(new_job_openings):
                    # new job openings appeared for origin one
                    serialized_job_info["other_opened_jobs"] = new_job_openings
                    jobs.append(serialized_job_info)
        except exceptions.CustomException as exc:
            slack_bot_app.client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL_ID"),
                text=str(exc),
            )

    # if client doesn't have a job or some jobs anymore remove it from DB
    remove_unavailable_jobs_from_db(job_controller, currently_available_jobs)
    if jobs:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hey! I have new job openings for you :eyes:",
                },
            }
        ]
        modal_window = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "action_id": "modal_window_handler",
                    "text": {"type": "plain_text", "text": "Watch them"},
                    "style": "primary",
                }
            ],
        }
        if len(str(jobs)) > 2000:
            delete_jobs_from_env_file()
            dotenv.set_key(level_up_directory_path + "/.env", "JOBS", str(jobs))
        else:
            modal_window["elements"][0]["value"] = str(jobs)
        blocks.append(modal_window)
        slack_bot_app.client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL_ID"), blocks=blocks
        )


run()
sys.path.pop(0)
