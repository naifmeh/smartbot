import pandas as pd
import time


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

    def increment_use(self):
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
            liste_pr.append(ip, port, code, https)

        return liste_pr



