from .models import Client, Job, SlackNotion
from ...upwork.utils import get_job_id_from_url


URL = "https://www.upwork.com/jobs/"


class ClientController:
    @classmethod
    def create(cls, name=None, url=None):
        # search for client entry by name no matter has url been provided or not
        client = Client.query.filter_by(name=name).first() if name is not None else None
        if client is not None:
            return "User with this name already exists!"
        if name is None:
            return "You haven't provided client name! It's required"
        if url is None:
            return "You haven't provided url of client account! It's required"
        new_client = Client(name=name, url=url)
        new_client.save()
        return "Successfully created!"

    @classmethod
    def get_all_clients(cls):
        clients = Client.query.all()
        result_dict = {}
        for client in clients:
            result_dict[client.name] = URL + client.url
        return result_dict

    @classmethod
    def get(cls, name=None, url=None):
        """get client either by name or url"""
        if name is None and url is None:
            return "You haven't provided neither name nor url"
        # search for client object by name or url. If both provided search by name
        client = (
            Client.query.filter_by(name=name).first()
            if name is not None
            else Client.query.filter_by(url=url).first()
        )
        return client

    @classmethod
    def delete(cls, name=None):
        client = Client.query.filter_by(name=name).first()
        if client is None:
            return "No such client!"
        else:
            jobs_by_client = Job.query.filter_by(client_id=client.id).all()
            if len(jobs_by_client) != 0:
                for job in jobs_by_client:
                    job.delete()
            client.delete()
            return "Deleted successfully!"


class JobController:
    @classmethod
    def create(cls, job_url=None, client_id=None):
        if job_url is None:
            return "You haven't provided job url! It's required"
        if client_id is None:
            return "You haven't provided client id for this job opening! It's required"
        job_id = get_job_id_from_url(job_url)
        if Job.query.filter_by(job_id=job_id).first() is None:
            new_job = Job(job_id=job_id, client_id=client_id)
            new_job.save()
            return "Successfully saved."
        else:
            return "Job opening already in database!"

    @classmethod
    def get(cls, job_id=None):
        if job_id is None:
            return "You haven't provided job id! It's required"
        job = Job.query.filter(job_id=job_id).first()
        return job

    @classmethod
    def delete(cls, job_id=None):
        if job_id is None:
            return "You haven't provided job id! It's required"
        job = Job.query.filter_by(job_id=job_id).first()
        client_id = job.client_id
        jobs_by_client = Job.query.filter_by(client_id=job.client_id).all()
        job.delete()
        if not len(jobs_by_client):
            client = Client.query.filter_by(id=client_id).first()
            client.delete()
        return "Deleted successfully!"


class SlackNotionController:
    @classmethod
    def create(cls, slack_user_id=None, notion_table_url=None):
        if slack_user_id is None:
            return "You haven't provided slack user id! It's required"
        if notion_table_url is None:
            return "You haven't provided notion table url! It's required"
        if (
            SlackNotion.query.filter_by(slack_user_id=slack_user_id).first()
            is None
        ):
            new_relation = SlackNotion(
                slack_user_id=slack_user_id, notion_table_url=notion_table_url
            )
            new_relation.save()
            return "Successfully saved."
        else:
            return "Relation already in database!"


    @classmethod
    def get(cls, slack_user_id=None):
        if slack_user_id is None:
            return "You haven't provided slack user id! It's required"
        relation = SlackNotion.query.filter(slack_user_id=slack_user_id).first()
        return relation
