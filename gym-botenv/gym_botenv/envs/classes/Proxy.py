import pandas as pd
import os
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
        directory = os.path.dirname(__file__)
        proxies = load_proxies(os.path.join(directory, '../data/proxies.csv'))
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







