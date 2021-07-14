from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class Client(DB.Model):

    __tablename__ = "client"

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), unique=True)
    url = DB.Column(DB.String(200), unique=True)
    client = DB.relationship(
        "Job", backref="owner", cascade="delete, merge, save-update"
    )
    # one to many (name -> urls)


class Job(DB.Model):

    __tablename__ = "job"

    id = DB.Column(DB.Integer, primary_key=True)
    client_id = DB.Column(DB.Integer, DB.ForeignKey("client.id"))
    clients_url = DB.Column(DB.String(200))
