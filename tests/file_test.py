import dotenv
import os
import pytest
import sys

dotenv.load_dotenv(".env")
current_directory_path = os.path.dirname(os.path.abspath(__file__))
level_up_directory_path = "/".join(current_directory_path.split("/")[:-1])
sys.path.insert(0, level_up_directory_path)

from db_schema.controllers import JobController
from db_schema.controllers import InvitationController
from db_schema.models import Job as JobModel
from helpers import file

job_controller = JobController()
invitation_controller = InvitationController()

FILE_PATH = ".env"


@pytest.fixture
def write_arg_to_file_setup():
    with open(FILE_PATH, "w") as f:
        pass


@pytest.mark.parametrize(
    "test",
    [("SOME_ARG", "some_value")],
)
def test_write_arg_to_file(write_arg_to_file_setup, test):
    file.write_arg_to_file(test[0], test[1], FILE_PATH)
    with open(FILE_PATH, "r") as f:
        lines = f.readlines()
    for line in lines:
        if "SOME_ARG" in line:
            break
    else:
        pytest.fail("Argument was written in file!")


@pytest.fixture
def delete_arg_from_file_setup():
    with open(FILE_PATH, "w") as f:
        f.write("SOME_ARG=some_value")


@pytest.mark.parametrize(
    "test",
    ["SOME_ARG"],
)
def test_delete_arg_from_file(delete_arg_from_file_setup, test):
    file.delete_arg_from_file(test, FILE_PATH)
    with open(FILE_PATH, "r") as f:
        lines = f.readlines()
    for line in lines:
        if "SOME_ARG" in line:
            pytest.fail("Argument was not removed from file!")


@pytest.fixture
def get_arg_value_from_file_setup():
    with open(FILE_PATH, "w") as f:
        f.write("SOME_ARG=some_value")


@pytest.mark.parametrize(
    "test",
    ["SOME_ARG"],
)
def test_get_arg_value_from_file(get_arg_value_from_file_setup, test):
    returned_value = file.get_arg_value_from_file(test, FILE_PATH)
    print(returned_value)
    if returned_value.split("=")[-1] != "some_value":
        pytest.fail("Value written from file isn't valid!")
