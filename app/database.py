from flask_sqlalchemy import SQLAlchemy
from .app import flask_app

DB = SQLAlchemy(flask_app)
