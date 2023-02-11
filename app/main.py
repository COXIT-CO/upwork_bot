import json
import threading
import time
import logging

from flask import request, Response
from ..slack.schema.controllers import ClientController, JobController, URL

# from config_parser import configuration
from ..upwork.upwork_integration import get_job
from logging.config import dictConfig
from log import LOG_CONFIG
from ..slack.app import slack_bot_app
from .app import flask_app

# SlackRequestHandler translates WSGI requests to Bolt's interface
# and builds WSGI response from Bolt's response.
from slack_bolt.adapter.flask import SlackRequestHandler

handler = SlackRequestHandler(slack_bot_app)

LOGGER = logging.getLogger()
LOG_CONFIG["root"]["handlers"].append("file")
flask_log = logging.getLogger("flask")
flask_log.setLevel(logging.ERROR)
dictConfig(LOG_CONFIG)

HOST = configuration.get("FLASK", "host")
PORT = configuration.getint("FLASK", "port")
SUCCESS_CODE = 200
CHANNEL_NAME = "#upwork_bot"


def create_new_user(request_data):
    """Create new user in Client table
    param: request_data(name, url)
    """
    return ClientController.create(request_data)


def send_upwork_request(request_data):
    """Call get_job function that makes request to Upwork API
    and returns list of open jobs
    param: request_data(id of job)
    return: list of urls
    """
    try:
        list_of_urls = get_job(request_data)
        if list_of_urls is None:
            list_of_urls = []
        return list_of_urls
    except json.decoder.JSONDecodeError as e:
        LOGGER.error("Error with url in DB! <%s> job id<%s>", e, request_data)


def push_all_urls_to_db(request_data, url):
    """Push all data from upwork request to Jobs table
    param: request_data(list of urls) and url(id of job)
    """
    return JobController.create(request_data, url)


def restrict_all_user_urls(request_data):
    """Show all urls from both table by certain user
    param: user name
    return: set of all user urls from Client and Job tables
    """
    return JobController.read_user_urls(request_data)


def restrict_all_users():
    """Show all users from Clients table
    return: dict with format { name: url }
    """
    return ClientController.read()


def restrict_jobs_by_client(request_data):
    """Show all urls from both table by certain user
    param: user name
    return: set of all user urls from Job table
    """
    return JobController.read_urls_by_user(request_data)


def cascade_delete_user(request_data):
    """Delete user from database
    param: name
    """
    return ClientController.delete(request_data)


def delete_unactual(request_data):
    """Delete not actual urls from database
    param: set of urls
    """
    return JobController.delete_not_actual(request_data)


def add_new_actual_urls(client_name, request_data):
    """Add new actual urls from upwork request
    param: client name, new url
    """
    return JobController.add_new_actual(client_name, request_data)


@slack_bot_app.on("message")
def message(payload):
    """Event, reacting on message in chat"""
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")
    try:
        if BOT_ID != user_id:
            try:
                list_of_data = text.split(",")
                list_of_data[1] = list_of_data[1][:-1].split(
                    "<https://www.upwork.com/jobs/"
                )
                if "/" in list_of_data[1][1]:
                    data_to_db = [list_of_data[0], list_of_data[1][1][:-1]]
                else:
                    data_to_db = [list_of_data[0], list_of_data[1][1]]
                client.chat_postMessage(
                    channel=channel_id, text=f"{create_new_user(data_to_db)}"
                )
                result_list = send_upwork_request(list_of_data[1][1])
                push_all_urls_to_db(result_list, list_of_data[1][1])
            except (AttributeError, IndexError, KeyError) as e:
                LOGGER.error("%s", e)
    except (IndexError, AttributeError) as e:
        LOGGER.error("Slack default error of 2 messages %s", e)


@flask_app.route("/all-clients", methods=["POST"])
def show_clients():
    """Slash-command, which show all clients"""
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")

    if BOT_ID != user_id:
        res_data = restrict_all_users()
        for user in res_data:
            client.chat_postMessage(
                channel=channel_id,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "<%s | %s>" % (res_data[user], user),
                        },
                    }
                ],
            )
    return Response(), SUCCESS_CODE


@flask_app.route("/client-urls", methods=["POST"])
def show_client_urls():
    """Slash-command, which show all urls by client"""
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")
    text = data.get("text")

    if BOT_ID != user_id:
        all_by_user = restrict_all_user_urls(f"{text}")
        client.chat_postMessage(
            channel=channel_id, text=f"{text}: %s" % [url for url in all_by_user]
        )

    return Response(), SUCCESS_CODE


@flask_app.route("/delete-client", methods=["POST"])
def delete_client():
    """Slash-command, which delete client by name"""
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")
    text = data.get("text")

    if BOT_ID != user_id:
        client.chat_postMessage(
            channel=channel_id, text=f"{cascade_delete_user(f'{text}')}"
        )

    return Response(), SUCCESS_CODE


def notiffication(func, sec=0, minutes=0, hours=0):
    while True:
        sleep_time = sec + (minutes * 60) + (hours * 3600)
        time.sleep(sleep_time)
        func()


def create_tread(func):
    enable_notification_thread = threading.Thread(
        target=notiffication, kwargs=({"func": func, "minutes": 330})
    )
    enable_notification_thread.daemon = True
    enable_notification_thread.start()


def check_data(data, client_name):
    """Check data from upwork request and database
    param: job id
    return: set of new jobs
    """
    try:
        actual_urls_from_upwork = set(send_upwork_request(data))
        urls_from_db_by_client = restrict_jobs_by_client(client_name)
        # not_actual - exist in db but don't actual yet
        not_actual = urls_from_db_by_client - actual_urls_from_upwork
        delete_unactual(not_actual)
        # new_actual - new urls from upwork, which don't in db
        new_actual = actual_urls_from_upwork.difference(urls_from_db_by_client)
        return new_actual
    except (TypeError, EOFError) as e:
        LOGGER.error("Error with sending request (url in db): %s", e)
        return set()


def send_upw_time_request():
    """Send request to Upwork and post new urls in chat"""
    raw_dict = restrict_all_users()
    for key in raw_dict.keys():
        link = raw_dict[key]
        url = link.split("~")
        raw_job_id = "~" + url[1]
        try:
            new_uncommited_urls = check_data(raw_job_id, key)
        except KeyError as e:
            LOGGER.error("Smth wrong with link in DB %s", e)
        else:
            if len(new_uncommited_urls) > 0:
                for new_url in new_uncommited_urls:
                    if add_new_actual_urls(key, new_url) == SUCCESS_CODE:
                        client.chat_postMessage(
                            channel=CHANNEL_NAME,
                            text=f"Got a new projects for you!: {key} -> {URL + new_url}",
                        )
            time.sleep(100)


if __name__ == "__main__":
    send_upw_time_request()
    create_tread(send_upw_time_request)
    flask_app.run(host=HOST, port=PORT)
