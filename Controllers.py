from Models import DB, RawData, AllData

URL = "https://www.upwork.com/jobs/"


class RawDataController:
    def create(self, request_data=None):
        name = request_data[0]
        url = request_data[1]
        user = RawData.query.filter_by(name=name).first()
        if user is not None:
            return "User with this name is already exist!"
        else:
            new_user = RawData(name=name, url=url)
            DB.session.add(new_user)
            DB.session.commit()
            return "Successfully created!"

    def read(self):
        users = RawData.query.all()
        result_dict = {}
        for user in users:
            result_dict[user.name] = URL + user.url
        return result_dict

    def delete(self, client_name=None):
        user = RawData.query.filter_by(name=client_name).first()
        if user is None:
            return "No such user!"
        else:
            list_of_urls = AllData.query.filter_by(client_id=user.id).all()
            if len(list_of_urls) != 0:
                for data in list_of_urls:
                    delete_row = AllData.query.filter_by(id=data.id).first()
                    DB.session.delete(delete_row)
                    DB.session.commit()
            DB.session.delete(user)
            DB.session.commit()
            return "Deleted successfully!"


class AllDataController:
    def create(self, request_data=None, url=None):
        user = RawData.query.filter_by(url=url).first()
        if user is not None:
            if request_data is not None:
                for data in request_data:
                    new_url = AllData(client=user, clients_url=data)
                    DB.session.add(new_url)
                    DB.session.commit()
            else:
                return "This client has no open jobs now."

    def read_user_urls(self, client_name=None):
        user = RawData.query.filter_by(name=client_name).first()
        urls_by_user = set()
        if user is None:
            return "No such user!"
        else:
            urls_by_user.add(URL + user.url)
            list_all_data_table = AllData.query.filter_by(client_id=user.id)
            for url in list_all_data_table:
                urls_by_user.add(URL + url.clients_url)
        return urls_by_user