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
from helpers.db import (
    find_new_job_openings,
    find_new_invitations,
    remove_job_from_db,
    remove_unactive_jobs_from_db,
    remove_unactive_invitations_from_db,
)
from db_schema.controllers import JobController
from db_schema.controllers import InvitationController
from db_schema.models import Job as JobModel
from db_schema.models import Invitation

job_controller = JobController()
invitation_controller = InvitationController()


def setup_module(module):
    """setup any state specific to the execution of the given module."""
    with flask_app.app_context():
        DB.create_all()


@pytest.fixture
def remove_job_from_db_setup():
    with flask_app.app_context():
        job_controller.create(
            slack_channel_id="channel_id",
            job_url="https://job_link.com",
            origin="upwork",
        )


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
                assert remove_job_from_db("channel_id", None) == "No such job opening!"
            case "https://wrong_link":
                assert (
                    remove_job_from_db("channel_id", "https://wrong_link")
                    == "No such job opening!"
                )
            case "https://job_link.com":
                assert (
                    remove_job_from_db("channel_id", "https://job_link.com")
                    == "Deleted successfully!"
                )


@pytest.fixture
def test_remove_unactive_jobs_from_db_setup():
    with flask_app.app_context():
        for i in range(5):
            job_controller.create(
                slack_channel_id="channel_id",
                job_url=f"https://upwork_link_{i}.com",
                origin="upwork",
            )
        for i in range(5):
            job_controller.create(
                slack_channel_id="channel_id",
                job_url=f"https://linkedin_link_{i}.com",
                origin="linkedin",
            )
        job_controller.create(
            slack_channel_id="channel_id",
            job_url="https://tempest_link.com",
            origin="tempest",
        )


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
                remove_unactive_jobs_from_db("channel_id", test, "upwork")
                with flask_app.app_context():
                    for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                        if job_controller.get("channel_id", job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    for job_url in [f"https://linkedin_link_{i}.com" for i in range(5)]:
                        if job_controller.get("channel_id", job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    if (
                        job_controller.get("channel_id", "https://tempest_link.com")
                        == ""
                    ):
                        pytest.fail(f"Job https://tempest_link.com isn't found!")
            case 2:
                remove_unactive_jobs_from_db("channel_id", test, "upwork")
                with flask_app.app_context():
                    for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                        if job_controller.get("channel_id", job_url) != "":
                            pytest.fail(f"Job {job_url} must be removed!")
                    for job_url in [f"https://linkedin_link_{i}.com" for i in range(5)]:
                        if job_controller.get("channel_id", job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    if (
                        job_controller.get("channel_id", "https://tempest_link.com")
                        == ""
                    ):
                        pytest.fail(f"Job https://tempest_link.com isn't found!")
            case 3:
                remove_unactive_jobs_from_db("channel_id", test, "upwork")
                with flask_app.app_context():
                    for job_url in [
                        f"https://upwork_link_{i}.com" for i in range(3, 5)
                    ]:
                        if job_controller.get("channel_id", job_url) != "":
                            pytest.fail(f"Job {job_url} must be removed!")
                    for job_url in [f"https://linkedin_link_{i}.com" for i in range(5)]:
                        if job_controller.get("channel_id", job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found!")
                    if (
                        job_controller.get("channel_id", "https://tempest_link.com")
                        == ""
                    ):
                        pytest.fail(f"Job https://tempest_link.com isn't found!")


@pytest.fixture
def test_find_new_job_openings_setup():
    with flask_app.app_context():
        for i in range(5):
            job_controller.create(
                slack_channel_id="channel_id",
                job_url=f"https://upwork_link_{i}.com",
                origin="upwork",
            )


@pytest.mark.parametrize(
    "id,test",
    [
        (
            1,
            [
                {
                    "job_title": f"upwork job {i}",
                    "job_url": f"https://upwork_link_{i}.com",
                }
                for i in range(5, 7)
            ],
        ),  # all new jobs
        (
            2,
            [
                {
                    "job_title": f"upwork job {i}",
                    "job_url": f"https://upwork_link_{i}.com",
                }
                for i in range(5)
            ],
        ),  # already existing jobs
        (
            3,
            [
                {
                    "job_title": f"upwork job {i}",
                    "job_url": f"https://upwork_link_{i}.com",
                }
                for i in range(3, 7)
            ],
        ),  # partially new jobs
        (
            4,
            [
                {
                    "job_title": f"linkedin job {i}",
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
                find_new_job_openings("channel_id", test, origin="upwork")
                with flask_app.app_context():
                    for job_url in [f"https://upwork_link_{i}.com" for i in range(7)]:
                        if job_controller.get("channel_id", job_url) == "":
                            pytest.fail(f"Job {job_url} isn't found in db!")
            case 2:
                find_new_job_openings("channel_id", test, origin="upwork")
                if len(JobModel.query.all()) != 5:
                    pytest.fail("There must be exactly 5 jobs in db!")
                for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                    if job_controller.get("channel_id", job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")
            case 3:
                find_new_job_openings("channel_id", test, origin="upwork")
                if len(JobModel.query.all()) != 7:
                    pytest.fail("There must be exactly 7 jobs in db!")
                for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                    if job_controller.get("channel_id", job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")
            case 4:
                find_new_job_openings("channel_id", test, origin="linkedin")
                if len(JobModel.query.all()) != 7:
                    pytest.fail("There must be exactly 7 jobs in db!")
                for job_url in [f"https://upwork_link_{i}.com" for i in range(5)]:
                    if job_controller.get("channel_id", job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")
                for job_url in [f"https://linkedin_link_{i}.com" for i in range(2)]:
                    if job_controller.get("channel_id", job_url) == "":
                        pytest.fail(f"Job {job_url} isn't found in db!")


@pytest.fixture
def test_find_new_invitations_setup():
    with flask_app.app_context():
        for i in range(5):
            invitation_controller.create(f"https://invitation_{i}.com")


@pytest.mark.parametrize(
    "id,test",
    [
        (
            1,
            [
                {"text": f"inv {i}", "link": f"https://invitation_{i}.com"}
                for i in range(5, 7)
            ],
        ),  # all new invitations
        (
            2,
            [
                {"text": f"inv {i}", "link": f"https://invitation_{i}.com"}
                for i in range(5)
            ],
        ),  # already existing invitations
        (
            3,
            [
                {"text": f"inv {i}", "link": f"https://invitation_{i}.com"}
                for i in range(3, 7)
            ],
        ),  # partially new invitations
    ],
)
def test_find_new_invitations(test_find_new_invitations_setup, id, test):
    with flask_app.app_context():
        match id:
            case 1:
                find_new_invitations(test)
                with flask_app.app_context():
                    for inv_link in [f"https://invitation_{i}.com" for i in range(7)]:
                        if invitation_controller.get(inv_link) == "":
                            pytest.fail(f"Invitation {inv_link} isn't found in db!")
            case 2:
                find_new_invitations(test)
                if len(Invitation.query.all()) != 5:
                    pytest.fail("There must be exactly 5 invitations in db!")
                for inv_link in [f"https://invitation_{i}.com" for i in range(5)]:
                    if invitation_controller.get(inv_link) == "":
                        pytest.fail(f"Invitation {inv_link} isn't found in db!")
            case 3:
                find_new_invitations(test)
                if len(Invitation.query.all()) != 7:
                    pytest.fail("There must be exactly 7 invitations in db!")
                for inv_link in [f"https://invitation_{i}.com" for i in range(5)]:
                    if invitation_controller.get(inv_link) == "":
                        pytest.fail(f"Invitation {inv_link} isn't found in db!")


@pytest.fixture
def test_remove_unactive_invitations_from_db_setup():
    with flask_app.app_context():
        for i in range(5):
            invitation_controller.create(
                invitation_url=f"https://invitation_upwork_{i}.com"
            )
        for i in range(5):
            invitation_controller.create(
                invitation_url=f"https://invitation_linkedin_{i}.com"
            )
        invitation_controller.create(
            invitation_url=f"https://invitation_tempest_{i}.com"
        )


@pytest.mark.parametrize(
    "id,test",
    [
        (
            1,
            [
                {"text": f"inv {i}", "link": f"https://invitation_upwork_{i}.com"}
                for i in range(5)
            ],
        ),
        (
            2,
            [{"text": "inv", "link": "https://wrong_invitation.com"} for _ in range(5)],
        ),
        (
            3,
            [
                {"text": f"inv {i}", "link": f"https://invitation_upwork_{i}.com"}
                for i in range(3)
            ]
            + [
                {"text": "inv", "link": "https://invitation_upwork.com"}
                for _ in range(3)
            ],
        ),
    ],
)
def test_remove_unactive_invitations_from_db(
    test_remove_unactive_invitations_from_db_setup, id, test
):
    with flask_app.app_context():
        match id:
            case 1:
                remove_unactive_invitations_from_db(test)
                with flask_app.app_context():
                    if len(Invitation.query.all()) != 5:
                        pytest.fail("There must be exactly 5 invitations in db!")
            case 2:
                remove_unactive_invitations_from_db(test)
                with flask_app.app_context():
                    if len(Invitation.query.all()) != 0:
                        pytest.fail("There must no invitations in db!")
            case 3:
                remove_unactive_invitations_from_db(test)
                with flask_app.app_context():
                    if len(Invitation.query.all()) != 3:
                        pytest.fail("There must be exactly 3 invitations in db!")
                    for inv_url in [
                        f"https://invitation_upwork_{i}.com" for i in range(3)
                    ]:
                        if invitation_controller.get(inv_url) == "":
                            pytest.fail(f"Invitation {inv_url} must be in db!")


def teardown_function():
    """teardown any state that was previously setup in our case with a pytest.fixture
    call.
    """
    with flask_app.app_context():
        for job in JobModel.query.all():
            job_controller.delete("channel_id", job.job_url)
        for inv in Invitation.query.all():
            invitation_controller.delete(inv.url)


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module
    method.
    """
    if os.path.exists("instance/test.db"):
        os.remove("instance/test.db")
