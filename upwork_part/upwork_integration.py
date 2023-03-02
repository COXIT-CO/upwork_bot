import logging
import os
import requests
import upwork
import validators
from upwork.routers import auth
from upwork.routers.jobs import profile
import os

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])

import sys

sys.path.insert(0, level_up_directory_path)
from helpers import exceptions

LOGGER = logging.getLogger()


class UpworkClient:
    """class holding all-upwork-binded information including upwork client to successfully access Upwork API"""

    def __init__(self, client_id, client_secret, access_token_data):
        """Initialization with Upwork client credentials to successfully access Upwork API

        :param client_id: Upwork client id
        :param client secret: Upwork client secret
        :param access_token_data: tokens-holding dictionary, as the stage of initialization should only have refresh token, which access one can be obtained from. E.g. :
            {'refresh_token': 'your_refresh_token'}
        """
        self.__client_id = client_id
        self.__client_secret = client_secret
        access_token_data["token_type"] = "Bearer"
        self.__access_token_data = access_token_data
        # upwork cleint will be created regardless of whether above parameters are valid
        self.__client = self.get_upwork_client(
            client_id, client_secret, access_token_data
        )
        # validation function will generate upwork client to access Upwork API
        self.validate_parameters(client_id, client_secret, access_token_data)

    def validate_parameters(self, client_id, client_secret, access_token_data):
        """Verify client id, client secret and access_token_data (contains access_token and refresh_token) parameters aren't empty, have proper types and acceptable by Upwork platform"""
        upwork_client_parameters = {
            "Client id": (client_id, str),
            "Client secret": (client_secret, str),
            "Access token data": (access_token_data, dict),
        }
        for key, value in upwork_client_parameters.items():
            if value is None or not value[0] or type(value[0]) != value[1]:
                raise exceptions.CustomException(
                    f"{key} is empty or its type isn't {value[1]}!"
                )
        refresh_token = access_token_data["refresh_token"]
        if refresh_token is None or not refresh_token or type(refresh_token) != str:
            raise exceptions.CustomException(
                "Refresh token is empty or its type isn't str!"
            )
        # to refresh access token we must have valid client id, secret and refresh token, so function invocation can be treated as validation
        self.refresh_access_token_data()
        # send some request ti Upwork server to verify access token
        auth.Api(self.__client).get_user_info()

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

    def update_token_data(self, token_data):
        """
        function invoked when refresh token expires, so we pass new token data to asign it to upwork client object
        :param token_data: looks like this
        {
            'access_token': <access_token>,
            'expires_at': 1234567890.12345,
            'expires_in': 86400,
            'refresh_token': <refresh_token>,
            'token_type': 'Bearer'
        }
        """
        # update access token data and upwork client
        self.__access_token_data = token_data
        self.__client = self.get_upwork_client(
            self.__client_id, self.__client_secret, self.__access_token_data
        )

    def receive_upwork_client(self):
        return self.__client


class Job:
    def __init__(self, job_url):
        required_url_substring = "www.upwork.com/jobs"
        if validators.url(job_url) and required_url_substring in job_url:
            self.__job_url = job_url
        else:
            raise exceptions.CustomException(f"Job url {job_url} is invalid!")

    def serialize_job(self):
        """convert job to python dict object"""
        serialized_job_info = {"job_url": self.__job_url}
        other_opened_jobs = []
        for other_job in self.__other_opened_jobs:
            other_job_info = {
                "job_url": other_job.__job_url,
                "job_title": other_job.__job_title,
            }
            other_opened_jobs.append(other_job_info)
        serialized_job_info["other_opened_jobs"] = other_opened_jobs
        return serialized_job_info

    def get_job(self, upwork_client):
        """
        main method to get full neccessary info about job
        given job url extract info about job itself: title and other job openings
        """
        job_key = self.get_job_id_from_url(self.__job_url)
        try:
            job_data = profile.Api(upwork_client).get_specific(job_key)
        except requests.exceptions.JSONDecodeError:
            raise exceptions.CustomException(
                f"Your job {self.__job_url} contains wrong job key {job_key}. Verify it is of structure https://www.upwork.com/jobs/~ + alphanumeric id!"
            )
        if "error" in job_data:
            raise exceptions.CustomException(
                f"Your job {self.__job_url} is private and not accessible or contains wrong job key {job_key} and can't be found!"
            )

        job = Job(self.__job_url)
        # here we pass upwork client because for each job opening we need to make request to get job url
        job.extract_other_opened_jobs(job_data, upwork_client)

        return job

    @staticmethod
    def get_job_id_from_url(url: str):
        """having generic url https://www.upwork.com/jobs/~016b4000a5635eebbe
        capture 016b4000a5635eebbe and return it"""
        url = url[:-1] if url.endswith("/") else url
        job_id = "~" + url.split("~")[-1]
        return job_id

    def extract_job_title(self, job_data):
        """extract job title from passed job content-holding dict and create object property"""
        return job_data["profile"]["op_title"]

    def extract_other_opened_jobs(self, job_data, upwork_client):
        """from passed job content-holding dict extract keys of other opened jobs and using upwork client make requests to get job content-holding dict and extract job title for each such job"""
        other_opened_jobs = []  # list of Job objects
        upwork_job_generic_url = "https://www.upwork.com/jobs/"

        if not job_data["profile"]["op_other_jobs"]:
            self.__other_opened_jobs = []
            return ""
        other_opened_jobs_data = job_data["profile"]["op_other_jobs"]["op_other_job"]
        if len(other_opened_jobs_data) == 1:
            # client has only one other job
            full_job_url = (
                upwork_job_generic_url
                + job_data["profile"]["op_other_jobs"]["op_other_job"]["op_ciphertext"]
            )
            job = Job(full_job_url)
            other_job_key = job_data["profile"]["op_other_jobs"]["op_other_job"][
                "op_ciphertext"
            ]
            other_job_data = profile.Api(upwork_client).get_specific(other_job_key)
            # inner initialization of job title
            job_title = job.extract_job_title(other_job_data)
            job.__job_title = job_title
            other_opened_jobs.append(job)
        else:
            # client has many other jobs
            for job_dict in other_opened_jobs_data:
                job_key = job_dict["op_ciphertext"]
                job_data = profile.Api(upwork_client).get_specific(job_key)
                if "error" in job_data:
                    continue
                full_job_url = upwork_job_generic_url + job_key

                job = Job(full_job_url)
                # inner initialization of job title
                job_title = job.extract_job_title(job_data)
                job.__job_title = job_title
                other_opened_jobs.append(job)

        self.__other_opened_jobs = other_opened_jobs
        return other_opened_jobs


upwork_client = UpworkClient(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    access_token_data={"refresh_token": os.getenv("REFRESH_TOKEN")},
)
