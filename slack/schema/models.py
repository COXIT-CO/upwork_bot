from app.database import DB


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


class SlackUserNotionTable(DB.Model):
    """model describing relation between notion table url and slack user"""

    __tablename__ = "slack_user_notion_table"

    id = DB.Column(DB.Integer, primary_key=True)
    slack_user_id = DB.Column(DB.Integer, unique=True)
    notion_table_url = DB.Column(DB.String(100))

    def save(self):
        DB.session.add(self)
        DB.session.commit()

    def update(self, notion_table_url):
        self.notion_table_url = notion_table_url
        DB.session.commit()
