from .utils import read_file_as_list
import os


class Useragent:

    def __init__(self, ua: str):
        """
        :param ua: User agent
        """
        self.ua = ua
        self.used = 0

    def increment_use(self):
        self.used += 1

    @staticmethod
    def load_user_agents():
        directory = os.path.dirname(__file__)

        useragents = read_file_as_list(os.path.join(directory, '../data/uas'))
        useragents_obj = [Useragent(x) for x in useragents]
        del useragents

        return useragents_obj



