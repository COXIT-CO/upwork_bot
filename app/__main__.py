if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv(".env")
    # import flask app and initialize routes to accept requests
    from .routes import flask_app
    from upwork_part.schema.models import Job
    from .database import DB
    with flask_app.app_context():
        DB.create_all()

    flask_app.run()
