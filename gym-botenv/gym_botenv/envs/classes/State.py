import itertools
from .utils import get_tuple_range


class State:
    """
    Class representing states.
    One state is represented by binaries representing fingerprinting, blocking bots features.
    And two tuples of ranges of visited pages, and visited pages among one security provider.
    """

    def __init__(self, block_bots: bool, fingerprint: bool, security_attribute: bool, range_visited_page: tuple,
                 block_amt: tuple):
        self.block_bots = block_bots
        self.fingerprint = fingerprint
        self.has_security_attr = security_attribute
        self.range_visited_pages = range_visited_page
        self.block_amt = block_amt


    @staticmethod
    def generate_states(tuple_visited_pages: tuple):
        """
        Method generating a list of states
        :param tuple_ua: Represent amount of times this ua was used (MAX, INTERVAL)
        :param tuple_proxy: Represent amount of times this proxy was used (MAX, INTERVAL)
        :param tuple_visited_pages: Represent amount of times a website was visited (MAX, INTERVAL)
        :return: list of states
        """

        block_bot = fingerp = sec_attr = [True, False]
        blocked = get_tuple_range(100, 10)
        visited_page = get_tuple_range(tuple_visited_pages[0], tuple_visited_pages[1])
        combination = list(itertools.product(*[block_bot, fingerp, sec_attr, visited_page, blocked]))
        states = [State(x[0], x[1], x[2], x[3], x[4]) for x in combination]
        return combination, states

    def __str__(self):
        return "{'bb':%r, 'fp':%r, 'secu_attr':%r, 'range_page':(%d, %d)"%(self.block_bots,
                                                                           self.fingerprint,
                                                                           self.has_security_attr,
                                                                           self.range_visited_pages[0],
                                                                           self.range_visited_pages[1])