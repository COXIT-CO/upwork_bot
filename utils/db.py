from app.app import flask_app
from datetime import datetime
from upwork_part.schema.controllers import JobController
from upwork_part.schema.controllers import InvitationController
from upwork_part.schema.models import Job as JobModel
from upwork_part.schema.models import Invitation

job_controller = JobController()
invitation_controller = InvitationController()


def find_new_job_openings(slack_channel_id, opened_jobs, origin):
    new_job_openings = []
    for job in opened_jobs:
        job_url = job["job_url"]
        with flask_app.app_context():
            job_object = job_controller.get(job_url)
        if not job_object:
            # job is new, so save it to db
            with flask_app.app_context():
                job_controller.create(slack_channel_id, job_url, origin=origin)
            new_job_openings.append(job)
    return new_job_openings


def remove_unactive_jobs_from_db(companies_data, origin):
    with flask_app.app_context():
        db_jobs = JobModel.query.filter_by(origin=origin).all()

    for job in db_jobs:
        url = job.job_url
        origin = job.origin
        is_job_available = False
        for job_url in companies_data:
            if url == job_url:
                is_job_available = True

        if origin == "linkedin":
            if (
                not is_job_available
                and (datetime.utcnow().date() - job.creation_time).days >= 3
            ):
                with flask_app.app_context():
                    job_controller.delete(url)
        else:
            if not is_job_available:
                with flask_app.app_context():
                    job_controller.delete(url)


def remove_job_from_db(job_url: str):
    with flask_app.app_context():
        return job_controller.delete(job_url)


def find_new_invitations(slack_channel_id, invitations):
    new_invitations = []
    for inv in invitations:
        invitation_link = inv["link"]
        with flask_app.app_context():
            invitation = invitation_controller.get(invitation_link)
        if not invitation:
            # invitation is new, so save it to db
            with flask_app.app_context():
                invitation_controller.create(slack_channel_id, invitation_link)
            new_invitations.append(inv)
    return new_invitations


def remove_unactive_invitations_from_db(invitations):
    with flask_app.app_context():
        invitations_from_bd = Invitation.query.all()

    for inv_db in invitations_from_bd:
        inv_db_link = inv_db.url
        for inv in invitations:
            inv_link = inv["link"]
            if inv_db_link == inv_link:
                break
        else:
            with flask_app.app_context():
                invitation_controller.delete(inv_db_link)
