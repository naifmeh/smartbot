import itertools
from .Proxy import *
from .Website import *
from .UserAgent import *


class Actions:
    """
    Class mapping actions to their behavior and various utils methods.
    """

    def __init__(self):
        pass

    @staticmethod
    def generate_actions_combination(main_actions: list):
        """
        Total amount of combinations is computable by the sum for i to N, with i starting
         at 1 (C(N,i))
        :return: list of tuples of possible combinations
        """
        list_actions = []
        for index in range(1, len(main_actions)+1):
            elements = itertools.combinations(main_actions, index)
            for element in elements:
                list_actions.append(element)

        dico_actions = {i: x for i, x in enumerate(list_actions)}
        return dico_actions

    @staticmethod
    def map_actions(actions, bot: Bot, state: State, states_dict: dict):
        ua = bot.ua
        proxy = bot.proxy
        website = states_dict[state][0][0]
        directory = os.path.dirname(__file__)
        for action in actions:
            if action == 0:
                ua = states_dict[state][1][0]
                Useragent.push_back_ua(states_dict, state)
            else if action == 1:
                proxy = states_dict[state][2][0]
                Proxy.push_back_proxy(states_dict, state)
            else if action == 2:
                Website.push_back_website(states_dict, state)
                website = states_dict[state][0][0]
            else if action == 3:
                continue
                
        return ua, proxy, website

            
                
                

