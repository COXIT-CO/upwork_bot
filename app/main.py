from config_parser import configuration
from database import DB

from slack_bolt import App

slack_bot_app = App(
    signing_secret=configuration.get("FLASK", "slack_signing_secret"),
    token=configuration.get("FLASK", "slack_bot_token"),
)

# There is nothing specific to Flask here!
# App is completely framework/runtime agnostic
@slack_bot_app.command("/hello-bolt")
def hello(body, ack):
    ack(f"Hi <@{body['user_id']}>!")


# Initialize Flask app
from flask import Flask, request

flask_app = Flask(__name__)

# SlackRequestHandler translates WSGI requests to Bolt's interface
# and builds WSGI response from Bolt's response.
from slack_bolt.adapter.flask import SlackRequestHandler

handler = SlackRequestHandler(slack_bot_app)


# just a function to co
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler runs App's dispatch method
    return handler.handle(request)


flask_app.run()


if __name__ == "__main__":
    with flask_app.app_context():
        DB.create_all()
