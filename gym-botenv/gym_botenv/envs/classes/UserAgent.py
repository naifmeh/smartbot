from .utils import read_file_as_list
import os
from .State import State




class Useragent:

    def __init__(self, ua: str):
        """
        :param ua: User agent
        """
        self.ua = ua
        self.used = 0

    def increment_counter(self):
        self.used += 1

    @staticmethod
    def populate_agents():
        directory = os.path.dirname(__file__)

        useragents = read_file_as_list(os.path.join(directory, '../data/uas'))
        useragents_obj = [Useragent(x) for x in useragents]
        del useragents

        return useragents_obj

    @staticmethod
    def push_back_ua(uas_liste: list):
        ua_temp = uas_liste[0]
        uas_liste.pop(0)
        uas_liste.append(ua_temp)
        




