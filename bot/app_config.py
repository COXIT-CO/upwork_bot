import ssl
from flask import Flask
from .schema.models import DB
from configparser import ConfigParser

ssl._create_default_https_context = ssl._create_unverified_context

flask_app = Flask(__name__)
flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DB.__init__(flask_app)

configuration = ConfigParser()
configuration.read("settings.ini")
