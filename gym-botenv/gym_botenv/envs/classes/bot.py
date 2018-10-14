

class Bot:
    """
    This class represent the bot parameters. It includes it's UA, it's IP
    and other further values
    """

    def __init__(self, ip: str, ua: str):
        self.ip = ip
        self.ua = ua
