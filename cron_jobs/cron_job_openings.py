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


from helpers import exceptions
from slack_bolt import App
from notion.notion_table_scraper import scrape_notion_table
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client
from cron_jobs.helpers import (
    find_new_job_openings,
    remove_unactive_jobs_from_db,
    remove_job_from_db,
    delete_arg_from_file,
    write_arg_to_env_file,
    post_slack_message
)

slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)


def delete_jobs_from_env_file():
    with open(level_up_directory_path + "/.env", "r") as file:
        lines = file.readlines()

    filtered_lines = [line for line in lines if "JOBS" not in line]

    with open(level_up_directory_path + "/.env", "w") as file:
        file.writelines(filtered_lines)


upwork_client.refresh_access_token_data()

encountered_errors = []
projects_data = scrape_notion_table(notion_table_url)
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

            new_job_openings = find_new_job_openings(other_opened_jobs, origin="upwork")
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
                "action_id": "modal_window_handler",
                "text": {"type": "plain_text", "text": "Watch them"},
                "style": "primary",
            }
        ],
    }
    if len(str(jobs)) > 2000:
        delete_arg_from_file("JOBS", file_path=level_up_directory_path + "/.env")
        write_arg_to_env_file("JOBS", jobs, file_path=level_up_directory_path + "/.env")
    else:
        modal_window["elements"][0]["value"] = str(jobs)
    blocks.append(modal_window)
    post_slack_message(channels, slack_bot_app, blocks, encountered_errors)

sys.path.pop(0)
