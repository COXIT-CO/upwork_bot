import os
import ssl
from flask import Flask

ssl._create_default_https_context = ssl._create_unverified_context

flask_app = Flask(__name__)
if os.getenv("TESTING"):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
else:
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
