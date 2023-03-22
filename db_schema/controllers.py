from .models import Job, Invitation

URL = "https://www.upwork.com/jobs/"


class JobController:
    @classmethod
    def create(cls, slack_channel_id, job_url, origin, company=None):
        if Job.query.filter_by(job_url=job_url).first() is None:
            new_job = Job(
                slack_channel_id=slack_channel_id,
                job_url=job_url,
                origin=origin,
                company=company,
            )
            new_job.save()
            return "Successfully saved!"
        else:
            return "Job opening already in database!"

    @classmethod
    def get(cls, job_url):
        job = Job.query.filter_by(job_url=job_url).first()
        return job if job else ""

    @classmethod
    def delete(cls, job_url):
        job = Job.query.filter_by(job_url=job_url).first()
        if job is None:
            return "No such job opening!"
        job.delete()
        return "Deleted successfully!"


class InvitationController:
    @classmethod
    def create(cls, slack_channel_id, invitation_url):
        if Invitation.query.filter_by(url=invitation_url).first() is None:
            new_invitation = Invitation(
                slack_channel_id=slack_channel_id, url=invitation_url
            )
            new_invitation.save()
            return "Successfully saved."
        else:
            return "Invitation already in database!"

    @classmethod
    def get(cls, invitation_url):
        invitation = Invitation.query.filter_by(url=invitation_url).first()
        return invitation if invitation else ""

    @classmethod
    def delete(cls, invitation_url):
        invitation = Invitation.query.filter_by(url=invitation_url).first()
        if invitation is None:
            return "No such invitation!"
        invitation.delete()
        return "Deleted successfully!"
