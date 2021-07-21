import ssl
from flask import Flask
from .schema.models import DB

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
DB.__init__(app)
