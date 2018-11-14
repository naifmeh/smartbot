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
    def map_actions(actions, bot: Bot, uas: list, ips: list, proxies: list):
        ua = bot.ua
        proxy = None
        rate = bot.rate_load_pics
        ip = bot.ip

        for action in actions:
            if action == 0: # Change UA
                ua = uas[0]
                Useragent.push_back_ua(uas)
            elif action == 1: # CHange ip
                ip = ips[0]
                tmp = ips[0]
                ips.pop(0)
                ips.append(tmp)
            elif action == 2: # Change proxy
                proxy = Proxy.pick_new_proxy(proxies)
            elif action == 3: # Change rate (add)
                if rate < 1.:
                    rate += 0.1
                else:
                    rate = 1.
            elif action == 4: # Change rate (diminue)
                if rate > 0.:
                    rate -= 0.1
                else:
                    rate = 0.
            elif action == 5: # Do nothing
                continue
                
        return ua, proxy, ip, rate

            
                
                

