

class Bot:
    """
    This class represent the bot parameters. It includes it's UA, it's IP
    and other further values
    """

    def __init__(self, ip: str, ua: str):
        self.ip = ip
        self.ua = ua
        self.use_plugins = False
        self.use_language = False
        self.webdriver = True
        self.use_permissions = False

    def overall_grade(self):
        self.base_grade = 100



