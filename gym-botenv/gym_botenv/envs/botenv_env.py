import gym
import numpy as np
import uuid
import itertools
import random
import operator
import os
from .classes.environment import Website, State, SecurityProvider, Actions
from .classes.environment import read_last_entry as read_line
from .classes.utils import read_file_as_list
from .classes.bot import Bot


def generate_security_providers(nSP: int, limits: tuple):
    """
    """
    list_security_providers = {0: None}
    for i in range(1, nSP+1):
        grade = random.randint(limits[0], limits[1] + 1)
        list_security_providers[i] = SecurityProvider(i, grade)

    return list_security_providers


def generate_fake_sites(n_sites: int, security_providers: dict, prob_sp: float, prob_fp: float, prob_bb: float,
                        checks_ref: float, checks_hd: float, checks_img: float):
    """
    Generate a list of fake websites with different attributes.

    :return: list of nSites fake websites containing a tuple of values
    """

    secu_providers_probs = np.ones(len(security_providers), dtype=float) * (prob_sp/(len(security_providers)-1))
    secu_providers_probs[0] = 1 - prob_sp

    liste_websites = []
    for i in range(n_sites):
        id = str(uuid.uuid4())

        security_provider = np.random.choice(list(security_providers.keys()), p=secu_providers_probs)
        block_bots = np.random.choice([True, False], p=[prob_bb, 1-prob_bb])
        fingerprinting = np.random.choice([True, False], p=[prob_fp, 1-prob_fp])
        checks_referer = np.random.choice([True, False], p=[checks_ref, 1-checks_ref])
        checks_head = np.random.choice([True, False], p=[checks_hd, 1-checks_hd])
        checks_image = np.random.choice([True, False], p=[checks_img, 1-checks_img])
        grade = np.random.choice(list(range(1, 6)))
        page_visits = { 5-i: (x, x+10) for i, x in enumerate(list(range(0, 50, 10)))}

        liste_websites.append(Website(id, grade, security_provider, fingerprinting, block_bots, checks_head,
                                      checks_referer, checks_image, page_visits[grade] ))

    return liste_websites


def generate_states():
    """

    :param list_website: List of website's
    :param num_binary_params: Amount of binary features
    :param params_pages: Tuple containing (max, step)
    :param params_secu_provider: Tuple containing (max, step)
    :return: A tuple of states
    """

    list_load_pics = [x for x in range(0, 11)]
    list_load_pics = np.divide(list_load_pics, 10)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    uas = read_file_as_list(os.path.join(current_dir, 'data/uas'))
    ips = read_file_as_list(os.path.join(current_dir, 'data/ips'))

    referer = head = [True, False] # TODO: Include them

    combination = list(itertools.product(*[uas, ips, list(list_load_pics), referer, head]))
    states = []
    for state in combination:
        states.append(state)

    del combination
    return states


def initiate_bot():
    """
    Function to initiate the bot
    :return:
    """
    directory = os.path.dirname(__file__)
    ip = read_line(os.path.join(directory, "data/ips"))
    ua = read_line(os.path.join(directory, "data/uas"))

    return Bot(ip, ua, (0, 10), False, True, True)

def normalize_values(minx, maxx, a, b,  value):
    return (b - a)*((value - minx)/(maxx - minx)) + a


class BotenvEnv(gym.Env):
    """ Simple bot environment

    Botenv is a fake environment allowing to mimic a website's defenses against bots.

    On it's first versions, Botenv should allow to mimic wether the website has or no
    fingerprinting capabilities, if it does or do not block bots, etc...

    The observation is the website current configuration and if it has blocked the bot or no. The action is selected among
    an action space containing IP change, UA change, and the feature we want to jump in.

    The reward function depend on under which configuration the bot got blocked. For instance,
    if the security provider is extremely good at it's job, the negative reward should have less impact than
    if the bot got blocked because of a bad security provider.

    """

    def __init__(self, num_steps=1000, n_sites=100, nSP=10, prob_sp=1 / 10, prob_fp=1 / 3, prob_bb=1 / 50):
        self.security_providers = generate_security_providers(nSP, (0, 10))
        self.websites = generate_fake_sites(n_sites, self.security_providers,
                                            prob_sp, prob_fp, prob_bb, 0.6, 0.6, 0.7)
        self.actions = list(range(13))
        #self.actions_list = Actions.generate_actions_combination(list(range(13)))
        #self.actions = list(range(len(self.actions_list)))
        self.nA = len(self.actions)
        self.states = generate_states()
        self.max_steps = num_steps

        self.bot = initiate_bot()

        self.state = self.states[0]
        self.action = 6
        self.observation = self.state
        self.reward = 0
        self.website = self.websites[0]
        self.bot_history = []
        self.action_history = []
        self.count_success_crawls = 0

        self.nStates = len(self.states)
        self.nSteps = 0
        self.state_map = {x: x for x in self.states}
        self.states_map = {x: i for i, x in enumerate(self.states)}
        pass

    def step(self, action):
        """
        Perform one step into the episode. This method will map the action to the corresponding behavior
        and launch the fake bot to crawl. Actions from 0 to nA-2 will simply crawl a website.
        The two last actions will respectively change the bot's IP and the UA.
        :param action: The action to take at this time step
        :param bot:
        :return: tuple containing the next state, the reward of this time step, and a boolean done.
        """
        self.action = (action,)
        #self.action = self.actions_list[action]
        self.reward = 0
        done = False

        action_result = Actions.map_actions(self.action, self.bot, self.websites)
        self.bot.ua = action_result[0]
        self.bot.ip = action_result[1]
        self.bot.rate_load_pics = action_result[2]
        self.bot.referer = action_result[3]
        self.bot.head = action_result[4]
        self.bot.documents = action_result[5]
        self.bot.page_visits = action_result[7]
        self.website = action_result[6]

        self.state = self.state_map[action_result[:5]]

        self.reward = self._fake_crawl(self.bot)
        self.nSteps += 1

        if self.nSteps == self.max_steps:
            done = True

        return self.state, self.reward, done, ''

    def _fake_crawl(self,  bot: Bot):
        """
        This private method will fake crawl a website corresponding to a state. The bot will get blocked by
        a security provider if it's powerful (i.e a high grade) and if an IP or an UA has visited the
        security provider too many times.
        :param state: the actual state
        :param bot: the bot
        :return: the reward (0 for not blocked)
        """
        if self.website.security_provider > 0:
            secu_provider = self.security_providers[self.website.security_provider]
            secu_provider.update_bot_visit(bot)
            secu_provider.increment_timestep()
            self.security_providers[self.website.security_provider] = secu_provider

        should_block, reward = self.website.evaluate_bot(bot, self.security_providers)


        self.bot_history.append(should_block)
        if not should_block:
            self.count_success_crawls += 1

        if self.nSteps == self.max_steps:
            if self.count_success_crawls > 0.8 * len(self.websites):
                reward += 1

        return reward


    def reset(self, n_sites=100, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):

        # self.security_providers = generate_security_providers(nSP, (0, 10))
        self.websites = generate_fake_sites(n_sites, self.security_providers,
                                            prob_sp, prob_fp, prob_bb, 0.6, 0.6, 0.7)

        self.state = self.states[0]
        self.action = 0
        self.observation = self.state
        self.reward = 0
        self.count_success_crawls = 0
        self.bot_history = []

        self.nSteps = 0

        return self.state

    def render(self, mode='all', close=False):
        pass
