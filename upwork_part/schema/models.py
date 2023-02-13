from app.database import DB


class Job(DB.Model):

    __tablename__ = "job"

    id = DB.Column(DB.Integer, primary_key=True)
    # having generic url https://www.upwork.com/jobs/~016b4000a5635eebbe
    # we will save 016b4000a5635eebbe part as job id
    job_key = DB.Column(DB.String(20), unique=True)

    def save(self):
        DB.session.add(self)
        DB.session.commit()

    def delete(self):
        DB.session.delete(self)
        DB.session.commit()
