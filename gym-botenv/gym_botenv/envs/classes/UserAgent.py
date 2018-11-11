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
    def sort_in_state(states_dict: dict, uas: list):
        uas_copy = uas.copy()
        for state in states_dict:
            for i, ua in enumerate(uas_copy):
                if state.range_used_ua[0] <= ua.used <= state.range_used_ua[1]:
                    states_dict[state][1].append(ua)
                    uas_copy.pop(i)
    @staticmethod
    def rearrange_ua(states_dict: dict, uas_dict: dict, ua):
        state = uas_dict[ua]
        states_dict[state][1].pop(states_dict[state][1].index(ua))
        
        for etat in states_dict:
            if etat.range_used_ua[0] <= ua.used <= etat.range_used_ua[1]:
                states_dict[etat][1] = [ua] + states_dict[etat][1]
                uas_dict[ua] = etat
                break
    @staticmethod
    def push_back_ua(states_dict: dict, state: State):
        ua_temp = states_dict[state][1][0]
        states_dict[state][1].pop(0)
        states_dict[state][1].append(ua_temp)
        




