import itertools
from .utils import get_tuple_range

class State:
    """
    Class representing states.
    One state is represented by binaries representing fingerprinting, blocking bots features.
    And two tuples of ranges of visited pages, and visited pages among one security provider.
    """

    def __init__(self, block_bots: bool, fingerprint: bool, range_visited_page: tuple, range_used_ua: tuple,
                 range_used_proxy:tuple, rate_load_pics: tuple):
        self.block_bots = block_bots
        self.fingerprint = fingerprint
        self.range_visited_pages = range_visited_page

        self.range_used_ua = range_used_ua
        self.range_used_proxy = range_used_proxy
        self.rate_load_pics = rate_load_pics

    @staticmethod
    def generate_states(tuple_ua: tuple, tuple_proxy: tuple, tuple_visited_pages):
        """
        Method generating a list of states
        :param tuple_ua: Represent amount of times this ua was used (MAX, INTERVAL)
        :param tuple_proxy: Represent amount of times this proxy was used (MAX, INTERVAL)
        :param tuple_visited_pages: Represent amount of times a website was visited (MAX, INTERVAL)
        :return: list of states
        """

        block_bot = fingerp = [True, False]
        visited_page = get_tuple_range(tuple_visited_pages[0], tuple_visited_pages[1])
        proxies = get_tuple_range(tuple_proxy[0], tuple_proxy[1])
        uas = get_tuple_range(tuple_ua[0], tuple_ua[1])

        combination = list(itertools.product(*[block_bot, fingerp, visited_page, proxies, uas]))

        return combination

    def __len__(self):
        return 6