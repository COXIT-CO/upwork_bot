import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-ci", "--client_id")
parser.add_argument("-cs", "--client_secret")
parser.add_argument("-rt", "--refresh_token")
parser.add_argument("-sbt", "--slack_bot_token")
parser.add_argument("-sss", "--slack_signing_secret")
parser.add_argument("-nt", "--notion_token")

args = parser.parse_args()
