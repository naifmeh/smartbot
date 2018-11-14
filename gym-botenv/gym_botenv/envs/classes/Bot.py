import ipaddress
import uuid
import numpy.random as random
from .Proxy import Proxy
from .UserAgent import Useragent

class Bot:
    """
    This class represent the bot parameters. It includes it's UA, it's IP
    and other further values
    """

    def __init__(self,  ua: Useragent, ip: str, rate: float, proxy=None):
        self.id = str(uuid.uuid4())
        self.proxy = proxy
        self.ua = ua
        if not self.proxy:
            self.ip = ip
        else:
            self.ip = proxy.ip + ':' + str(proxy.port)
        self.referer = True
        self.head = True
        self.documents = False
        self.rate_load_pics = rate

    def bot_tuple(self):
        return self.proxy, self.ua, self.referer, self.head, self.documents, self.rate_load_pics

    def bot_ua_ip(self):
        return self.proxy, self.ua

    def __eq__(self, other):
        if self.proxy == other.proxy and self.ip == other.ip and self.ua == other.ua:
            return True
        return False

    def __str__(self):
        return "{'proxy':%s, 'ua':%s, referer:%r, head:%r, documents:%r, page_visits:%d," \
               "rate_load_pics:%lf"%(self.proxy, self.ua, self.referer, self.head, self.documents,
                                          self.page_visits, self.rate_load_pics)


