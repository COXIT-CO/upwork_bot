"""all events when user wants to subscribe to receive new job openings or opens/interacts with modal windows in slack are handed here"""
import ast
import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()

from slack.app import slack_bot_app
from helpers.file import (
    write_arg_to_file,
    delete_arg_from_file,
    get_arg_value_from_file,
)
from helpers.slack import (
    build_blocks_given_job_openings,
    build_blocks_given_invitations,
)


# subscribe to receive new upwork job openings by provided url on notion table
@slack_bot_app.command("/subscribe_upwork")
def subscribe_upwork(ack, body):
    ack()
    channel_id = body["channel_id"]
    upwork_table_url = body["text"]

    slack_channels_data = get_arg_value_from_file("SLACK_CHANNELS_DATA")
    if slack_channels_data != {}:
        slack_channels_data = slack_channels_data[20:-1]
        slack_channels_data = ast.literal_eval(slack_channels_data)
    for chan in slack_channels_data:
        if isinstance(chan, tuple):
            if channel_id == chan[0]:
                channel_id = chan
                break
        elif isinstance(chan, str):
            channel_id = chan
            break
    channel_data = slack_channels_data.get(channel_id, {})
    channel_data["upwork_table_url"] = upwork_table_url
    slack_channels_data[channel_id] = channel_data

    args = {
        "SLACK_CHANNELS_DATA": str(slack_channels_data),
        "SLACK_SIGNING_SECRET": os.getenv("SLACK_SIGNING_SECRET"),
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "CLIENT_ID": os.getenv("CLIENT_ID"),
        "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
        "CLIENT_EMAIL": os.getenv("CLIENT_EMAIL"),
        "CLIENT_PASSWORD": os.getenv("CLIENT_PASSWORD"),
        "REDIRECT_URI": os.getenv("REDIRECT_URI"),
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
        "REFRESH_TOKEN": os.getenv("REFRESH_TOKEN"),
        "LOGIN_ANSWER": os.getenv("LOGIN_ANSWER"),
    }
    for arg, value in args.items():
        write_arg_to_file(arg, value, file_path=f"{ROOT_DIR}/.env")

    # docker container binded code should provide full paths to interpreter and executables
    python_path = "/usr/local/bin/python"
    subprocess.Popen(
        f"{python_path} /app/cron_jobs/upwork_jobs_scraping.py",
        shell=True,
    )
    subprocess.Popen(
        f"{python_path} /app/cron_jobs/upwork_interviews_scraping.py",
        shell=True,
    )
    subprocess.Popen(
        f"{python_path} /app/cron_jobs/refresh_upwork_token.py",
        shell=True,
    )


# subscribe to receive new linkedin job openings by provided url on notion table
@slack_bot_app.command("/subscribe_linkedin")
def subscribe_linkedin(ack, body):
    ack()
    channel_id = body["channel_id"]
    linkedin_table_url = body["text"]

    slack_channels_data = get_arg_value_from_file("SLACK_CHANNELS_DATA")
    if slack_channels_data != {}:
        slack_channels_data = slack_channels_data[20:-1]
        slack_channels_data = ast.literal_eval(slack_channels_data)
    for chan in slack_channels_data:
        if isinstance(chan, tuple):
            if channel_id == chan[0]:
                channel_id = chan
                break
        elif isinstance(chan, str):
            channel_id = chan
            break
    channel_data = slack_channels_data.get(channel_id, {})
    channel_data["linkedin_table_url"] = linkedin_table_url
    slack_channels_data[channel_id] = channel_data

    args = {
        "SLACK_CHANNELS_DATA": str(slack_channels_data),
        "SLACK_SIGNING_SECRET": os.getenv("SLACK_SIGNING_SECRET"),
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "CLIENT_ID": os.getenv("CLIENT_ID"),
        "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
        "CLIENT_EMAIL": os.getenv("CLIENT_EMAIL"),
        "CLIENT_PASSWORD": os.getenv("CLIENT_PASSWORD"),
        "REDIRECT_URI": os.getenv("REDIRECT_URI"),
        "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
        "REFRESH_TOKEN": os.getenv("REFRESH_TOKEN"),
        "LOGIN_ANSWER": os.getenv("LOGIN_ANSWER"),
    }
    for arg, value in args.items():
        write_arg_to_file(arg, value, file_path=f"{ROOT_DIR}/.env")

    # docker container binded code should provide full paths to interpreter and executables
    python_path = "/usr/local/bin/python"
    subprocess.Popen(
        f"{python_path} /app/cron_jobs/linkedin_jobs_scraping.py",
        shell=True,
    )


# handler to open modal window on new upwork jobs
@slack_bot_app.action("upwork_handler")
def handle_upwork_job_openings(ack, body, payload, client):
    ack()
    channel_id = body["container"]["channel_id"]
    if "value" in payload:
        channel_jobs = ast.literal_eval(payload["value"])
    else:
        slack_channels_data = get_arg_value_from_file("SLACK_CHANNELS_DATA")
        slack_channels_data = slack_channels_data[20:-1]
        slack_channels_data = ast.literal_eval(slack_channels_data)

        for chan in slack_channels_data:
            if isinstance(chan, tuple):
                chan_id = chan[0]
                if channel_id == chan_id:
                    channel_id = chan
                    break
            elif isinstance(chan, str):
                channel_id = chan
                break

        channel_data = slack_channels_data[channel_id]
        channel_jobs = ast.literal_eval(channel_data["upwork_jobs"])

    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "upwork_window_callback",
            "title": {"type": "plain_text", "text": "Upwork job openings"},
            "blocks": build_blocks_given_job_openings(channel_jobs, origin="upwork"),
        },
    )


# handler to open modal window on new linkedin jobs
@slack_bot_app.action("linkedin_handler")
def handle_linkedin_job_openings(ack, body, payload, client):
    ack()
    channel_id = body["container"]["channel_id"]
    if "value" in payload:
        channel_jobs = ast.literal_eval(payload["value"])
    else:
        slack_channels_data = get_arg_value_from_file("SLACK_CHANNELS_DATA")
        slack_channels_data = slack_channels_data[20:-1]
        slack_channels_data = ast.literal_eval(slack_channels_data)

        for chan in slack_channels_data:
            if isinstance(chan, tuple):
                if channel_id == chan[0]:
                    channel_id = chan
                    break
            elif isinstance(chan, str):
                channel_id = chan
                break

        channel_data = slack_channels_data[channel_id]
        channel_jobs = channel_data["linkedin_jobs"]

    try:
        page = int(channel_data["current_linkedin_jobs_page"])
    except UnboundLocalError:
        page = None

    blocks = build_blocks_given_job_openings(channel_jobs, origin="linkedin", page=page)
    elements = []
    if page is not None:
        if len(channel_jobs) > 1 and page < len(channel_jobs) - 1:
            elements.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "next"},
                    "style": "primary",
                    "action_id": "next_page",
                    "value": "my_data",
                }
            )
        if page > 0:
            elements.insert(
                0,
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "previous"},
                    "style": "danger",
                    "action_id": "previous_page",
                    "value": "my_data",
                },
            )
        blocks.append({"type": "actions", "elements": elements})
    response = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "linkedin_window_callback",
            "title": {"type": "plain_text", "text": "LinkedIn job openings"},
            "blocks": blocks,
        },
    )
    try:
        if isinstance(channel_id, str):
            del slack_channels_data[channel_id]
            channel_id = (channel_id, response["view"]["id"])
        elif isinstance(channel_id, tuple):
            view_id = response["view"]["id"]
            if view_id != channel_id[1]:
                del slack_channels_data[channel_id]
            channel_id = (channel_id[0], view_id)
        slack_channels_data[channel_id] = channel_data
        delete_arg_from_file("SLACK_CHANNELS_DATA", file_path=f"{ROOT_DIR}/.env")
        write_arg_to_file(
            "SLACK_CHANNELS_DATA", slack_channels_data, file_path=f"{ROOT_DIR}/.env"
        )
    except UnboundLocalError:
        pass


@slack_bot_app.action("previous_page")
def handle_previous_page(ack, body, client):
    ack()
    view_id = body["container"]["view_id"]

    slack_channels_data = get_arg_value_from_file("SLACK_CHANNELS_DATA")
    slack_channels_data = slack_channels_data[20:-1]
    slack_channels_data = ast.literal_eval(slack_channels_data)
    for chan in slack_channels_data:
        if isinstance(chan, tuple):
            chan_view_id = chan[1]
            if view_id == chan_view_id:
                break
    channel_data = slack_channels_data[chan]
    page = int(channel_data["current_linkedin_jobs_page"])
    page = 0 if page - 1 < 0 else page - 1

    channel_data["current_linkedin_jobs_page"] = page
    slack_channels_data[chan] = channel_data

    delete_arg_from_file("SLACK_CHANNELS_DATA", file_path=f"{ROOT_DIR}/.env")
    write_arg_to_file(
        "SLACK_CHANNELS_DATA", slack_channels_data, file_path=f"{ROOT_DIR}/.env"
    )

    jobs_to_display = [channel_data["linkedin_jobs"][page]]

    blocks = build_blocks_given_job_openings(jobs_to_display, origin="linkedin")
    elements = [
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "next"},
            "style": "primary",
            "action_id": "next_page",
            "value": "my_data",
        }
    ]
    if page > 0:
        elements.insert(
            0,
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "previous"},
                "style": "danger",
                "action_id": "previous_page",
                "value": "my_data",
            },
        )
    blocks.append({"type": "actions", "elements": elements})
    view_id = body["container"]["view_id"]
    client.views_update(
        view_id=view_id,
        view={
            "type": "modal",
            "callback_id": "linkedin_window_callback",
            "title": {"type": "plain_text", "text": "LinkedIn job openings"},
            "blocks": blocks,
        },
    )


@slack_bot_app.action("next_page")
def handle_next_page(ack, body, client):
    ack()
    view_id = body["container"]["view_id"]

    slack_channels_data = get_arg_value_from_file("SLACK_CHANNELS_DATA")
    slack_channels_data = slack_channels_data[20:-1]
    slack_channels_data = ast.literal_eval(slack_channels_data)
    for chan in slack_channels_data:
        if isinstance(chan, tuple):
            chan_view_id = chan[1]
            if view_id == chan_view_id:
                break
    channel_data = slack_channels_data[chan]
    page = int(channel_data["current_linkedin_jobs_page"])

    page = (
        page + 1
        if page < len(channel_data["linkedin_jobs"]) - 1
        else len(channel_data["linkedin_jobs"]) - 1
    )
    channel_data["current_linkedin_jobs_page"] = page
    slack_channels_data[chan] = channel_data
    delete_arg_from_file("SLACK_CHANNELS_DATA", file_path=f"{ROOT_DIR}/.env")
    write_arg_to_file(
        "SLACK_CHANNELS_DATA", slack_channels_data, file_path=f"{ROOT_DIR}/.env"
    )
    jobs_to_display = [channel_data["linkedin_jobs"][page]]

    blocks = build_blocks_given_job_openings(jobs_to_display, origin="linkedin")
    elements = [
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "previous"},
            "style": "danger",
            "action_id": "previous_page",
            "value": "my_data",
        }
    ]
    if page < len(channel_data["linkedin_jobs"]) - 1:
        elements.append(
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "next"},
                "style": "primary",
                "action_id": "next_page",
                "value": "my_data",
            }
        )
    blocks.append({"type": "actions", "elements": elements})
    view_id = body["container"]["view_id"]
    client.views_update(
        view_id=view_id,
        view={
            "type": "modal",
            "callback_id": "linkedin_window_callback",
            "title": {"type": "plain_text", "text": "LinkedIn job openings"},
            "blocks": blocks,
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
