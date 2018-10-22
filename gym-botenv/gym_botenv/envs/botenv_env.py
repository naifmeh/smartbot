import gym
import numpy as np
import uuid
import itertools
import random
import operator
import os
from .classes.environment import Website, State, SecurityProvider, Actions
from .classes.environment import read_last_entry as read_line
from .classes.utils import read_file_in_list
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
                        checks_perms: float, checks_plugs: float, checks_webdrvr: bool, checks_ref: bool):
    """
    Generate a list of fake websites with different attributes.

    :return: list of nSites fake websites containing a tuple of values
    """

    secu_providers_probs = np.ones(len(security_providers), dtype=float) * (prob_sp/len(security_providers))
    security_providers[0] = 1 - prob_sp

    liste_websites = []
    for i in range(n_sites):
        id = str(uuid.uuid4())
        security_provider = np.random.choice(security_providers.keys(), p=secu_providers_probs)
        block_bots = np.random.choice([True, False], p=[prob_bb, 1-prob_bb])
        fingerprinting = np.random.choice([True, False], p=[prob_fp, 1-prob_fp])
        checks_permissions = np.random.choice([True, False], p=[checks_perms, 1-checks_perms])
        checks_plugins = np.random.choice([True, False], p=[checks_plugs, 1-checks_plugs])
        checks_webdriver = np.random.choice([True, False], p=[checks_webdrvr, 1-checks_webdrvr])
        checks_referer = np.random.choice([True, False], p=[checks_ref, 1-checks_ref])

        liste_websites.append(Website(id, security_provider, fingerprinting, block_bots, checks_permissions,
                                      checks_plugins, checks_webdriver, checks_referer))

    return liste_websites




def generate_states(num_binary_params: int,  params_secu_provider: tuple):
    """

    :param list_website: List of website's
    :param num_binary_params: Amount of binary features
    :param params_pages: Tuple containing (max, step)
    :param params_secu_provider: Tuple containing (max, step)
    :return: A tuple of states
    """

    list_load_pics = [x for x in range(0, 11)]
    list_load_pics = np.divide(list_load_pics, 10)

    uas = read_file_in_list('./data/uas')
    ips = read_file_in_list('./data/ips')

    # TODO complete states generation






def is_bot_blocked(website: Website, values_dict: dict):
    probs = np.ones(2, dtype=float) * values_dict[website.id]
    probs[0] = 1 - probs[1]

    return int(np.random.choice([0, 1], p=probs))






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
        pass

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

    def reset(self, n_sites=1000, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):
        pass

    def render(self, mode='all', close=False):
        pass
