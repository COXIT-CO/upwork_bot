import dotenv
import os
import threading
from notion.notion_table_scraper import scrape_notion_table
from slack.app import slack_bot_app
from slack.utils import build_blocks_given_job_openings
from upwork_part.exceptions import CustomException
from upwork_part.upwork_integration import Job
from upwork_part.upwork_integration import upwork_client


def handle_subscription(notion_table_url):
    """event handler to user subscription"""
    projects_data = scrape_notion_table(notion_table_url)
    jobs = []
    for job_data in projects_data:
        job_url = job_data["url"]
        job_title = job_data["title"]
        try:
            job = Job(job_url).get_job(upwork_client.receive_upwork_client())
            serialized_job_info = job.serialize_job()
            serialized_job_info["job_title"] = job_title
            jobs.append(serialized_job_info)
        except CustomException as exc:
            slack_bot_app.client.chat_postMessage(
                channel=os.getenv("CHANNEL_ID"),
                text=str(exc),
            )
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
    # here create modal window trigger handler to use local 'jobs' variable
    @slack_bot_app.action("modal_window_handler")
    def watch_job_openings(ack, body, client):
        ack()
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "modal_window_callback",
                "title": {"type": "plain_text", "text": "New job openings"},
                "blocks": build_blocks_given_job_openings(jobs),
            },
        )


@slack_bot_app.command("/subscribe")
def subscribe(ack, body):
    slack_bot_app.client.chat_postMessage(
        channel=body["channel_id"],
        text="You have successfully subscribed to receive new job openings! :tada:",
    )
    channel_id = body["channel_id"]
    notion_table_url = body["text"]  # extract notion table url provided by user
    dotenv.set_key(".env", "SLACK_CHANNEL_ID", channel_id)
    dotenv.set_key(".env", "NOTION_TABLE_URL", notion_table_url)
    threading.Thread(target=handle_subscription, args=(notion_table_url,)).start()
    ack()
