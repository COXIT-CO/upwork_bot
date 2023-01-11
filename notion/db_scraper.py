import dotenv
import os
import validators
from notion_database.database import Database

dotenv.load_dotenv(".env")


def run(notion_page_url: str):
    """whole process from receiving link to notion page with database
    to return the extracted projects links in database"""
    is_url_valid = validators.url(notion_page_url)
    if is_url_valid:
        database_id = get_database_id_from_url(notion_page_url)
        if is_database_id_valid(database_id):
            # return list with projects urls or None that is converted to False
            return get_projects_urls(database_id)


def get_projects_urls(database_id: str):
    """given database id extract all projects urls from table"""
    projects_urls = []
    DB = Database(integrations_token=os.getenv("NOTION_TOKEN"))
    DB.retrieve_database(database_id=database_id)
    DB.find_all_page(database_id=database_id)
    for page in DB.result["results"]:
        projects_urls.append(page["properties"]["Link"]["url"])

    return projects_urls


def get_database_id_from_url(url: str):
    url_ending = url.split("/")[-1]
    # if database id contains hyphens capture first 36 letters else 32
    database_id = url_ending[:36] if "-" in url_ending[:36] else url_ending[:32]
    return database_id


def is_database_id_valid(database_id: str):
    if len(database_id) not in (32, 36):
        return False
    for letter in database_id:
        if not (letter.isalnum() or letter.isalpha() or letter == "-"):
            return False
    return True
