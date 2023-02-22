import os
import sys

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

sys.path.insert(0, level_up_directory_path)

from app.app import flask_app
from upwork_part.schema.controllers import JobController
from upwork_part.schema.models import Job as JobModel

job_controller = JobController()

def find_new_job_openings(opened_jobs, origin):
    new_job_openings = []
    for job in opened_jobs:
        job_url = job["job_url"]
        with flask_app.app_context():
            job_object = job_controller.get(job_url)
        if not job_object:
            # job is new, so save it to db
            with flask_app.app_context():
                job_controller.create(job_url, origin=origin)
            new_job_openings.append(job)
    return new_job_openings


def remove_unactive_jobs_from_db(active_jobs, origin):
    with flask_app.app_context():
        db_jobs = JobModel.query.filter_by(origin=origin).all()

    for job in db_jobs:
        url = job.job_url
        origin = job.origin
        is_job_available = False
        for job_url in active_jobs:
            if url == job_url:
                is_job_available = True

        if not is_job_available:
            with flask_app.app_context():
                job_controller.delete(url)


def remove_job_from_db(job_url: str):
    with flask_app.app_context():
        return job_controller.delete(job_url)