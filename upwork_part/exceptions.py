class CustomException(Exception):
    def __init__(self, error_msg=None):
        self.__error_msg = error_msg if error_msg else None

    def __str__(self):
        return self.__error_msg
