import ast
import os
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


from helpers import exceptions
from slack_bolt import App
from notion.notion_table_scraper import scrape_notion_table
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client
from helpers.db import (
    find_new_job_openings,
    remove_unactive_jobs_from_db,
    remove_job_from_db,
)
from helpers.slack import post_slack_message
from helpers.file import delete_arg_from_file, write_arg_to_file

slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)


upwork_client.refresh_access_token_data()

for chan in channels:
    encountered_errors = []
    projects_data = scrape_notion_table(slack_channels_data[chan]["upwork_table_url"])
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
                remove_job_from_db(job_url)
            else:
                active_jobs.append(job_url)
                for job in other_opened_jobs:
                    active_jobs.append(job["job_url"])

                new_job_openings = find_new_job_openings(
                    chan, other_opened_jobs, origin="upwork"
                )
                if len(new_job_openings):
                    # new job openings appeared for origin one
                    serialized_job_info["other_opened_jobs"] = new_job_openings
                    jobs.append(serialized_job_info)
        except exceptions.CustomException as exc:
            encountered_errors.append(str(exc))

    # if client doesn't have a job or some jobs anymore remove it from DB
    remove_unactive_jobs_from_db(active_jobs, origin="upwork")

    if jobs:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hey! I have new *upwork* job openings for you :eyes:",
                },
            }
        ]
        modal_window = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "action_id": "upwork_handler",
                    "text": {"type": "plain_text", "text": "Watch them"},
                    "style": "primary",
                }
            ],
        }
        if len(str(jobs)) > 2000:
            slack_channels_data[chan]["upwork_jobs"]
        else:
            modal_window["elements"][0]["value"] = str(jobs)
        blocks.append(modal_window)
        post_slack_message(chan, slack_bot_app, blocks, encountered_errors)

delete_arg_from_file("SLACK_CHANNELS_DATA", file_path=f"{ROOT_DIR}/.env")
write_arg_to_file(
    "SLACK_CHANNELS_DATA", slack_channels_data, file_path=f"{ROOT_DIR}/.env"
)

sys.path.pop(0)
