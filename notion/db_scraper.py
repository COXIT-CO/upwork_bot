from notion_database.database import Database
import dotenv
import os

dotenv.load_dotenv(".env")

def get_projects_urls(database_id: str):
    """given database id extract all projects urls from table"""
    projects_urls = []
    DB = Database(
        integrations_token=os.getenv("NOTION_TOKEN"))
    DB.retrieve_database(
        database_id=database_id)
    DB.find_all_page(database_id=database_id)
    for page in DB.result['results']:
        projects_urls.append(page['properties']['Link']['url'])

    return projects_urls


def get_database_id_from_url(url: str):
    url_ending = url.split("/")[-1]
    database_id = url_ending[:32]  # first 32 letters matching database id
    return database_id
