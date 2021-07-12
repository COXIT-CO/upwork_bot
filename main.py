import ssl
import threading
import time

from flask import Flask, request, Response
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

from models import DB
from controllers import ClientController, JobController, URL
from upwork_integration import configuration, get_desktop_client, get_job

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB.__init__(app)

client = WebClient(token=configuration.get("SLACK", "slack_bot_token"))
SLACK_WEBHOOK_URL = configuration.get("SLACK", "slack_webhook_url")
slack_event_adapter = SlackEventAdapter(
    configuration.get("SLACK", "slack_signing_secret"), "/slack/event", app
)

BOT_ID = client.api_call("auth.test")["user_id"]


def create_new_user(request_data):
    """Create new user in Client table
    param: request_data(name, url)
    """
    new_user = ClientController()
    return new_user.create(request_data)


def send_upwork_request(request_data):
    """Call get_job function that makes request to Upwork API
    and returns list of open jobs
    param: request_data(id of job)
    return: list of urls
    """
    list_of_urls = get_job(request_data)
    if list_of_urls is None:
        list_of_urls = []
    return list_of_urls


def push_all_urls_to_db(request_data, url):
    """Push all data from upwork request to Jobs table
    param: request_data(list of urls) and url(id of job)
    """
    new_urls = JobController()
    return new_urls.create(request_data, url)


def restrict_all_user_urls(request_data):
    """Show all urls from both table by certain user
    param: user name
    return: set of all user urls
    """
    all_urls = JobController()
    return all_urls.read_user_urls(request_data)


def restrict_all_users():
    """Show all users from Clients table
    return: dict with format { name: url }
    """
    return ClientController().read()


def restrict_jobs_urls():
    """Show all urls from Jobs table
    return: set of job ids
    """
    return JobController().read_jobs_data()


def cascade_delete_user(request_data):
    """Delete user from database
    param: name
    """
    return ClientController().delete(request_data)


@slack_event_adapter.on("message")
def message(payload):
    """Event, reacting on message in chat"""
    event = payload.get("event", {})
    message.channel_id = event.get("channel")
    message.user_id = event.get("user")
    text = event.get("text")
    try:
        if BOT_ID != user_id:
            list_of_data = text.split(",")
            list_of_data[1] = list_of_data[1][:-1].split("<https://www.upwork.com/jobs/")
            data_to_db = [list_of_data[0], list_of_data[1][1]]
            client.chat_postMessage(
                channel=channel_id, text=f"{create_new_user(data_to_db)}"
            )
            result_list = send_upwork_request(list_of_data[1][1])
            push_all_urls_to_db(result_list, list_of_data[1][1])
    except IndexError or AttributeError:
        pass


@app.route("/all-clients", methods=["POST"])
def show_clients():
    """Slash-command, which show all clients"""
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")

    if BOT_ID != user_id:
        client.chat_postMessage(
            channel=channel_id, text=f"{restrict_all_users()}"
        )

    return Response(), 200


@app.route("/client-urls", methods=["POST"])
def show_client_urls():
    """Slash-command, which show all urls by client"""
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")
    text = data.get("text")

    if BOT_ID != user_id:
        client.chat_postMessage(
            channel=channel_id, text=f"{restrict_all_user_urls(f'{text}')}"
        )

    return Response(), 200


@app.route("/delete-client", methods=["POST"])
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

    return Response(), 200


def notiffication(func, sec=0, minutes=0, hours=0):
    while True:
        sleep_time = sec + (minutes * 60) + (hours * 3600)
        time.sleep(sleep_time)
        func()


def create_tread(func):
    enable_notification_thread = threading.Thread(
        target=notiffication, kwargs=({"func": func, "minutes": 10}))
    enable_notification_thread.daemon = True
    enable_notification_thread.start()


def check_data(data):
    """Check data from upwork request and database
    param: job id
    return: set of new jobs
    """
    urls_from_upwork = set(send_upwork_request(data))
    urls_from_db = restrict_jobs_urls()
    return urls_from_upwork.difference(urls_from_db)


def send_upw_time_request():
    """Send request to Upwork and post new urls in chat"""
    raw_dict = restrict_all_users()
    for key in raw_dict.keys():
        link = raw_dict[key]
        url = link.split("~")
        raw_job_id = "~" + url[1]
        print(link, key)
        if len(check_data(raw_job_id)) != 0:
            for new_url in check_data(raw_job_id):
                client.chat_postMessage(
                    channel='#upwork_bot', text=f"{key}, { URL+ new_url}"
                )
            push_all_urls_to_db(check_data(raw_job_id), raw_job_id)
        time.sleep(100)

if __name__ == "__main__":

    send_upw_time_request()
    create_tread(send_upw_time_request)
    app.run(host="127.0.0.1", port="8000")
