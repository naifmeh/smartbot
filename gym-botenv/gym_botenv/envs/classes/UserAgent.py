
class Useragent:

    def __init__(self, ua: str):
        """
        :param ua: User agent
        """
        self.ua = ua
        self.used = 0

    def increment_use(self):
        self.used += 1
