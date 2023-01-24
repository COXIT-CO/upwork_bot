import dotenv

dotenv.load_dotenv(".env")
# import flask app and initialize routes to accept requests
from .routes import flask_app

flask_app.run()
