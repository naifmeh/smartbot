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

        directory = os.path.dirname(__file__)
        for action in actions:
            continue

