import gym
import os
from .classes.Website import *
from .classes.State import *
from .classes.Proxy import *
from .classes.Bot import Bot


def initiate_bot():
    """
    Function to initiate the bot
    :return:
    """
    directory = os.path.dirname(__file__)

    proxy = Proxy.populate_proxies()[0]
    ua = read_last_entry(os.path.join(directory, "data/uas"))

    return Bot(proxy, ua, (0, 10), False, True, True)


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
        self.websites = Website.generate_fake_sites(n_sites, prob_sp, prob_fb, prob_bb, 0.4, 0.4 )
        self.states_tuple, self.states_obj = States.generate_states((1000, 100), (1000, 100), (1000, 50))
        self.proxies = Proxy.populate_proxies()
        self.useragents = Useragent.populate_agents()
        self.actions = list(range(4))

        self.nA = len(self.actions)
        self.nStates = len(self.states_tuple)
        self.max_steps = num_steps

        self.bot = initiate_bot()

        self.state = self.states_tuple[0]
        self.action = (0,)
        self.observation = self.state
        self.reward = 0
        self.website = self.websites[0]
        self.bot_history = []
        self.action_history = []
        self.count_success_crawls = 0

        self.nSteps = 0
        self.states_dict, self.websites_dict = Website.sort_in_states(self.states_obj, self.websites)
        self.proxies_dict =  Proxy.sort_in_states(self.states_dict, self.proxies)
        self.uas_dict = Useragent.sort_in_states(self.states_dict, self.useragents)

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
        self.reward = 0
        done = False

        action_result = Actions.map_actions(self.action, self.bot, self.state, self.states_dict)
        self.bot.ua = action_result[0]
        self.bot.ua.increment_counter()
        self.bot.proxy = action_result[1]
        self.bot.proxy.increment_counter()
        self.website = action_result[2]
        if len(self.website) < 2:
            self.reward = -0.5
        else:
            self.reward = self._fake_crawl(self.bot)

        self.website.update_bot_visit(self.bot)
        self.website.increment_bot_timestep()
        Website.rearrange_website(self.states_dict, self.websites_dict, self.website)
        Useragent.rearrange_ua(self.states_dict, self.uas_dict, self.bot.ua)
        Proxy.rearrange_proxy(self.states_dict, self.proxies_dict, self.bot.proxy)

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

        def normalize(value: int, maxi: int, mini: int): return ((value)/(180))*(maxi-mini) + mini

        score, shoud_block = self.website.evaluate_bot(bot)
        if should_block:
            reward = normalize(value, -1, -5)
        else:
            reward = 5
        
        return reward


    def reset(self, n_sites=100, nSP=10, prob_sp=1 / 10, prob_fp=1 / 4, prob_bb=1 / 50):
        self.websites = Website.generate_fake_sites(n_sites, prob_sp, prob_fb, prob_bb, 0.4, 0.4 )
        self.proxies = Proxy.populate_proxies()
        self.useragents = Useragent.populate_agents()
        self.actions = list(range(4))


        self.bot = initiate_bot()

        self.state = self.states_tuple[0]
        self.action = (0,)
        self.observation = self.state
        self.reward = 0
        self.website = self.websites[0]
        self.bot_history = []
        self.count_success_crawls = 0

        self.nSteps = 0
        self.states_dict, self.websites_dict = Website.sort_in_states(self.states_obj, self.websites)
        self.proxies_dict =  Proxy.sort_in_states(self.states_dict, self.proxies)
        self.uas_dict = Useragent.sort_in_states(self.states_dict, self.useragents)

    def render(self, mode='all', close=False):
        pass
