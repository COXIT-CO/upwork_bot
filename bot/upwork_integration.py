import logging
from pprint import pprint
import upwork
from upwork.routers import auth
from upwork.routers.jobs import profile
from configparser import ConfigParser

configuration = ConfigParser()
configuration.read("settings.ini")

LOGGER = logging.getLogger()


def get_desktop_client():
    token = {
        "access_token": configuration.get("UPWORK", "access_token"),
        "expires_at": configuration.getfloat("UPWORK", "expires_at"),
        "expires_in": configuration.getint("UPWORK", "expires_in"),
        "refresh_token": configuration.get("UPWORK", "refresh_token"),
        "token_type": configuration.get("UPWORK", "token_type"),
    }

    config = upwork.Config(
        {
            "client_id": configuration.get("UPWORK", "client_id"),
            "client_secret": configuration.get("UPWORK", "client_secret"),
            "token": token,
        }
    )
    client = upwork.Client(config)

    try:
        config.token
    except AttributeError as e:
        authorization_url, state = client.get_authorization_url()
        LOGGER.error("Upw auth error: ", e)
        # cover "state" flow if needed
        authz_code = input(
            "Please enter the full callback URL you get "
            "following this link:\n{0}\n\n> ".format(authorization_url)
        )
        print("Retrieving access and refresh tokens.... ")
        token = client.get_access_token(authz_code)
        # WARNING: the access token will be refreshed automatically for you
        # in case it's expired, i.e. expires_at < time(). Make sure you replace the
        # old token accordingly in your security storage. Call client.get_actual_config
        # periodically to sync-up the data
        pprint(token)
        print("OK")

    return client


def get_job(data: str) -> list:
    client = get_desktop_client()
    client_jobs = []
    response_dict = profile.Api(client).get_specific(data)
    list_of_jobs = response_dict["profile"]["op_other_jobs"]
    if len(list_of_jobs) == 0:
        client_jobs = None
        return client_jobs
    else:
        list_of_jobs = response_dict["profile"]["op_other_jobs"]["op_other_job"]
        if isinstance(list_of_jobs, list) and len(list_of_jobs) > 1:
            for item in list_of_jobs:
                client_jobs.append(item["op_ciphertext"])
        else:  # 1 dict
            for item in list_of_jobs.values():
                client_jobs.append(item)
        return client_jobs
