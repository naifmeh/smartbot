import gym
import numpy as np
import uuid
import itertools
import random
import operator
import os
from .classes.environment import Website, State, SecurityProvider, Actions
from .classes.environment import read_last_entry as read_line
from .classes.bot import Bot


def generate_security_providers(nSP: int, limits: tuple):
    """
    """
    list_security_providers = {0: None}
    for i in range(1, nSP+1):
        grade = random.randint(limits[0], limits[1] + 1)
        list_security_providers[i] = SecurityProvider(i, grade)

    return list_security_providers

def generate_fake_sites(nSites: int, security_providers: dict, probSP: float, probFP: float, probBB: float):
    """

    :param nSites: Amount of fake websites generated
    :param nSP: Amount of security providers
    :param probSP: Probability that a website has a security provider
    :param probFP: Probability that a website has browser fingerprinting capabilities
    :param probBB: Probability that a website block bots
    :return: list of nSites fake websites containing a tuple of values
    """
    nSP = len(security_providers)
    probsSP = np.ones(nSP, dtype=float) * probSP / (nSP - 1)
    probsSP[0] = 1 - probSP

    probsFP = np.ones(2, dtype=float) * probFP
    probsFP[1] = 1 - probFP

    probsBB = np.ones(2, dtype=float) * probBB
    probsBB[1] = 1 - probBB

    list_website = []
    for i in range(nSites):
        id = str(uuid.uuid4())
        SP = np.random.choice(list(security_providers.keys()), p=probsSP)
        FP = np.random.choice([0, 1], p=probsFP)  # 0 : doesnt use fp, 1:use fp
        BB = np.random.choice([0, 1], p=probsBB)  # 0: doesnt block bots, 1 block bots
        num_page_visit = 0
        website_obj = Website(id, SP, FP, BB, num_page_visit)
        list_website.append(website_obj)

    return list_website


def generate_states(num_binary_params: int, params_pages: tuple, params_secu_provider: tuple):
    """

    :param list_website: List of website's
    :param num_binary_params: Amount of binary features
    :param params_pages: Tuple containing (max, step)
    :param params_secu_provider: Tuple containing (max, step)
    :return: A tuple of states
    """

    max_visited_page = params_pages[0]
    range_visited_page = params_pages[1]
    list_range_visited_page = []
    for i in range(0, max_visited_page, range_visited_page):
        list_range_visited_page.append((i, i + range_visited_page - 1))

    max_security_provider = params_secu_provider[0]
    range_page_secu_provider = params_secu_provider[1]
    list_range_page_secu_provider = []
    for i in range(0, max_security_provider, range_page_secu_provider):
        list_range_page_secu_provider.append((i, i + range_page_secu_provider - 1))

    list_states_features = []
    for i in range(num_binary_params):
        list_states_features.append(list(range(2)))

    list_states_features.append(list_range_visited_page)
    list_states_features.append(list_range_page_secu_provider)

    states_tuple = list(itertools.product(*list_states_features))
    random.shuffle(states_tuple)
    states = []
    for state in states_tuple:
        states.append(State(state))

    return states


def generate_actions(list_states: list):
    """

    :param list_states:
    :return:
    """
    dict_actions = {}
    len_states = len(list_states)
    for i in range(len_states + 2):
        if i >= len_states:
            dict_actions[i] = ()
            continue
        dict_actions[i] = list_states[i]

    return dict_actions


def normalized_websites_values(list_website: list, security_providers: dict):
    values = {}
    for website in list_website:
        website.compute_value(security_providers)
        values[website.id] = website.value

    maximum = max(values.items(), key=operator.itemgetter(1))[1]
    minimum = min(values.items(), key=operator.itemgetter(1))[1]

    for id, value in values.items():
        values[id] = float(float(value - minimum) / float(maximum - minimum))

    return values


def is_bot_blocked(website: Website, values_dict: dict):
    probs = np.ones(2, dtype=float) * values_dict[website.id]
    probs[0] = 1 - probs[1]

    return int(np.random.choice([0, 1], p=probs))


def websites_to_state(list_websites: list, list_states: list, security_providers: dict):
    state_map = {}
    copy_list_website = list_websites.copy()
    for state in list_states:
        state_map[state] = []
        for index, website in enumerate(copy_list_website):
            if state.useFP != website.hasFingerprinting:
                continue
            elif state.useBB != website.blockbots:
                continue
            elif website.amount_page_visited not in range(state.rangeVisitedPage[0], state.rangeVisitedPage[1] + 1):
                continue
            else:
                security_provider = website.security_provider
                if security_provider == 0:
                    state_map[state].append(website)
                    copy_list_website.pop(index)
                else:
                    if security_providers[security_provider].counter_visited in range(state.rangeVisitedSecuProvider[0],
                                                                                      state.rangeVisitedSecuProvider[
                                                                                          1] + 1):
                        state_map[state].append(website)
                        copy_list_website.pop(index)

    return state_map


def upgrade_state_list(website, state, state_map: dict, security_providers: dict):
    state_map[state].pop(state_map[state].index(website))
    for state, _ in state_map.items():
        if state.useFP != website.hasFingerprinting:
            continue
        elif state.useBB != website.blockbots:
            continue
        elif website.amount_page_visited not in range(state.rangeVisitedPage[0], state.rangeVisitedPage[1] + 1):
            continue
        else:
            security_provider = website.security_provider
            if security_provider == 0:
                state_map[state].append(website)
                break
            else:
                if security_providers[security_provider].counter_visited in range(state.rangeVisitedSecuProvider[0],
                                                                                  state.rangeVisitedSecuProvider[
                                                                                      1] + 1):
                    state_map[state].append(website)
                    break


def initiate_bot():
    """
    Function to initiate the bot
    :return:
    """
    directory = os.path.dirname(__file__)
    ip = read_line(os.path.join(directory, "data/ips"))
    ua = read_line(os.path.join(directory, "data/uas"))

    return Bot(ip, ua)


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

    def __init__(self, num_steps, n_sites=1000, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):

        self.security_providers = generate_security_providers(nSP, (0, 10))
        self.sites = generate_fake_sites(n_sites, self.security_providers, prob_sp, prob_fp, prob_bb)
        self.states = generate_states(2, (100, 10), (1000, 50))
        self.actions = generate_actions(self.states)  # dict map action - state
        self.max_steps = num_steps
        self.bot = initiate_bot()

        self.state = self.states[0]
        self.action = 0
        self.observation = self.state
        self.reward = 0
        self.website = 0

        self.nA = len(self.actions)
        self.nStates = len(self.states)
        self.nSteps = 0

        self.states_map = websites_to_state(self.sites, self.states, self.security_providers)

    def step(self, action):
        """
        Perform one step into the episode. This method will map the action to the corresponding behavior
        and launch the fake bot to crawl. Actions from 0 to nA-2 will simply crawl a website.
        The two last actions will respectively change the bot's IP and the UA.
        :param action: The action to take at this time step
        :param bot:
        :return: tuple containing the next state, the reward of this time step, and a boolean done.
        """
        self.action = action
        action_bundle = Actions(self.actions)

        reward = 0
        done = False
        # TODO: Make actions, launch bot, wait for return signal and return state, reward, done or no
        action_result = action_bundle.map_actions(action, self.bot)
        self.bot.ua = action_result[1]
        self.bot.ip = action_result[2]
        self.state = action_result[0] if len(action_result[0]) > 1 else self.state

        reward = self._fake_crawl(self.state, self.bot)
        self.nSteps += 1

        self.reward = reward
        if self.nSteps == self.max_steps:
            done = True

        return self.state, reward, done, ''

    def _fake_crawl(self, state: State, bot: Bot):
        """
        This private method will fake crawl a website corresponding to a state. The bot will get blocked by
        a security provider if it's powerful (i.e a high grade) and if an IP or an UA has visited the
        security provider too many times.
        :param state: the actual state
        :param bot: the bot
        :return: the reward (0 for not blocked)
        """
        if len(self.states_map[state]) < 1:
            self.website = 0
            return -0.1
        website = self.states_map[state][0]
        website.amount_page_visited += 1
        self.website = website

        upgrade_state_list(website, state, self.states_map, self.security_providers)

        if website.security_provider > 0:
            secu_provider = self.security_providers[website.security_provider]
            secu_provider.increment_counter()
            secu_provider.update_bot_visit(bot)
            self.security_providers[website.security_provider] = secu_provider
            block_bot = secu_provider.should_block_bot(bot)
            if block_bot:
                return -10

        values = normalized_websites_values(self.sites, self.security_providers)
        block_bot = is_bot_blocked(website, values)
        if block_bot:
            return -5

        return 5

    def get_state_map(self):
        return { x:i for i, x in enumerate(self.states)}

    def reset(self, n_sites=1000, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):
        self.security_providers = generate_security_providers(nSP, (1, 10))
        self.sites = generate_fake_sites(n_sites, self.security_providers, prob_sp, prob_fp, prob_bb)
        self.bot = initiate_bot()

        self.state = self.states[0]
        self.action = 0
        self.observation = self.state
        self.reward = 0
        self.website = 0

        self.nSteps = 0

        self.states_map = websites_to_state(self.sites, self.states, self.security_providers)

        return self.state

    def render(self, mode='all', close=False):
        if mode == 'blocked' and self.reward >= 0:
            return
        print("------------- Step {}".format(self.nSteps))
        print("State : {}".format(self.state))
        print("Action taken at step t-1 : {}".format(self.action))
        print("Website visited : {}".format(self.website))
        print("Reward for step t : {}".format(self.reward), end='\n\n')
