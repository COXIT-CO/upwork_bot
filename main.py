import ssl
from flask import Flask, request, Response
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter

from Models import DB, ma
from Controllers import RawDataController, AllDataController
from upwork_integration import *

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB.__init__(app)
ma.init_app(app)


client = WebClient(token=configuration.get("SLACK", "slack_bot_token"))
SLACK_WEBHOOK_URL = configuration.get("SLACK", "slack_webhook_url")
slack_event_adapter = SlackEventAdapter(
    configuration.get("SLACK", "slack_signing_secret"), "/slack/event", app)

BOT_ID = client.api_call("auth.test")["user_id"]


def create_new_user(request_data):
    new_user = RawDataController()
    return new_user.create(request_data)


def send_upwork_request(request_data):
    list_of_urls = get_job(request_data)
    return list_of_urls


def push_all_urls_to_db(request_data, url):
    new_urls = AllDataController()
    return new_urls.create(request_data, url)


def restrict_all_user_urls(request_data):
    all_urls = AllDataController()
    return all_urls.read_user_urls(request_data)


def restrict_all_users():
    return RawDataController().read()


def cascade_delete_user(request_data):
    return RawDataController().delete(request_data)


@slack_event_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if BOT_ID != user_id:
        list_of_data = text.split(",")
        list_of_data[1] = list_of_data[1][:-1].split("<https://www.upwork.com/jobs/")
        data_to_db = [list_of_data[0], list_of_data[1][1]]

        client.chat_postMessage(channel=channel_id, text=f"{create_new_user(data_to_db)}")
        result_list = send_upwork_request(list_of_data[1][1])
        push_all_urls_to_db(result_list, list_of_data[1][1])


@app.route("/all-clients", methods=["POST"])
def show_clients():
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=f"{restrict_all_users()}")

    return Response(), 200


@app.route("/client-urls", methods=["POST"])
def show_client_urls():
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")
    text = data.get("text")

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=f"{restrict_all_user_urls(f'{text}')}")

    return Response(), 200


@app.route("/delete-client", methods=["POST"])
def delete_client():
    data = request.form
    channel_id = data.get("channel_id")
    user_id = data.get("user_id")
    text = data.get("text")

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=f"{cascade_delete_user(f'{text}')}")

    return Response(), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port='8000', debug=True)
