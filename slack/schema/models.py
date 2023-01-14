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

    def save(self):
        DB.session.add(self)
        DB.session.commit()

    def delete(self):
        DB.session.delete(self)
        DB.session.commit()


class Job(DB.Model):

    __tablename__ = "job"

    id = DB.Column(DB.Integer, primary_key=True)
    # having generic url https://www.upwork.com/jobs/~016b4000a5635eebbe
    # we will save 016b4000a5635eebbe part as job id
    job_id = DB.Column(DB.String(20), unique=True)
    client_id = DB.Column(DB.Integer, DB.ForeignKey("client.id"))

    def save(self):
        DB.session.add(self)
        DB.session.commit()

    def delete(self):
        DB.session.delete(self)
        DB.session.commit()
