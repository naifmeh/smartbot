import numpy as np

MAX_WEBSITE_BLOCK_VALUE = 230


def compute_blocking(value: int):

    prob = np.ones(2, dtype=float) * (value / 230)
    prob[1] = 1 - prob[0]

    return np.random.choice([True, False], p=prob)


def read_last_entry(filename: str):
    """
        Util function to push the last used item in a file to its last position. It
        pops it and save it at the end of the file.
        :param filename:
        :return: first line of file passed in parameter
    """
    with open(filename, 'r+') as f:
        first = f.readline()
        data = f.read()
        f.seek(0)
        f.write(data)
        f.write(first)
        f.truncate()

    return first.strip()


def read_file_as_list(filename: str):

    with open(filename, 'r') as f:
        lines = f.readlines()

    lines = [x.strip() for x in lines]

    return lines


def get_tuple_range(infos: tuple):
    """

    :param infos: Tuple containing (Max, step)
    :return: List of tuples of ranges
    """
    liste = []
    for i in range(0, infos[0]-infos[1] + 1, infos[1]):
        liste.append((i, i + infos[0]))

    return liste