import ipaddress
import uuid

class Bot:
    """
    This class represent the bot parameters. It includes it's UA, it's IP
    and other further values
    """

    def __init__(self, ip: str, ua: str, use_plugs: bool, use_language: bool, webdriver: bool, use_permissions: bool,
                 rate_load_pics=1.):
        self.id = str(uuid.uuid4())
        self.ip = ip
        self.ua = ua
        self.use_plugins = use_plugs
        self.use_language = use_language
        self.webdriver = webdriver
        self.referer = True
        self.use_permissions = use_permissions
        self.rate_load_pics = rate_load_pics

    def bot_tuple(self):
        return self.ip, self.ua, self.use_plugins, self.use_language, self.use_language, self.webdriver, \
               self.referer, self.use_permissions, self.rate_load_pics





