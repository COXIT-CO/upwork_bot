from .models import Job

URL = "https://www.upwork.com/jobs/"


class JobController:
    @classmethod
    def create(cls, job_url=None):
        if job_url is None:
            return "You haven't provided job url! It's required"
        job_key = job_url.split("~")[-1]
        if Job.query.filter_by(job_key=job_key).first() is None:
            new_job = Job(job_key=job_key)
            new_job.save()
            return "Successfully saved."
        else:
            return "Job opening already in database!"

    @classmethod
    def get(cls, job_url=None):
        if job_url is None:
            return "You haven't provided job key! It's required"
        job_key = job_url.split("~")[-1]
        job = Job.query.filter_by(job_key=job_key).first()
        return job if job else ""

    @classmethod
    def delete(cls, job_key=None):
        if job_key is None:
            return "You haven't provided job key! It's required"
        job = Job.query.filter_by(job_key=job_key).first()
        if job is None:
            return "No such job opening!"
        job.delete()
        return "Deleted successfully!"
