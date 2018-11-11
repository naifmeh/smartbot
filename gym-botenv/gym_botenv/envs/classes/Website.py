import uuid
import numpy as np
from .Bot import Bot
from .Proxy import Proxy
from .State import State


class Website:

    def __init__(self, uid: uuid, grade:int, has_fp: bool, block_bots: bool, checks_head: bool,
                 checks_referer: bool, average_visit: int):
        self.id = uid
        self.grade = grade
        #self.security_provider = secu_provider

        self.use_fp = has_fp
        self.block_bots = block_bots
        self.checks_referer = checks_referer
        self.checks_head = checks_head
        #self.check_image_rate = checks_rate
        self.average_page_visits = average_visit

        self.visit_counter = 0
        self.session_counter = []

        self.uas_visited = {} # This should contain config - [amount, time step], at some timestep we can forget
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
    
    def __len__(self):
        return 2

    def increment_bot_timestep(self):
        self.uas_visited = {x: [i[0], i[1] + 1] for x, i in self.uas_visited.items()}
        self.ips_visited = {x: [i[0], i[1] + 1] for x, i in self.ips_visited.items()}

    def _checks_ua(self, bot: Bot):
        threshold = (6-self.grade) * 25
        if bot.ua in self.uas_visited:
            if self.uas_visited[bot.ua][0] > threshold:
                return True # Introduce probability according to grade
        return False

    def _checks_proxy(self, bot: Bot):
        if bot.proxy in self.ips_visited:
            if self.ips_visited[bot.ip][0] > ((6-self.grade)*25):
                return True
        return False

    def evaluate_bot(self, bot: Bot):

        def normalize(value: int, maxi: int): return value/maxi

        def compute_blocking(prob: float): return np.random.choice([True, False],p = [prob, 1-prob])

        score = 0

        if self.checks_referer:
                score += 10
        if self.checks_head:
                score += 10
        if self.check_image_rate:
            if bot.rate_load_pics < 0.3:
                score += 20
            elif 0.3 < bot.rate_load_pics < 0.7:
                score += 5

        if self._checks_proxy(bot):
            score += 30
        if self._checks_ip(bot):
            score += 50

        # if bot.page_visits > self.average_page_visits[1]:
        #     return True, -3

        score += self.grade * 10
        val = self.session_counter * 1
        if score + val > 180:
            score = 180
        else:
             score += val

        return score, compute_blocking(normalize(score, 180))

    def __str__(self):
        return """{ 'id' : %s, 'security_provider' : %d, 'fp' : %r, 'bb' : %r, 'visited' : %d } """ \
                   % (self.id, self.security_provider, self.use_fp, self.block_bots,)

    @staticmethod
    def generate_fake_sites(n_sites: int,  prob_sp: float, prob_fp: float, prob_bb: float,
                            checks_ref: float, checks_hd: float):
        """
        Generate a list of fake websites with different attributes.

        :return: list of nSites fake websites containing a tuple of values
        """

        #secu_providers_probs = np.ones(len(security_providers), dtype=float) * (prob_sp / (len(security_providers) - 1))
        #secu_providers_probs[0] = 1 - prob_sp

        proxies, _ = Proxy.populate_proxies()

        liste_websites = []
        for i in range(n_sites):
            id = str(uuid.uuid4())

            #security_provider = np.random.choice(list(security_providers.keys()), p=secu_providers_probs)
            block_bots = np.random.choice([True, False], p=[prob_bb, 1 - prob_bb])
            fingerprinting = np.random.choice([True, False], p=[prob_fp, 1 - prob_fp])
            checks_referer = np.random.choice([True, False], p=[checks_ref, 1 - checks_ref])
            checks_head = np.random.choice([True, False], p=[checks_hd, 1 - checks_hd])
            #checks_image = np.random.choice([True, False], p=[checks_img, 1 - checks_img])

            grade = np.random.choice(list(range(1, 6)))
            page_visits = {5 - i: (x, x + 10) for i, x in enumerate(list(range(0, 50, 10)))}

            liste_websites.append(Website(id, grade, fingerprinting, block_bots, checks_head,
                                          checks_referer,  page_visits[grade]))

        return liste_websites
    
    @staticmethod
    def sort_in_states(states: list, websites: list):
        websites_copy = website.copy()
        state_dict = {}
        websites_dict = {}
        for state in states:
            state_dict[state] = ([], [], []) #Websites, uas, proxies
            for website in websites_copy:
                if website.use_fp  == state.fingerprint and website.block_bots == state.block_bots:
                    state_dict[state][0].append(website)
                    websites_dict[website] = state
                    websites_copy.pop(websites_copy.index(website))
        return state_dict, websites_dict
    
    @staticmethod
    def rearrange_website(states: dict, websites_dict: dict, website):
        state = websites_dict[website]
        states[state][0].pop(states[state][0].index(website))
        for etat in states:
            if etat.block_bots == website.block_bots and etat.fingerprint == website.use_fb:
                if  etat.range_visited_pages[0] <=website.visit_counter <= etat.range_visited_pages[1]:
                    states[etat][0] = [website] + states[etat][0]
                    website_dict[website] = etat
                    break

    @staticmethod
    def push_back_website(states_dict: dict, state: State):
        temp_website = states_dict[state][0][0]
        states_dict[state][0].pop(0)
        states_dict[state][0].append(temp_website)

        

        






