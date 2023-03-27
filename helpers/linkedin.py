import selenium.webdriver
import time


def scroll_page_down(driver: selenium.webdriver):
    """given selenium webdriver instance scroll the current html page driver is on down"""
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
    time.sleep(1)


def extract_job_title(full_job_url: str):
    if "/view/" in full_job_url:
        return full_job_url.split("?")[0]
    elif "currentJobId" in full_job_url:
        return full_job_url.split("&")[0]


def trim_company_url(url: str):
    url_pieces = url.split("/")
    company_name = url_pieces[url_pieces.index("company") + 1]
    return "https://www.linkedin.com/company/" + company_name


def is_company_url_valid(url: str):
    """given link to a linkedin company validate it and return the result of whether the link is correct or not"""
    if len(url.split("https://www.linkedin.com/company/")) == 2 or len(url.split("http://www.linkedin.com/company/")) == 2:
        return True
    return False


def paginate_jobs(companies_data):
    divided_jobs = [[]]
    how_many_symbols = 0
    for item in companies_data:
        company_title = item["company_title"]
        company_url = item["company_url"]
        how_many_symbols += (
            len("company_title" + "company_url") + len(company_title) + len(company_url)
        )
        if how_many_symbols >= 2700:
            how_many_symbols = (
                len("company_title" + "company_url")
                + len(company_title)
                + len(company_url)
            )
            divided_jobs.append([])
        last_item = divided_jobs[-1]
        last_item.append(
            {"company_title": company_title, "company_url": company_url, "jobs": []}
        )
        jobs = item["jobs"]
        company_data = last_item[-1]
        for job_data in jobs:
            job_url = job_data["job_url"]
            job_title = job_data["job_title"]
            if (
                how_many_symbols
                + len("job_title" + "job_url")
                + len(job_url)
                + len(job_title)
                >= 2700
            ):
                if len(company_data["jobs"]) == 0:
                    last_item.pop(-1)
                how_many_symbols = (
                    len("job_url" + "job_title") + len(company_title) + len(company_url)
                )
                divided_jobs.append([])
                last_item = divided_jobs[-1]
                last_item.append(
                    {
                        "company_title": company_title,
                        "company_url": company_url,
                        "jobs": [],
                    }
                )
                company_data = last_item[-1]
            company_data["jobs"].append({"job_url": job_url, "job_title": job_title})
            how_many_symbols += (
                len("job_url" + "job_title") + len(job_title) + len(job_url)
            )
    return divided_jobs
