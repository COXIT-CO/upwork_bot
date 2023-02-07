import os
from slack_bolt import App

print(os.getenv("SLACK_SIGNING_SECRET"))
print(os.getenv("SLACK_BOT_TOKEN"))

slack_bot_app = App(
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"), token=os.getenv("SLACK_BOT_TOKEN")
)
