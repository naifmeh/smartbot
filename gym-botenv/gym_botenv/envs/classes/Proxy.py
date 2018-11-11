import pandas as pd
import time
from .State import State

def load_proxies(filename: str):
    try:
        proxies_file = pd.read_csv(filename)
        return proxies_file
    except Exception:
        raise Exception("File not found")


class Proxy:

    def __init__(self, ip: str, port: int, loc: str, https: bool):
        self.ip = ip
        self.country = loc
        self.port = port
        self.https = https

        self.used = 0

    def increment_counter(self):
        self.used += 1

    @staticmethod
    def populate_proxies():
        proxies = load_proxies('./data/proxies.csv')
        liste_pr = []
        for i in range(len(proxies)):
            ip = proxies['IP'][i]
            port = proxies['PORT'][i]
            code = proxies['CODE'][i]
            https = proxies['HTTPS'][i]
            liste_pr.append(Proxy(ip, port, code, https))

        return liste_pr

    @staticmethod
    def pick_new_proxy(liste_proxies: list):
        proxy = liste_proxies[0]
        liste_proxies.pop(0)
        liste_proxies.append(proxy)

        return proxy
    
    @staticmethod
    def sort_in_states(states_dict: dict, proxies: list):
        proxies_copy = proxies.copy()
        proxy_dict = {}
        for state in states_dict:
            for i, proxy in enumerate(proxies_copy):
                if state.range_used_proxy[0] <= proxy.used <= state.range_used_proxy[1]:
                    states_dict[state][2].append(proxy)
                    proxies_copy.pop(i)
                    proxy_dict[proxy] = state
        return proxy_dict
        
    @staticmethod
    def rearrange_proxy(states_dict: dict, proxies_dict: dict, proxy):
        state = proxies_dict(proxy)
        states_dict[state][2].pop(states_dict[state][2].index(proxy))

        for etat in states_dict:
            if etat.range_used_proxy[0] <= proxy.used <= etat.range_used_proxy[1]:
                states_dict[etat][3] = [proxy] + states_dict[etat][3]
                proxies_dict[proxy] = etat
                break
    @staticmethod
    def push_back_proxy(states_dict: dict, state: State):
        proxy_temp = states_dict[state][2][0]
        states_dict[state][2].pop(0)
        states_dict[state][2].append(proxy_temp)





