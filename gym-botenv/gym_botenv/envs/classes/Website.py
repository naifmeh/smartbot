import uuid
import numpy as np
from .bot import Bot
from .Proxy import Proxy


class Website:

    def __init__(self, uid: uuid, grade:int, secu_provider: int, country: str, has_fp: bool, block_bots: bool, checks_head: bool,
                 checks_referer: bool, checks_rate: bool, average_visit: int):
        self.id = uid
        self.grade = grade
        self.security_provider = secu_provider
        self.country = country

        self.use_fp = has_fp
        self.block_bots = block_bots
        self.checks_referer = checks_referer
        self.checks_head = checks_head
        self.check_image_rate = checks_rate
        self.average_page_visits = average_visit

        self.uas_visited = {} # This should contain config - [amount, time step], at some timestep we can forge
        self.ips_visited = {}

    def update_bot_visit(self, bot: Bot):
        bot_tuple = bot.bot_ua_ip()
        if bot_tuple[0] in self.uas_visited.keys():
            self.uas_visited[bot_tuple[0]][0] += 1
        else:
            self.uas_visited[bot_tuple[0]] = [1, 1]

        if bot_tuple[1] in self.ips_visited.keys():
            self.ips_visited[bot_tuple[1]][0] += 1
        else:
            self.ips_visited[bot_tuple[1]] = [1, 1]

    def increment_bot_timestep(self):
        self.uas_visited = {x: [i[0], i[1] + 1] for x, i in self.uas_visited.items() if i[1] < 100}
        self.ips_visited = {x: [i[0], i[1] + 1] for x, i in self.ips_visited.items() if i[1] < 100}

    def _checks_ua(self, bot: Bot):
        threshold = (6-self.grade) * 25
        if bot.ua in self.uas_visited:
            if self.uas_visited[bot.ua][0] > threshold:
                return True # Introduce probability according to grade
        return False

    def _checks_ip(self, bot: Bot):
        if bot.proxy in self.ips_visited:
            if self.ips_visited[bot.ip][0] > ((6-self.grade)*25):
                return True
        return False

    def evaluate_bot(self, bot: Bot, security_providers: dict):
        if self.security_provider > 0:
            secu_provider = security_providers[self.security_provider]
            bloque = secu_provider.should_block_bot(bot)
            if bloque:
                block = np.random.choice([True, False], p=[0.9, 0.1])
                if block:
                    return block, -1

        score = 0
        if self.checks_referer:
            if not bot.referer:
                score += 10
        if self.checks_head:
            if bot.head:
                score += 10
        if self.check_image_rate:
            if bot.rate_load_pics < 0.3:
                score += 10
            elif 0.3 < bot.rate_load_pics < 0.7:
                score += 5
        if score == 25:
            block = np.random.choice([True, False], p=[0.8, 0.2])
            if block:
                return True, -5
        elif 25 > score > 10:
            block = np.random.choice([True, False], p=[0.3, 0.7])
            if block:
                return True, -5

        second_score = 0
        if self._checks_ua(bot):
            second_score += 10
        if self._checks_ip(bot):
            second_score += 10

        if second_score == 20:
            return True, -5
        elif second_score == 10:
            return np.random.choice([True, False], p=[0.8, 0.2]), -3

        if bot.page_visits > self.average_page_visits[1]:
            return True, -3

        if bot.documents and self.grade >= 3:
            block = np.random.choice([True, False], p=[0.6, 0.4])
            if block:
                return True, -3

        return False, 3

    def __str__(self):
        return """{ 'id' : %s, 'security_provider' : %d, 'fp' : %r, 'bb' : %r, 'visited' : %d } """ \
                   % (self.id, self.security_provider, self.use_fp, self.block_bots,)

    @staticmethod
    def generate_fake_sites(n_sites: int, security_providers: dict, prob_sp: float, prob_fp: float, prob_bb: float,
                            checks_ref: float, checks_hd: float, checks_img: float):
        """
        Generate a list of fake websites with different attributes.

        :return: list of nSites fake websites containing a tuple of values
        """

        secu_providers_probs = np.ones(len(security_providers), dtype=float) * (prob_sp / (len(security_providers) - 1))
        secu_providers_probs[0] = 1 - prob_sp

        proxies, _ = Proxy.populate_proxies()

        liste_websites = []
        for i in range(n_sites):
            id = str(uuid.uuid4())

            security_provider = np.random.choice(list(security_providers.keys()), p=secu_providers_probs)
            domain = np.random.choice(list(set(proxies['CODE'])))
            block_bots = np.random.choice([True, False], p=[prob_bb, 1 - prob_bb])
            fingerprinting = np.random.choice([True, False], p=[prob_fp, 1 - prob_fp])
            checks_referer = np.random.choice([True, False], p=[checks_ref, 1 - checks_ref])
            checks_head = np.random.choice([True, False], p=[checks_hd, 1 - checks_hd])
            checks_image = np.random.choice([True, False], p=[checks_img, 1 - checks_img])

            grade = np.random.choice(list(range(1, 6)))
            page_visits = {5 - i: (x, x + 10) for i, x in enumerate(list(range(0, 50, 10)))}

            liste_websites.append(Website(id, grade, security_provider, domain, fingerprinting, block_bots, checks_head,
                                          checks_referer, checks_image, page_visits[grade]))

        return liste_websites






