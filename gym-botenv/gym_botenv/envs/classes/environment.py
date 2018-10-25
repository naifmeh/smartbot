import uuid
import itertools
import numpy as np
import os
from .bot import Bot
from .utils import compute_blocking, read_last_entry

BOT_DETECTION_VISIT_LIMIT = 50


class SecurityProvider:

    def __init__(self, id_sp: int, grade_sp: int):
        self.id = id_sp
        self.grade = grade_sp

        self.counter_visited = 0

        self.list_ips = {}
        self.list_uas = {}

    def increment_counter(self):
        if(self.id == 0):
            print("Updated SP with value 0")
        self.counter_visited += 1

    def update_bot_visit(self, bot: Bot):

        if bot.ua in self.list_uas.keys():
            self.list_uas[bot.ua] += 1
        else:
            self.list_uas[bot.ua] = 1

        if bot.ip in self.list_ips.keys():
            self.list_ips[bot.ip] += 1
        else:
            self.list_ips[bot.ip] = 1

    def add_website(self, website):
        self.list_websites.append(website)

    def should_block_bot(self, bot: Bot):
        lowest_prob = 0.8
        highest_prob = 0.99
        lowest_grade = 1
        highest_grade = 10
        formula = lambda x: ((x-lowest_grade)*(highest_prob - lowest_prob))/(highest_grade - lowest_grade) + lowest_prob

        prob = np.ones(2, dtype=float) * formula(self.grade)
        if prob[1] <= 1:
            prob[1] = 1 - prob[1]
        else:
            prob = [1, 0]

        if (bot.ua in self.list_uas.keys()) and (self.list_uas[bot.ua] > (30-self.grade)):
            block = np.random.choice([True, False], p=prob)
            if block:
                self.list_uas[bot.ua] = 0
            return block
        if(bot.ip in self.list_ips.keys()) and(self.list_ips[bot.ip] > (30-self.grade)):
            block = np.random.choice([True, False], p=prob)
            if block:
                self.list_ips[bot.ip] = 0
            return block
        return False


class Website:

    def __init__(self, uid: uuid, secu_provider: int, has_fp: bool, block_bots: bool, checks_permissions: bool,
                 checks_plugins: bool, checks_webdriver: bool, checks_referer: bool):
        self.id = uid
        self.security_provider = secu_provider
        self.hasFingerprinting = has_fp
        self.block_bots = block_bots
        self.checks_permissions = checks_permissions
        self.checks_plugins = checks_plugins
        self.checks_webdriver = checks_webdriver
        self.checks_referer = checks_referer
        self.bots_visited = {} # This should contain config - [amount, time step], at some timestep we can forge

    def increment_visited_page(self, bot: Bot):
        self.bots_visited[bot][0] += 1

    def increment_time_step(self):
        for bot, (_, i) in self.bots_visited.items():
            if i > 300:
                self.bots_visited.pop(bot)
            else:
                self.bots_visited[bot][1] += 1

    def add_bot(self, bot: Bot):
        self.bots_visited[bot] = [1, 0]

    def should_block_bot(self, bot: Bot, dict_secu_providers: dict):
        security_provider = dict_secu_providers[self.security_provider]
        blocking = security_provider.should_block_bot(bot)
        score = 0
        if blocking:
            score += 70

        if bot in self.bots_visited.keys():
            nb_visited = self.bots_visited[bot][0]
            if nb_visited > BOT_DETECTION_VISIT_LIMIT:
                self.bots_visited.pop(bot)
                score += 50

        if self.checks_permissions:
            score += 10
        if self.checks_plugins:
            score += 10
        if self.checks_webdriver:
            score += 10
        if self.checks_referer:
            score += 30

        if bot.rate_load_pics < 1.:
            score += (1. - bot.rate_load_pics) * 50

        return compute_blocking(score)

    def __str__(self):
        return """{ 'id' : %s, 'security_provider' : %d, 'fp' : %r, 'bb' : %r, 'visited' : %d } """ \
                   % (self.id, self.security_provider, self.hasFingerprinting, self.block_bots, )


class State:
    """
    Class representing states.
    One state is represented by binaries representing fingerprinting, blocking bots features.
    And two tuples of ranges of visited pages, and visited pages among one security provider.
    """

    def __init__(self, state: tuple):
        assert len(state) >= 4
        self.ua = state[0]
        self.ip = state[1]
        self.rate_pic = state[2]

    def __str__(self):
        return """ {'ua' : %r, 'ip' : %r, 'rate_pic' : %s }""" \
               % (self.ua, self.ip, self.rate)

    def __len__(self):
        return 3


class Actions:
    """
    Class mapping actions to their behavior and various utils methods.
    """

    def __init__(self):
        pass

    @staticmethod
    def generate_actions_combination(main_actions: list):
        """
        Total amount of combinations is computable by the sum for i to N, with i starting
         at 1 (C(N,i))
        :return: list of tuples of possible combinations
        """
        list_actions = []
        for index in range(1, len(main_actions)+1):
            elements = itertools.combinations(main_actions, index)
            for element in elements:
                list_actions.append(element)

        dico_actions = {i: x for i, x in enumerate(list_actions)}
        return dico_actions

    @staticmethod
    def map_actions(actions, bot: Bot):
        ua = bot.ua
        ip = bot.ip
        rate = bot.rate_load_pics
        directory = os.path.dirname(__file__)

        for action in range(len(actions)):
            if action == 0:
                ua = read_last_entry(os.path.join(directory, "../data/uas"))
            elif action == 1:
                ip = read_last_entry(os.path.join(directory, "../data/uas"))
            elif action == 2:
                if bot.rate_load_pics > 0.9:
                    rate = 0.0
                else:
                    rate = bot.rate_load_pics + 0.1

        return ua, ip, rate


