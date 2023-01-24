from .app import flask_app
from flask import request
from slack_bolt.adapter.flask import SlackRequestHandler

from slack.event_handler import slack_bot_app

# SlackRequestHandler translates WSGI requests to Bolt's interface
# and builds WSGI response from Bolt's response.
handler = SlackRequestHandler(slack_bot_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/slack/subscribe", methods=["POST"])
def slack_subscribe():
    return handler.handle(request)


@flask_app.route("/slack/interactive", methods=["POST"])
def abc():
    return handler.handle(request)


@flask_app.route("/slack/unsubscribe", methods=["POST"])
def slack_unsubscribe():
    return handler.handle(request)
