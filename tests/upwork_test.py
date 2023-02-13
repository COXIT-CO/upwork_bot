import os
import dotenv

dotenv.load_dotenv(".env")
import pytest
from ..upwork_part.exceptions import CustomException
from ..upwork_part.upwork_integration import UpworkClient, Job

UPWORK_CLIENT_ID = os.getenv("CLIENT_ID")
UPWORK_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
ACCESS_TOKEN_DATA = {"refresh_token": REFRESH_TOKEN}


@pytest.mark.parametrize(
    "test_id,client_id,client_secret,access_token_data",
    [
        # valid test
        (
            1,
            UPWORK_CLIENT_ID,
            UPWORK_CLIENT_SECRET,
            ACCESS_TOKEN_DATA,
        ),  # single possible valid test
        # invalid tests
        # invalid client id
        (2, None, UPWORK_CLIENT_SECRET, ACCESS_TOKEN_DATA),
        # invalid client secret
        (4, UPWORK_CLIENT_ID, None, ACCESS_TOKEN_DATA),
        # invalid refresh token
        (
            6,
            UPWORK_CLIENT_ID,
            UPWORK_CLIENT_SECRET,
            {"refresh_token": "invalid_refresh_token"},
        ),
        # empty access token data
        (
            7,
            UPWORK_CLIENT_ID,
            UPWORK_CLIENT_SECRET,
            {},
        ),
    ],
)
def test_upwork_client(test_id, client_id, client_secret, access_token_data):
    """this function tests creation of UpworkClient class and its behaviour during wrong data expected to raise an error"""
    if test_id == 1:
        # successful test with all parameters provided and valid
        assert UpworkClient(client_id, client_secret, access_token_data)
    else:
        # any test case appeared here must fail to pass test
        pytest.mark.xfail(strict=True)
        with pytest.raises(Exception):
            UpworkClient(client_id, client_secret, access_token_data)


class TestUpworkJob:
    """class for testing Job class from upwork.upwork_integration module"""

    @pytest.mark.parametrize(
        "test_id,job_url",
        [
            (1, "https://www.upwork.com/jobs/~016b4000a5025eebbc"),  # successful test
            (2, "https://www.upwork.com/jobs/~016b40a5025eabbc"),  # wrong job key
            (3, "https:/wrong_url.com"),  # wrong job utl
        ],
    )
    def test_get_job(self, test_id, job_url):
        upwork_client = UpworkClient(
            UPWORK_CLIENT_ID, UPWORK_CLIENT_SECRET, ACCESS_TOKEN_DATA
        )

        if test_id == 1:
            job = Job(job_url)
            job.get_job(upwork_client.receive_upwork_client())
            assert type(job) == Job
        elif test_id == 2:
            """should raise an exception on the stage of getting job info"""
            pytest.mark.xfail(strict=True)
            job = Job(job_url)
            with pytest.raises(CustomException):
                job.get_job(
                    upwork_client.receive_upwork_client()
                )  # wrong job key should raise an exception
        elif test_id == 3:
            """should raise an exception on the stage of Job object creation"""
            pytest.mark.xfail(strict=True)
            with pytest.raises(CustomException):
                Job(job_url)  # wrong utl should raise an exception
