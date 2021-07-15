import unittest
from main import DB, app
from models import Client, Job
from controllers import ClientController, JobController


def data_to_client():
    user = Client(name="Kate", url="~012e124456e16572e7")
    user2 = Client(name="Vova", url="~01d924c5f6e5aa0918")
    user3 = Client(name="Ira", url="~016ae5b7934dbca5e8")
    user.save()
    user2.save()
    user3.save()


def data_to_job():
    job = Job(client_id=2, clients_url="~012e124456e165770")
    job2 = Job(client_id=2, clients_url="~012e124456e165780")
    job3 = Job(client_id=3, clients_url="~012e124456e165710")
    job.save()
    job2.save()
    job3.save()


class TestClient(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self._app = app.test_client()

    def tearDown(self):
        user = Client.query.all()
        for i in user:
            DB.session.delete(i)
            DB.session.commit()

    def test_create_client_200(self):
        data = ["Kate", "~012e124456e16572e7"]
        assert ClientController.create(data) == "Successfully created!"

    def test_create_client_404(self):
        user = Client(name="Kate", url="~012e124456e16572e7")
        user.save()
        data = ["Kate", "~012e124456e16572e7"]
        assert (
            ClientController.create(data)
            == "User with this name or url is already exist!"
        )

    def test_read_client_data_200(self):
        expected = {
            "Kate": "https://www.upwork.com/jobs/~012e124456e16572e7",
            "Vova": "https://www.upwork.com/jobs/~01d924c5f6e5aa0918",
            "Ira": "https://www.upwork.com/jobs/~016ae5b7934dbca5e8",
        }
        data_to_client()
        assert ClientController.read() == expected

    def test_delete_certain_404(self):
        data = "TEST"
        assert ClientController.delete(data) == "No such user!"

    def test_delete_certain_200(self):
        data_to_client()
        data = "Kate"
        assert ClientController.delete(data) == "Deleted successfully!"

    def test_create_200(self):
        data_to_client()
        data = ["~0104ed8821eaaefd6e", "~01cd8382ed0dc92c24"]
        url = "~012e124456e16572e7"
        assert JobController.create(data, url) == "Successfully saved."

    def test_create_400(self):
        data_to_client()
        data = []
        url = "~012e124456e16572e7"
        assert JobController.create(data, url) == "This client has no open jobs now."

    def test_read_user_urls_404(self):
        data_to_client()
        data = "TEST"
        assert JobController.read_user_urls(data) == "No such user!"

    def test_read_user_urls_200(self):
        data_to_client()
        data_to_job()
        data = "Vova"
        expected = {
            "https://www.upwork.com/jobs/~01d924c5f6e5aa0918",
            "https://www.upwork.com/jobs/~012e124456e165780",
            "https://www.upwork.com/jobs/~012e124456e165770",
        }
        assert JobController.read_user_urls(data) == expected

    def test_read_urls_by_200(self):
        data_to_client()
        data_to_job()
        data = "Vova"
        expected = {"~012e124456e165770", "~012e124456e165780"}
        assert JobController.read_urls_by_user(data) == expected

    def test_read_urls_by_404(self):
        data_to_client()
        data = "TEST"
        assert JobController.read_urls_by_user(data) == "No such user!"

    def test_delete_unactual_200(self):
        data_to_client()
        data_to_job()
        data = {"~012e124456e165770", "~012e124456e165710"}
        assert JobController.delete_not_actual(data) == "Deleted successfully!"

    def test_add_actual_200(self):
        data_to_client()
        data_to_job()
        name = "Kate"
        data = "~012e124456e165775"
        assert JobController.add_new_actual(name, data) == 200

    def test_add_actual_400(self):
        data_to_client()
        data_to_job()
        name = "Vova"
        data = "~012e124456e165780"
        assert JobController.add_new_actual(name, data) == "This url already exists!"


if __name__ == "__main__":
    unittest.main()
