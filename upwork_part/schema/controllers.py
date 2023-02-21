from .models import Job, Invitation

URL = "https://www.upwork.com/jobs/"


class JobController:
    @classmethod
    def create(cls, job_url=None, origin=None):
        if job_url is None:
            return "You haven't provided job url! It's required"
        if origin is None:
            return "You haven't provided origin for job! It's required"
        if Job.query.filter_by(job_url=job_url).first() is None:
            new_job = Job(job_url=job_url, origin=origin)
            new_job.save()
            return "Successfully saved."
        else:
            return "Job opening already in database!"

    @classmethod
    def get(cls, job_url=None):
        if job_url is None:
            return "You haven't provided job key! It's required"
        job = Job.query.filter_by(job_url=job_url).first()
        return job if job else ""

    @classmethod
    def delete(cls, job_url=None):
        if job_url is None:
            return "You haven't provided job key! It's required"
        job = Job.query.filter_by(job_url=job_url).first()
        if job is None:
            return "No such job opening!"
        job.delete()
        return "Deleted successfully!"


class InvitationController:
    @classmethod
    def create(cls, invitation_url=None):
        if invitation_url is None:
            return "You haven't provided invitation url! It's required"
        if Invitation.query.filter_by(url=invitation_url).first() is None:
            new_invitation = Invitation(url=invitation_url)
            new_invitation.save()
            return "Successfully saved."
        else:
            return "Invitation already in database!"

    @classmethod
    def get(cls, invitation_url=None):
        if invitation_url is None:
            return "You haven't provided invitation key! It's required"
        invitation = Invitation.query.filter_by(url=invitation_url).first()
        return invitation if invitation else ""

    @classmethod
    def delete(cls, invitation_url=None):
        if invitation_url is None:
            return "You haven't provided invitation url! It's required"
        invitation = Invitation.query.filter_by(url=invitation_url).first()
        if invitation is None:
            return "No such invitation!"
        invitation.delete()
        return "Deleted successfully!"
