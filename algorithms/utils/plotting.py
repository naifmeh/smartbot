import matplotlib
import numpy as np
from collections import namedtuple
from matplotlib import pyplot as plt
import pandas as pd

EpisodeStats = namedtuple("Stats", ["episode_lengths", "episode_rewards"])
BotStats = namedtuple("Bot", ["blocked", "not_blocked"])


def plot_episode_stats(stats, smoothing_window=10, noshow=False, title="None"):

    # Plot the episode reward over time
    fig = plt.figure(figsize=(10, 5))
    rewards_smoothed = pd.Series(stats.episode_rewards).rolling(smoothing_window, min_periods=smoothing_window).mean()
    plt.plot(rewards_smoothed)
    plt.xlabel("Episode")
    plt.ylabel("Episode Reward (Smoothed)")
    if title != "None":
        plt.title(title)
    else:
        plt.title("Episode Reward over Time (Smoothed over window size {})".format(smoothing_window))
    if noshow:
        plt.close(fig)
    else:
        plt.show(fig)

    return fig


def plot_bot_stats(stats, num_steps=1000, title="Bot results"):
    fig = plt.figure(figsize=(10, 5))
    data_not_blocked = pd.Series(stats.not_blocked)
    data_blocked = pd.Series(stats.blocked)
    N = range(len(data_not_blocked))
    others = [num_steps for _ in N]
    p2 = plt.bar(N, data_not_blocked, bottom=data_blocked)
    mean_blocked_data = data_blocked.rolling(10, min_periods=10).mean()
    p1 = plt.bar(N, data_blocked)
    p3 = plt.plot(mean_blocked_data, color='r')


    # plt.bar(range(len(data_not_blocked)), data_not_blocked)
    plt.xlabel("Episode")
    plt.ylabel("Amount of successful crawls")
    plt.legend((p2[0], p1[0]), ('Not blocked', 'Blocked'))
    plt.title(title)

    plt.show(fig)

    return fig



# Todo :  plot other stuffs