from ..app.config_parser import configuration
from slack_bolt import App

slack_bot_app = App(
    signing_secret=configuration.get("FLASK", "slack_signing_secret"),
    token=configuration.get("FLASK", "slack_bot_token"),
)
