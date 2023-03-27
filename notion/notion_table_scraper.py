import validators
import os
from notion_database.database import Database
from helpers.exceptions import CustomException


def scrape_notion_table(notion_page_url: str, origin):
    """main function. Whole process from receiving link to notion page
    with database to return the extracted projects links in database"""
    is_url_valid = validators.url(notion_page_url)
    if not is_url_valid:
        raise CustomException("Notion table URL you have provided is invalid!")

    database_id = get_database_id_from_url(notion_page_url)
    if not is_database_id_valid(database_id):
        raise CustomException("Notion database id is invalid!")

    return get_projects_titles_and_urls(database_id, origin)


def get_projects_titles_and_urls(database_id: str, origin):
    """given database id extract all projects urls from table"""
    urls = []
    DB = Database(integrations_token=os.getenv("NOTION_TOKEN"))
    DB.retrieve_database(database_id=database_id)
    DB.find_all_page(database_id=database_id)

    if "results" not in DB.result:
        raise CustomException(
            "You have provided invalid notion token or notion table url is valid!"
        )
    for page in DB.result["results"]:
        try:
            if origin == "linkedin":
                title = page["properties"]["Company Name"]["title"][0]["text"][
                    "content"
                ]
            elif origin == "upwork":
                title = page["properties"]["Project Name"]["title"][0]["text"][
                    "content"
                ]
            url = page["properties"]["Link"]["url"]
        except KeyError:
            raise CustomException(
                "Your table doesn't have 'Project Name' and/or 'Link' fields!"
            )
        urls.append({"url": url, "title": title})

    return urls


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
