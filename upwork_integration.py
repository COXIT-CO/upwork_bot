from pprint import pprint
import upwork
from upwork.routers import auth
from upwork.routers.jobs import profile

try:
    from configparser import ConfigParser
except Exception as e:
    raise e

configuration = ConfigParser()
configuration.read("settings.ini")


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
    except AttributeError:
        authorization_url, state = client.get_authorization_url()
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

    client_jobs = []
    response_dict = profile.Api(client).get_specific(data)
    list_of_jobs = response_dict["profile"]["op_other_jobs"]["op_other_job"]
    for item in list_of_jobs:
        client_jobs.append(item["op_ciphertext"])

    return client_jobs


if __name__ == "__main__":
    client = get_desktop_client()
    print("Input job link: ")
    url = input().split("~")
    result = "~" + url[1]

    try:
        print("Information")
        pprint(auth.Api(client).get_user_info())
        pprint(get_job(result))
    except Exception as e:
        print("Exception at %s %s" % (client.last_method, client.last_url))
        raise e
