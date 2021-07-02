from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


DB = SQLAlchemy()
ma = Marshmallow()


class RawData(DB.Model):

    __tablename__ = "raw_data"

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), unique=True)
    url = DB.Column(DB.String(200), unique=True)
    # one to many (name -> urls)

    def __init__(self, name=None, url=None):
        self.name = name
        self.url = url


class AllData(DB.Model):

    __tablename__ = "all_data"

    id = DB.Column(DB.Integer, primary_key=True)
    client_id = DB.Column(DB.Integer, DB.ForeignKey("raw_data.id"))
    client = DB.relationship(
        "RawData", backref="owner", cascade="delete, merge, save-update"
    )
    clients_url = DB.Column(DB.String(200), unique=True)

    def __init__(self, client=None, clients_url=None):
        self.client = client
        self.clients_url = clients_url
