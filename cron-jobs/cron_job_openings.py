import ast
import os
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

with open(level_up_directory_path + "/.env", "r") as file:
    lines = file.readlines()

for line in lines:
    if "SLACK_CHANNEL_ID" in line:
        channels = ast.literal_eval(line.split("=")[-1][:-1])
    elif "NOTION_TABLE_URL" in line:
        notion_table_url = line[17:-1]
    elif "CLIENT_ID" in line:
        os.environ["CLIENT_ID"] = line.split("=")[-1][:-1]
    elif "CLIENT_SECRET" in line:
        os.environ["CLIENT_SECRET"] = line.split("=")[-1][:-1]
    elif "CLIENT_EMAIL" in line:
        os.environ["CLIENT_EMAIL"] = line.split("=")[-1][:-1]
    elif "CLIENT_PASSWORD" in line:
        os.environ["CLIENT_PASSWORD"] = line.split("=")[-1][:-1]
    elif "REDIRECT_URI" in line:
        os.environ["REDIRECT_URI"] = line.split("=")[-1][:-1]
    elif "SLACK_BOT_TOKEN" in line:
        os.environ["SLACK_BOT_TOKEN"] = line.split("=")[-1][:-1]
    elif "SLACK_SIGNING_SECRET" in line:
        os.environ["SLACK_SIGNING_SECRET"] = line.split("=")[-1][:-1]
    elif "NOTION_TOKEN" in line:
        os.environ["NOTION_TOKEN"] = line.split("=")[-1][:-1]
    elif "REFRESH_TOKEN" in line:
        os.environ["REFRESH_TOKEN"] = line.split("=")[-1][:-1]


from app.app import flask_app
from helpers import exceptions
from slack_bolt import App
from notion.notion_table_scraper import scrape_notion_table
from upwork_part.schema.controllers import JobController
from upwork_part.schema.models import Job as JobModel
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client

slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)


def delete_jobs_from_env_file():
    with open(level_up_directory_path + "/.env", "r") as file:
        lines = file.readlines()

    filtered_lines = [line for line in lines if "JOBS" not in line]

    with open(level_up_directory_path + "/.env", "w") as file:
        file.writelines(filtered_lines)


def find_new_job_openings(job_controller: JobController, opened_jobs, origin):
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


def remove_unavailable_jobs_from_db(job_controller: JobController, active_jobs, origin):
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


def remove_job_from_db(job_controller: JobController, job_url: str):
    with flask_app.app_context():
        job_controller.delete(job_url)


upwork_client.refresh_access_token_data()

projects_data = scrape_notion_table(notion_table_url)
job_controller = JobController()
jobs = []
active_jobs = []
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
            active_jobs.append(job_url)
            for job in other_opened_jobs:
                active_jobs.append(job["job_url"])

            new_job_openings = find_new_job_openings(job_controller, other_opened_jobs, origin="upwork")
            if len(new_job_openings):
                # new job openings appeared for origin one
                serialized_job_info["other_opened_jobs"] = new_job_openings
                jobs.append(serialized_job_info)
    except exceptions.CustomException as exc:
        for chan in channels:
            slack_bot_app.client.chat_postMessage(
                channel=chan,
                text=str(exc),
            )

# if client doesn't have a job or some jobs anymore remove it from DB
remove_unavailable_jobs_from_db(job_controller, active_jobs, origin="upwork")
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
        with open(level_up_directory_path + "/.env", "w") as file:
            file.write(f"JOBS={str(jobs)}\n")
    else:
        modal_window["elements"][0]["value"] = str(jobs)
    blocks.append(modal_window)
    for chan in channels:
        slack_bot_app.client.chat_postMessage(channel=chan, blocks=blocks)

sys.path.pop(0)
