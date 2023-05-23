from app.database import DB
from datetime import datetime


class Job(DB.Model):
    __tablename__ = "job"

    id = DB.Column(DB.Integer, primary_key=True)
    # having generic url https://www.upwork.com/jobs/~016b4000a5635eebbe
    # we will save 016b4000a5635eebbe part as job id
    slack_channel_id = DB.Column(DB.Text)
    job_url = DB.Column(DB.Text)
    origin = DB.Column(DB.String(20))
    company = DB.Column(DB.String(20), nullable=True)
    creation_time = DB.Column(DB.Date, nullable=True, default=datetime.utcnow().date())

    __table_args__ = (DB.UniqueConstraint("slack_channel_id", "job_url", name="uix_1"),)

    def save(self):
        DB.session.add(self)
        DB.session.commit()

    def delete(self):
        DB.session.delete(self)
        DB.session.commit()


class Invitation(DB.Model):
    __tablename__ = "invitations"

    id = DB.Column(DB.Integer, primary_key=True)
    url = DB.Column(DB.String(70), unique=True)

    def save(self):
        DB.session.add(self)
        DB.session.commit()

    def delete(self):
        DB.session.delete(self)
        DB.session.commit()
