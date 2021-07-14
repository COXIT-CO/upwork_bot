from models import DB, Client, Job

URL = "https://www.upwork.com/jobs/"


class ClientController:
    @classmethod
    def create(cls, request_data=None):
        name = request_data[0]
        url = request_data[1]
        user = Client.query.filter_by(name=name).first()
        user_by_url = Client.query.filter_by(url=url).first()
        if user is not None or user_by_url is not None:
            return "User with this name or url is already exist!"
        new_user = Client(name=name, url=url)
        DB.session.add(new_user)
        DB.session.commit()
        return "Successfully created!"

    @classmethod
    def read(cls):
        users = Client.query.all()
        result_dict = {}
        for user in users:
            result_dict[user.name] = URL + user.url
        return result_dict

    @classmethod
    def delete(cls, client_name=None):
        user = Client.query.filter_by(name=client_name).first()
        if user is None:
            return "No such user!"
        else:
            list_of_urls = Job.query.filter_by(client_id=user.id).all()
            if len(list_of_urls) != 0:
                for data in list_of_urls:
                    delete_row = Job.query.filter_by(id=data.id).first()
                    DB.session.delete(delete_row)
                    DB.session.commit()
            DB.session.delete(user)
            DB.session.commit()
            return "Deleted successfully!"


class JobController:
    @classmethod
    def create(cls, request_data=None, url=None):
        user = Client.query.filter_by(url=url).first()
        if user is not None:
            if request_data is not None:
                for data in request_data:
                    if Job.query.filter_by(clients_url=data).first() is None:
                        new_url = Job(owner=user, clients_url=data)
                        DB.session.add(new_url)
                        DB.session.commit()
                    else:
                        return "Exists in database."
            return "This client has no open jobs now."

    @classmethod
    def read_user_urls(cls, client_name=None):
        user = Client.query.filter_by(name=client_name).first()
        urls_by_user = set()
        if user is None:
            return "No such user!"
        urls_by_user.add(URL + user.url)
        list_all_data_table = Job.query.filter_by(client_id=user.id)
        for url in list_all_data_table:
            urls_by_user.add(URL + url.clients_url)
        return urls_by_user

    @classmethod
    def read_urls_by_user(cls, client_name=None):
        user = Client.query.filter_by(name=client_name).first()
        urls_by_user = set()
        if user is None:
            return "No such user!"
        list_all_data_table = Job.query.filter_by(client_id=user.id)
        for url in list_all_data_table:
            urls_by_user.add(url.clients_url)
        return urls_by_user

    @classmethod
    def delete_not_actual(cls, request_data=None):
        for url in request_data:
            delete_row = Job.query.filter_by(clients_url=url).first()
            print(delete_row)
            DB.session.delete(delete_row)
            DB.session.commit()
        return "Deleted successfully!"

    @classmethod
    def add_new_actual(cls, client_name=None, request_data=None):
        user = Client.query.filter_by(name=client_name).first()
        job = Job.query.filter_by(clients_url=request_data).first()
        if user is not None:
            if job is None:
                add_new = Job(client_id=user.id, clients_url=request_data)
                DB.session.add(add_new)
                DB.session.commit()
                return 200
            else:
                return "This url already exists!"
