if __name__ == "__main__":
    
    import dotenv
    from . import args_parser

    dotenv.load_dotenv(".env")
    dotenv.set_key(".env", "CLIENT_ID", args_parser.args.client_id)
    dotenv.set_key(".env", "CLIENT_SECRET", args_parser.args.client_secret)
    dotenv.set_key(".env", "REFRESH_TOKEN", args_parser.args.refresh_token)
    dotenv.set_key(".env", "SLACK_BOT_TOKEN", args_parser.args.slack_bot_token)
    dotenv.set_key(".env", "SLACK_SIGNING_SECRET", args_parser.args.slack_signing_secret)
    dotenv.set_key(".env", "NOTION_TOKEN", args_parser.args.notion_token)
    
    # import flask app and initialize routes to accept requests
    from .routes import flask_app
    from upwork_part.schema.models import Job
    from .database import DB

    with flask_app.app_context():
        DB.create_all()

    flask_app.run()
