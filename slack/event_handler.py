import ast

# import dotenv
import os
import subprocess
import threading
from app.app import flask_app
from helpers import exceptions
from notion.notion_table_scraper import scrape_notion_table
from slack.app import slack_bot_app
from slack.utils import build_blocks_given_job_openings, build_blocks_given_invitations
from upwork_part.schema.controllers import JobController
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client


def handle_subscription(notion_table_url):
    """event handler to user subscription"""
    try:
        projects_data = scrape_notion_table(notion_table_url)
    except exceptions.CustomException as exc:
        slack_bot_app.client.chat_postMessage(
            channel=os.getenv("SLACK_CHANNEL_ID"), text=str(exc)
        )
        return ""
    setup_cron_jobs()
    jobs = []
    for job_data in projects_data:
        job_url = job_data["url"]
        job_title = job_data["title"]
        try:
            job = Job(job_url).get_job(upwork_client.receive_upwork_client())
            serialized_job_info = job.serialize_job()
            save_jobs_to_db(serialized_job_info)
            serialized_job_info["job_title"] = job_title
            jobs.append(serialized_job_info)
        except exceptions.CustomException as exc:
            slack_bot_app.client.chat_postMessage(
                channel=os.getenv("CHANNEL_ID"),
                text=str(exc),
            )
    # dotenv.set_key(".env", "JOBS", str(jobs))
    os.environ["JOBS"] = str(jobs)
    slack_bot_app.client.chat_postMessage(
        channel=os.getenv("SLACK_CHANNEL_ID"),
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hi! I have new job openings for you :eyes:",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "modal_window_handler",
                        "text": {"type": "plain_text", "text": "Watch them"},
                        "style": "primary",
                    }
                ],
            },
        ],
    )


def save_jobs_to_db(serialized_job_data):
    job_controller = JobController()
    job_url = serialized_job_data["job_url"]
    with flask_app.app_context():
        job_controller.create(job_url)
        for job_data in serialized_job_data["other_opened_jobs"]:
            job_controller.create(job_data["job_url"])


def setup_cron_jobs(level_up_directory_path):
    # # subprocess.Popen(["crontab", "-r"])
    # job_openings_cron_job = (
    #     f"python {level_up_directory_path}/cron-jobs/cron_job_openings.py"
    # )
    # cron_jobs = f"* * * * * {job_openings_cron_job}\n"
    # subprocess.Popen(f"echo 'abc' > abc.txt", shell=True)  # {level_up_directory_path}/crontab")
    subprocess.Popen(f'echo "* * * * * root python {level_up_directory_path}/cron-jobs/test.py\n\
# Don\'t remove the empty line at the end of this file. It is required to run the cron job" > /etc/cron.d/hello-cron', shell=True)
    subprocess.Popen("crontab -f", shell=True)
#     subprocess.Popen(f'echo "* * * * * root python {level_up_directory_path}/cron-jobs/cron_job_openings.py\n\
# # Don\'t remove the empty line at the end of this file. It is required to run the cron job" > /etc/cron.d/hello-cron', shell=True)
#     subprocess.Popen("cron -f", shell=True)
    # # subprocess.Popen(f"echo '{cron_jobs}' | crontab -", shell=True)


@slack_bot_app.command("/subscribe")
def subscribe(ack, body):
    channel_id = body["channel_id"]
    notion_table_url = body["text"]  # extract notion table url provided by user
    # os.environ["SLACK_CHANNEL_ID"] = channel_id
    # os.environ["NOTION_TABLE_URL"] = notion_table_url
    # dotenv.set_key(".env", "SLACK_CHANNEL_ID", channel_id)
    # dotenv.set_key(".env", "NOTION_TABLE_URL", notion_table_url)
    # os.environ["SLACK_CHANNEL_ID"] = channel_id
    # os.environ["NOTION_TABLE_URL"] = notion_table_url
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
    with open("/app/.env", "w") as file:
        file.write(f"SLACK_CHANNEL_ID={channel_id}\n")
        file.write(f"NOTION_TABLE_URL={notion_table_url}\n")
        file.write(f"SLACK_CHANNEL_ID={os.getenv('SLACK_CHANNEL_ID')}\n")
        file.write(f"SLACK_SIGNING_SECRET={os.getenv('SLACK_SIGNING_SECRET')}\n")
        file.write(f"SLACK_BOT_TOKEN={os.getenv('SLACK_BOT_TOKEN')}\n")
        file.write(f"CLIENT_ID={os.getenv('CLIENT_ID')}\n")
        file.write(f"CLIENT_SECRET={os.getenv('CLIENT_SECRET')}\n")
        file.write(f"CLIENT_EMAIL={os.getenv('CLIENT_EMAIL')}\n")
        file.write(f"CLIENT_PASSWORD={os.getenv('CLIENT_PASSWORD')}\n")
        file.write(f"REDIRECT_URI={os.getenv('REDIRECT_URI')}\n")
        file.write(f"NOTION_TOKEN={os.getenv('NOTION_TOKEN')}\n")
        file.write(f"REFRESH_TOKEN={os.getenv('REFRESH_TOKEN')}\n")
    # subprocess.Popen(
    #     f"python {level_up_directory_path}/cron-jobs/cron_job_openings.py", shell=True
    # )
    subprocess.Popen(
        f"/usr/local/bin/python /app/cron-jobs/cron_job_openings.py",
        shell=True,
    )
    # setup_cron_jobs(level_up_directory_path)
    # threading.Thread(target=handle_subscription, args=(notion_table_url,)).start()
    ack()


@slack_bot_app.action("modal_window_handler")
def handle_job_openings(ack, body, payload, client):
    ack()
    if "value" in payload:
        jobs_to_list = ast.literal_eval(payload["value"])
    else:
        with open("/app/jobs", "r") as file:
            lines = file.readlines()
        jobs = "".join(lines)[5:]
        jobs_to_list = ast.literal_eval(jobs)
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "modal_window_callback",
            "title": {"type": "plain_text", "text": "New job openings"},
            "blocks": build_blocks_given_job_openings(jobs_to_list),
        },
    )


@slack_bot_app.action("invitations_handler")
def handle_invitations(ack, body, client, payload):
    ack()
    invitations = ast.literal_eval(payload["value"])
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "invitations_callback",
            "title": {"type": "plain_text", "text": "New invitations"},
            "blocks": build_blocks_given_invitations(invitations),
        },
    )
