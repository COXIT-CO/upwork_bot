import logging
import upwork
import requests
from upwork.routers.jobs import profile

LOGGER = logging.getLogger()


class UpworkClient:
    """class holding all-upwork-binded information including upwork client to successfully access Upwork API"""

    def __init__(self, client_id, client_secret, redirect_url, access_token_data):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token_data = access_token_data
        self.client = self.get_upwork_client(client_id, client_secret, redirect_url)

    def get_upwork_client(self, client_id, client_secret, access_token_data):
        """creation of "upwork client" to access Upwork API"""
        config = upwork.Config(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "token": access_token_data,
            }
        )
        client = upwork.Client(config)
        return client

    def refresh_access_token_data(
        self, refresh_token, client_id, client_secret, redirect_url
    ):
        """
        once upwork access token expires (it's valid for 24 hours) we need to refresh it using refresh token that is valid for 2 weeks

        function returns new dictionary with new tokens (access and refresh ones) data as shown
        e.g. of returned dictionary:
        {
            'access_token': 'oauth2v2_419655edb57520a232655fa25a1070be',
            'expires_at': 1673988561.2039783,
            'expires_in': 86400,
            'refresh_token': 'oauth2v2_4edb7804d59f5f5229d6d6b8017b2016',
            'token_type': 'Bearer'
        }
        """
        url = "https://www.upwork.com/api/v3/oauth2/token"
        parameters = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_url": redirect_url,
            "refresh_token": refresh_token,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        refreshed_access_data = requests.post(
            url=url, params=parameters, headers=headers
        )
        return refreshed_access_data.json()


class Job:
    def __init__(self, job_url):
        self.__job_url = job_url

    def get_properties(
        self, get_job_url: bool, get_job_title: bool, get_other_opened_job: bool
    ):
        """composed getter with ability to separately get object properties"""
        properties_to_return = []
        if get_job_url:
            properties_to_return.append(self.__job_url)
        if get_job_title:
            properties_to_return.append(self.__job_title)
        if get_other_opened_job:
            properties_to_return.append(self.__other_opened_jobs)

        return properties_to_return

    def get_job(self, job_url, upwork_client):
        """
        main method to get full neccessary info about job
        given job url extract info about job itself: title and other job openings
        """
        job_key = self.get_job_id_from_url(job_url)
        job_data = profile.Api(upwork_client).get_specific(job_key)

        job = Job(job_url)
        # do not save returned values as they will be saved implicitly as object properties,
        # so this can be treated as initialization
        job.extract_job_title(job_data)
        # here we pass upwork client because for each job opening we need to make request to get job title
        job.extract_other_opened_jobs(job_data, upwork_client)

        return job

    @staticmethod
    def get_job_id_from_url(url):
        """having generic url https://www.upwork.com/jobs/~016b4000a5635eebbe
        capture 016b4000a5635eebbe and return it"""
        job_id = url.split("~")[-1]
        return job_id

    def extract_job_title(self, job_data):
        """extract job title from passed job content-holding dict and create object property"""
        self.__job_title = job_data["profile"]["op_title"]
        return self.__job_title

    def extract_other_opened_jobs(self, job_data, upwork_client):
        """from passed job content-holding dict extract keys of other opened jobs and using upwork client make requests to get job content-holding dict and extract job title for each such job"""
        other_opened_jobs = []  # list of Job objects

        upwork_job_generic_url = "https://www.upwork.com/jobs/"
        for _, job_key in job_data["op_other_jobs"]["op_other_job"]:
            job_data = profile.Api(upwork_client).get_specific(job_key)
            full_job_url = upwork_job_generic_url + job_key

            job = Job(full_job_url)
            # inner initialization of job title
            job.extract_job_title(job_data)
            other_opened_jobs.append(job)

        self.__other_opened_jobs = other_opened_jobs
        return other_opened_jobs
