import ast
import os
import subprocess
from slack.app import slack_bot_app
from slack.utils import build_blocks_given_job_openings, build_blocks_given_invitations


@slack_bot_app.command("/subscribe")
def subscribe(ack, body):
    channel_id = body["channel_id"]
    notion_table_url = body["text"]
    current_directory_path = os.path.dirname(os.path.abspath(__file__))
    level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
    channels = [channel_id]
    try:
        with open(f"{level_up_directory_path}/.env", "r") as file:
            lines = file.readlines()
            for line in lines:
                if "SLACK_CHANNEL_ID" in line:
                    active_channels = ast.literal_eval(line.split("=")[-1][:-1])
                    if channels[0] not in active_channels:
                        channels += active_channels
    except FileNotFoundError:
        # do nothing if we subscribe for the first time
        pass

    with open(f"{level_up_directory_path}/.env", "w") as file:
        file.write(f"NOTION_TABLE_URL={notion_table_url}\n")
        file.write(f"SLACK_CHANNEL_ID={str(channels)}\n")
        file.write(f"SLACK_SIGNING_SECRET={os.getenv('SLACK_SIGNING_SECRET')}\n")
        file.write(f"SLACK_BOT_TOKEN={os.getenv('SLACK_BOT_TOKEN')}\n")
        file.write(f"CLIENT_ID={os.getenv('CLIENT_ID')}\n")
        file.write(f"CLIENT_SECRET={os.getenv('CLIENT_SECRET')}\n")
        file.write(f"CLIENT_EMAIL={os.getenv('CLIENT_EMAIL')}\n")
        file.write(f"CLIENT_PASSWORD={os.getenv('CLIENT_PASSWORD')}\n")
        file.write(f"REDIRECT_URI={os.getenv('REDIRECT_URI')}\n")
        file.write(f"NOTION_TOKEN={os.getenv('NOTION_TOKEN')}\n")
        file.write(f"REFRESH_TOKEN={os.getenv('REFRESH_TOKEN')}\n")
        file.write(f"LOGIN_ANSWER={os.getenv('LOGIN_ANSWER')}\n")

    # docker container binded code should provide full paths to interpreter and executables
    python_path = "/usr/local/bin/python"
    subprocess.Popen(
        f"{python_path} /app/cron-jobs/cron_job_openings.py",
        shell=True,
    )
    subprocess.Popen(
        f"{python_path} /app/cron-jobs/cron_interview_updates.py",
        shell=True,
    )
    subprocess.Popen(
        f"{python_path} /app/cron-jobs/cron_refresh_token.py",
        shell=True,
    )
    ack()


@slack_bot_app.action("modal_window_handler")
def handle_job_openings(ack, body, payload, client):
    ack()
    if "value" in payload:
        jobs_to_list = ast.literal_eval(payload["value"])
    else:
        current_directory_path = os.path.dirname(os.path.abspath(__file__))
        level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
        with open(level_up_directory_path + "/.env", "r") as file:
            lines = file.readlines()
        jobs = "".join(lines)[5:-1]
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
