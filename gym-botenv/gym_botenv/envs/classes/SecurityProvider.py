import numpy as np
import random
from .Bot import Bot


class SecurityProvider:

    def __init__(self, id_sp: int, grade_sp: int):
        self.id = id_sp
        self.grade = grade_sp

        self.counter_visited = 0

        self.list_ips = {}
        self.list_uas = {}

    def increment_counter(self):
        self.counter_visited += 1

    def update_bot_visit(self, bot: Bot):

        if bot.ua in self.list_uas.keys():
            self.list_uas[bot.ua][0] += 1
        else:
            self.list_uas[bot.ua] = [1, 1]

        if bot.proxy in self.list_ips.keys():
            self.list_ips[bot.proxy][0] += 1
        else:
            self.list_ips[bot.proxy] = [1, 1]

    def increment_timestep(self):
        self.list_uas = {x: [i[0], i[1] + 1] for x, i in self.list_uas.items() if i[1] < (self.grade * 50)}
        self.list_ips = {x: [i[0], i[1] + 1] for x, i in self.list_ips.items() if i[1] < (self.grade * 50)}

    def add_website(self, website):
        self.list_websites.append(website)

    def should_block_bot(self, bot: Bot):
        lowest_prob = 0.8
        highest_prob = 0.99
        lowest_grade = 1
        highest_grade = 10

        def formula(x): return ((x-lowest_grade)*(highest_prob - lowest_prob))/(highest_grade - lowest_grade) + lowest_prob

        prob = np.ones(2, dtype=float) * formula(self.grade)
        if prob[1] <= 1:
            prob[1] = 1 - prob[1]
        else:
            prob = [1, 0]

        if (bot.ua in self.list_uas.keys()) and (self.list_uas[bot.ua][0] > ((6-self.grade) * 100)):
            block = np.random.choice([True, False], p=prob)
            return block
        if(bot.ip in self.list_ips.keys()) and(self.list_ips[bot.proxy][0] > ((6-self.grade) * 100)):
            block = np.random.choice([True, False], p=prob)
            return block
        return False

    @staticmethod
    def generate_security_providers(nSP: int, limits: tuple):
        """
        Generate security providers
        :param nSP:
        :param limits:
        :return: Dictionary of security providers
        """
        list_security_providers = {0: None}
        for i in range(1, nSP + 1):
            grade = random.randint(limits[0], limits[1] + 1)
            list_security_providers[i] = SecurityProvider(i, grade)

        return list_security_providers

