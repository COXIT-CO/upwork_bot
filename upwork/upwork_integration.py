import logging
import upwork
import requests
from upwork.routers.jobs import profile

LOGGER = logging.getLogger()


class UpworkClient:
    """class holding all-upwork-binded information including upwork client to successfully access Upwork API"""

    def __init__(self, client_id, client_secret, redirect_url, access_token_data):
        """
        e.g. of access_token_data parameter:
        {
            'access_token': 'your_access_token',
            'expires_at': 123456789.1234567,
            'expires_in': 86400,
            'refresh_token': 'your_refresh_token',
            'token_type': 'Bearer'
        }
        """
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__redirect_url = redirect_url
        self.__access_token_data = access_token_data
        self.__client = self.get_upwork_client(client_id, client_secret, redirect_url)

    @staticmethod
    def get_upwork_client(client_id, client_secret, access_token_data):
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

    def refresh_access_token_data(self):
        """
        once upwork access token expires (it's valid for 24 hours) we need to refresh it using refresh token that is valid for 2 weeks

        return result is dictionary of same key-value structure as access_token_data parameter in __init__ method. Take a look at comment for it
        """
        url = "https://www.upwork.com/api/v3/oauth2/token"
        refresh_token = self.__access_token_data["refresh_token"]
        parameters = {
            "grant_type": "refresh_token",
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "redirect_url": self.__redirect_url,
            "refresh_token": refresh_token,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        refreshed_access_token_data = requests.post(
            url=url, params=parameters, headers=headers
        )
        # update access token data and upwork client
        self.__access_token_data = refreshed_access_token_data.json()
        self.__client = self.get_upwork_client(
            self.__client_id, self.__client_secret, self.__access_token_data
        )


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
