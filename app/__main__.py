if __name__ == "__main__":
    from .routes import flask_app
    from upwork_part.schema.models import Job
    from .database import DB

    with flask_app.app_context():
        DB.create_all()

    flask_app.run("0.0.0.0", port=8000)
