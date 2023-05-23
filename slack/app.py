import os
from slack_bolt import App

slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)
