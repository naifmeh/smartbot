import uuid
import itertools
import numpy as np
import os
from .bot import Bot
from .utils import compute_blocking, read_last_entry

BOT_DETECTION_VISIT_LIMIT = 1


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

        if (bot.ua in self.list_uas.keys()) and (self.list_uas[bot.ua] > (15-self.grade)):
            block = np.random.choice([True, False], p=prob)
            if block:
                self.list_uas[bot.ua] = 0
            return block
        if(bot.ip in self.list_ips.keys()) and(self.list_ips[bot.ip] > (15-self.grade)):
            block = np.random.choice([True, False], p=prob)
            if block:
                self.list_ips[bot.ip] = 0
            return block
        return False


class Website:

    def __init__(self, uid: uuid, grade:int, secu_provider: int, has_fp: bool, block_bots: bool, checks_head: bool,
                 checks_referer: bool, checks_rate: bool, average_visit: int):
        self.id = uid
        self.grade = grade
        self.security_provider = secu_provider
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
        self.uas_visited = {x: [i[0], i[1]+1] for x, i in self.uas_visited.items() if i[1] < 100}
        self.ips_visited = {x: [i[0], i[1] + 1] for x, i in self.ips_visited.items() if i[1] < 100}

    def _checks_ua(self, bot: Bot):
        threshold = (6-self.grade) * 25
        if bot.ua in self.uas_visited:
            if self.uas_visited[bot.ua][0] > threshold:
                return True # Introduce probability according to grade
        return False

    def _checks_ip(self, bot: Bot):
        if bot.ip in self.ips_visited:
            if self.ips_visited[bot.ip][0] > ((6-self.grade)*25):
                return True
        return False

    def evaluate_bot(self, bot: Bot):

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


class State:
    """
    Class representing states.
    One state is represented by binaries representing fingerprinting, blocking bots features.
    And two tuples of ranges of visited pages, and visited pages among one security provider.
    """

    def __init__(self, state: tuple):
        assert len(state) >= 3
        self.ua = state[0]
        self.ip = state[1]
        self.rate_pic = state[2]

    def __str__(self):
        return """ {'ua' : %r, 'ip' : %r, 'rate_pic' : %s }""" \
               % (self.ua, self.ip, self.rate_pic)

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
    def map_actions(actions, bot: Bot, websites: list):
        ua = bot.ua
        ip = bot.ip
        rate = bot.rate_load_pics
        referer = bot.referer
        head = bot.head
        document = bot.documents
        website = websites[0]
        page_visits = bot.page_visits

        directory = os.path.dirname(__file__)

        for action in actions:
            if action == 0:
                ua = read_last_entry(os.path.join(directory, "../data/uas"))
            elif action == 1:
                ip = read_last_entry(os.path.join(directory, "../data/ips"))
            elif action == 2:
                if bot.rate_load_pics > 0.9:
                    rate = 0.0
                else:
                    rate = bot.rate_load_pics + 0.1
            elif action == 3:
                referer = not referer
            elif action == 4:
                head = not head
            elif action == 5:
                document = not document
            elif action == 6:
                websites.pop(0)
                website.update_bot_visit(bot)
                website.increment_bot_timestep()
                websites.append(website)
            elif action >= 7:
                liste = [(x, x+9) for x in range(0, 50, 10)]
                action_sec = 11 - action
                page_visits = np.random.choice(liste[action_sec])


        return ua, ip, round(rate, 1), referer, head, document, website, page_visits


