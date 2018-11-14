import gym
import os
from .classes.Website import *
from .classes.State import *
from .classes.Proxy import *
from .classes.Bot import Bot
from .classes.UserAgent import *
import math
from .classes.Action import *
import numpy as np
from .classes.utils import read_last_entry


def initiate_bot(proxi, usera, ip):
    """
    Function to initiate the bot
    :return:
    """

    return Bot(usera, ip, 1., proxi)

def last_element(liste: list):
    tmp = liste[0]
    liste.pop(0)
    liste.append(tmp)

    return tmp

def state_of_website(states: list, website: Website):
    for state in states:
        if state.range_visited_pages[0] <= website.visit_counter <= state.range_visited_pages[1]:
            if website.use_fp == state.fingerprint and website.block_bots == state.block_bots and \
            state.has_security_attr == website.security_attribute:
                return state


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

    def __init__(self, num_steps=1000, n_sites=50, prob_fp=1 / 3, prob_bb=1 / 50):
        directory = os.path.dirname(__file__)

        self.ips = read_file_as_list(os.path.join(directory, "data/ips"))
        self.websites = Website.generate_fake_sites(n_sites, prob_fp , prob_bb, 0.4, 0.4)
        self.states_tuple, self.states_obj = State.generate_states((1000, 50))
        self.proxies = Proxy.populate_proxies()
        self.useragents = Useragent.populate_agents()
        self.actions = list(range(6))

        self.nA = len(self.actions)
        self.nStates = len(self.states_tuple)
        self.max_steps = num_steps

        self.bot = initiate_bot(Proxy.pick_new_proxy(self.proxies), last_element(self.useragents), last_element(self.ips))

        self.state = self.states_obj[0]
        self.action = (0,)
        self.observation = self.state
        self.reward = 0
        self.website = self.websites[0]
        self.bot_history = []
        self.count_success_crawls = 0

        self.nSteps = 0
        self.states_map = {x:i for i, x in enumerate(self.states_obj)}

    def step(self, action):
        """
        Perform one step into the episode. This method will map the action to the corresponding behavior
        and launch the fake bot to crawl. Actions from 0 to nA-2 will simply crawl a website.
        The two last actions will respectively change the bot's IP and the UA.
        :param action: The action to take at this time step
        :param bot:
        :return: tuple containing the next state, the reward of this time step, and a boolean done.
        """
        def normalize(value: int, maxi: int, mini: int): return (maxi - mini)*(value/180) + mini

        self.action = (action,)
        self.reward = 0
        done = False

        action_result = Actions.map_actions(self.action, self.bot, self.useragents, self.ips, self.proxies)
        self.bot = Bot(action_result[0], action_result[2], action_result[3], proxy=action_result[1])

        score, block = self.website.evaluate_bot(self.bot)
        self.bot_history.append(block)
        if block:
            self.reward = math.ceil(normalize(score, -1, -7))
        else:
            self.reward = 2

        self.website.update_bot_visit(self.bot)
        self.website.increment_visit()
        self.website = np.random.choice(self.websites)
        for website in self.websites:
            website.increment_bot_timestep()

        self.state = state_of_website(self.states_obj, self.website)
        # print(self.website)
        # print(self.state)

        self.nSteps += 1

        if self.nSteps >= self.max_steps:
            done = True

        return self.state, self.reward, done, ''


    def reset(self, n_sites=100, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):
        self.websites = Website.generate_fake_sites(n_sites, prob_fp, prob_bb, 0.4, 0.4)

        self.state = self.states_obj[0]
        self.action = (5,)
        self.observation = self.state
        self.reward = 0
        self.website = self.websites[0]
        self.bot_history = []
        self.count_success_crawls = 0

        self.nSteps = 0



    def render(self, mode='all', close=False):
        pass
