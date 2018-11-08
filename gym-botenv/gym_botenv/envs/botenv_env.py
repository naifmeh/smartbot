import gym
import random
import os
from .classes.Website import Website, State, SecurityProvider, Actions
from .classes.Website import read_last_entry as read_line
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



def initiate_bot():
    """
    Function to initiate the bot
    :return:
    """
    directory = os.path.dirname(__file__)
    ip = read_line(os.path.join(directory, "data/ips"))
    ua = read_line(os.path.join(directory, "data/uas"))

    return Bot(ip, ua, (0, 10), False, True, True)


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

    def _fake_crawl(self,  bot: Bot):
        """
        This private method will fake crawl a website corresponding to a state. The bot will get blocked by
        a security provider if it's powerful (i.e a high grade) and if an IP or an UA has visited the
        security provider too many times.
        :param state: the actual state
        :param bot: the bot
        :return: the reward (0 for not blocked)
        """
        pass


    def reset(self, n_sites=100, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):
        pass

    def render(self, mode='all', close=False):
        pass
