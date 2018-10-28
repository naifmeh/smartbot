import ipaddress
import uuid
import numpy.random as random

class Bot:
    """
    This class represent the bot parameters. It includes it's UA, it's IP
    and other further values
    """

    def __init__(self, ip: str, ua: str, page_visits: tuple, use_head: bool, load_documents: bool,
                 use_referer: bool, rate_load_pics=1.):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.ua = ua
        self.referer = use_referer
        self.head = use_head
        self.documents = load_documents
        self.page_visits = random.choice(page_visits)
        self.rate_load_pics = rate_load_pics

    def bot_tuple(self):
        return self.ip, self.ua, self.referer, self.head, self.documents, self.rate_load_pics

    def bot_ua_ip(self):
        return self.ip, self.ua

    def __str__(self):
        return "{'ip':%s, 'ua':%s, referer:%r, head:%r, documents:%r, page_visits:%d," \
               "rate_load_pics:%lf"%(self.ip, self.ua, self.referer, self.head, self.documents,
                                          self.page_visits, self.rate_load_pics)


