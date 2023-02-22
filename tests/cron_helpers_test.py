from email.policy import default
import pytest
import os

current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
import sys

sys.path.append(level_up_directory_path)
os.environ[
    "TESTING"
] = "true"  # TESTING valiable should be initialized regardless the assigned value
from app.app import flask_app
from app.database import DB
from cron_jobs.helpers import (
    remove_job_from_db,
    remove_unactive_jobs_from_db,
    find_new_job_openings,
)
from upwork_part.schema.controllers import JobController
from upwork_part.schema.models import Job as JobModel

job_controller = JobController()


def setup_module(module):
    """setup any state specific to the execution of the given module."""
    with flask_app.app_context():
        DB.create_all()


@pytest.fixture
def remove_job_from_db_setup():
    with flask_app.app_context():
        job_controller.create(job_url="https://job_link.com", origin="upwork")


@pytest.mark.parametrize(
    "test",
    [
        None,  # wrong case
        "https://wrong_link",  # wrong case
        "https://job_link.com",  # successful case
    ],
)
def test_remove_job_from_db(remove_job_from_db_setup, test):
    with flask_app.app_context():
        match test:
            case None:
                assert (
                    remove_job_from_db(None)
                    == "You haven't provided job url! It's required"
                )
            case "https://wrong_link":
                assert (
                    remove_job_from_db("https://wrong_link") == "No such job opening!"
                )
            case "https://job_link.com":
                print(job_controller.get("https://job_link.com"))
                assert (
                    remove_job_from_db("https://job_link.com")
                    == "Deleted successfully!"
                )


@pytest.fixture
def test_remove_unactive_jobs_from_db_setup():
    with flask_app.app_context():
        for i in range(5):
            job_controller.create(
                job_url=f"https://upwork_link_{i}.com", origin="upwork"
            )
        for i in range(5):
            job_controller.create(
                job_url=f"https://linkedin_link_{i}.com", origin="linkedin"
            )
        job_controller.create(job_url="https://tempest_link.com", origin="tempest")


@pytest.mark.parametrize(
    "id,test",
    [
        (1, [f"https://upwork_link_{i}.com" for i in range(5)]),  # active jobs
        (2, ["https://unexisting_link.com" for _ in range(5)]),  # active jobs
        (
            3,
            [f"https://upwork_link_{i}.com" for i in range(3)]
            + ["https://unexisting_link.com" for _ in range(3)],
        ),  # active jobs
    ],
)
def test_remove_unactive_jobs_from_db(
    test_remove_unactive_jobs_from_db_setup, id, test
):
    with flask_app.app_context():
        match id:
            case 1:
                remove_unactive_jobs_from_db(test, "upwork")
                with flask_app.app_context():
                    for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                        if job_controller.get(job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    for job_url in [f"https://linkedin_link_{i}.com" for i in range(5)]:
                        if job_controller.get(job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    if job_controller.get("https://tempest_link.com") == "":
                        pytest.fail(f"Job https://tempest_link.com isn't found!")
            case 2:
                remove_unactive_jobs_from_db(test, "upwork")
                with flask_app.app_context():
                    for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                        if job_controller.get(job_url) != "":
                            pytest.fail(f"Job {job_url} must be removed!")
                    for job_url in [f"https://linkedin_link_{i}.com" for i in range(5)]:
                        if job_controller.get(job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    if job_controller.get("https://tempest_link.com") == "":
                        pytest.fail(f"Job https://tempest_link.com isn't found!")
            case 3:
                remove_unactive_jobs_from_db(test, "upwork")
                with flask_app.app_context():
                    for job_url in [
                        f"https://upwork_link_{i}.com" for i in range(3, 5)
                    ]:
                        if job_controller.get(job_url) != "":
                            pytest.fail(f"Job {job_url} must be removed!")
                    for job_url in [f"https://linkedin_link_{i}.com" for i in range(5)]:
                        if job_controller.get(job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    if job_controller.get("https://tempest_link.com") == "":
                        pytest.fail(f"Job https://tempest_link.com isn't found!")


@pytest.fixture
def test_find_new_job_openings_setup():
    with flask_app.app_context():
        for i in range(5):
            job_controller.create(
                job_url=f"https://upwork_link_{i}.com", origin="upwork"
            )


@pytest.mark.parametrize(
    "id,test",
    [
        (
            1,
            [
                {
                    "job_title": "upwork job {i}",
                    "job_url": f"https://upwork_link_{i}.com",
                }
                for i in range(5, 7)
            ],
        ),  # all new jobs
        (
            2,
            [
                {
                    "job_title": "upwork job {i}",
                    "job_url": f"https://upwork_link_{i}.com",
                }
                for i in range(5)
            ],
        ),  # already existing jobs
        (
            3,
            [
                {
                    "job_title": "upwork job {i}",
                    "job_url": f"https://upwork_link_{i}.com",
                }
                for i in range(3, 7)
            ],
        ),  # partially new jobs
        (
            4,
            [
                {
                    "job_title": "linkedin job {i}",
                    "job_url": f"https://linkedin_link_{i}.com",
                }
                for i in range(2)
            ],
        ),  # all new jobs with other origin
    ],
)
def test_find_new_job_openings(test_find_new_job_openings_setup, id, test):
    with flask_app.app_context():
        match id:
            case 1:
                find_new_job_openings(test, origin="upwork")
                with flask_app.app_context():
                    for job_url in [f"https://upwork_link_{i}.com" for i in range(7)]:
                        if job_controller.get(job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found in db!")
            case 2:
                find_new_job_openings(test, origin="upwork")
                if len(JobModel.query.all()) != 5:
                    pytest.fail("There must be exactly 5 jobs in db!")
                for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                    if job_controller.get(job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")
            case 3:
                find_new_job_openings(test, origin="upwork")
                if len(JobModel.query.all()) != 7:
                    pytest.fail("There must be exactly 7 jobs in db!")
                for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                    if job_controller.get(job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")
            case 4:
                find_new_job_openings(test, origin="linkedin")
                if len(JobModel.query.all()) != 7:
                    pytest.fail("There must be exactly 7 jobs in db!")
                for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                    if job_controller.get(job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")
                for job_url in [f"https://linkedin_link_{i}.com" for i in range(2)]:
                    if job_controller.get(job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")


def teardown_function():
    """teardown any state that was previously setup in our case with a pytest.fixture
    call.
    """
    with flask_app.app_context():
        for job in JobModel.query.all():
            job_controller.delete(job.job_url)


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    if os.path.exists("instance/test.db"):
        os.remove("instance/test.db")