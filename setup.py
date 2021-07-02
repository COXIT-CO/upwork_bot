"""Run setup.py before running other files. Then input required data."""
import sys
import argparse
import configparser
from os import path


def create_parser():
    """Creates parameters passed from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-cid", "--client_id")
    parser.add_argument("-csc", "--client_secret")
    parser.add_argument("-at", "--access_token")
    parser.add_argument("-eat", "--expires_at")
    parser.add_argument("-ein", "--expires_in")
    parser.add_argument("-rt", "--refresh_token")
    parser.add_argument("-tt", "--token_type")
    parser.add_argument("-sbt", "--slack_bot_token")
    parser.add_argument("-sss", "--slack_signing_secret")
    parser.add_argument("-swu", "--slack_webhook_url")

    return parser


def initialize_variables():
    """Using parser to output parameters from console"""
    configuration = configparser.ConfigParser()
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    if len(sys.argv) == 1:
        sys.exit(
            "Please check if you run script with parameters . Script is terminated"
        )

    configuration.add_section("UPWORK")
    configuration["UPWORK"]["client_id"] = namespace.client_id
    configuration["UPWORK"]["client_secret"] = namespace.client_secret
    configuration["UPWORK"]["access_token"] = namespace.access_token
    configuration["UPWORK"]["expires_at"] = namespace.expires_at
    configuration["UPWORK"]["expires_in"] = namespace.expires_in
    configuration["UPWORK"]["refresh_token"] = namespace.refresh_token
    configuration["UPWORK"]["token_type"] = namespace.token_type

    configuration.add_section("SLACK")
    configuration["SLACK"]["slack_bot_token"] = namespace.client_id
    configuration["SLACK"]["slack_signing_secret"] = namespace.client_secret
    configuration["SLACK"]["slack_webhook_url"] = namespace.access_token

    with open("settings.ini", "w") as configfile:  # save
        configuration.write(configfile)


if __name__ == "__main__":
    if path.isfile("settings.ini"):
        key = input("Do you really wanna change your settings?(y/n) ")
        if key == "y":
            initialize_variables()
        else:
            sys.exit("Script is terminated")
    else:
        initialize_variables()
