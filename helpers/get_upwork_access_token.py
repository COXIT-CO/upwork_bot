import upwork
from pprint import pprint


def get_desktop_client():
    """Emulation of desktop app.
    Your keys should be created with project type "Desktop".

    Returns: ``upwork.Client`` instance ready to work.

    """

    config = upwork.Config(
        {
            "client_id": "1c3cc82d1b899a9ee1e44681f1c43514",
            "client_secret": "fe9bec427ad322bf",
            "redirect_uri": "https://coxit.co/",
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
        print(authz_code)

        print("Retrieving access and refresh tokens.... ")
        token = client.get_access_token(authz_code)
        # WARNING: the access token will be refreshed automatically for you
        # in case it's expired, i.e. expires_at < time(). Make sure you replace the
        # old token accordingly in your security storage. Call client.get_actual_config
        # periodically to sync-up the data
        pprint(token)

    return client


if __name__ == "__main__":
    client = get_desktop_client()
