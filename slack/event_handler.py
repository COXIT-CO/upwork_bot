import ast
import dotenv
import os
import subprocess
import threading
from app.app import flask_app
from helpers import exceptions
from notion.notion_table_scraper import scrape_notion_table
from slack.app import slack_bot_app
from slack.utils import build_blocks_given_job_openings
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
    setup_cron_job()
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
    dotenv.set_key(".env", "JOBS", str(jobs))
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


def setup_cron_job():
    subprocess.Popen(["crontab", "-r"])
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
    cmd = f"python {level_up_directory_path}/cron-jobs/cron_job_openings.py"
    subprocess.Popen("echo '0 */6 * * * {}' | crontab -".format(cmd), shell=True)


@slack_bot_app.command("/subscribe")
def subscribe(ack, body):
    channel_id = body["channel_id"]
    notion_table_url = body["text"]  # extract notion table url provided by user
    os.environ['SLACK_CHANNEL_ID'] = channel_id
    os.environ['NOTION_TABLE_URL'] = notion_table_url
    dotenv.set_key(".env", "SLACK_CHANNEL_ID", channel_id)
    dotenv.set_key(".env", "NOTION_TABLE_URL", notion_table_url)
    threading.Thread(target=handle_subscription, args=(notion_table_url,)).start()
    ack()


@slack_bot_app.action("modal_window_handler")
def handle_some_action(ack, body, payload, client):
    ack()
    if "value" in payload:
        jobs_to_list = ast.literal_eval(payload["value"])
    else:
        jobs_to_list = ast.literal_eval(os.getenv("JOBS"))
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "modal_window_callback",
            "title": {"type": "plain_text", "text": "New job openings"},
            "blocks": build_blocks_given_job_openings(jobs_to_list),
        },
    )
