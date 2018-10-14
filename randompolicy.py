import gym
import itertools
import numpy as np
import sys

if "./gym-botenv/" not in sys.path:
    sys.path.append("./gym-botenv/")

from gym_botenv.envs.botenv_env import BotenvEnv
from utils import plotting


if __name__ == '__main__':

    botenv = BotenvEnv(1000)
    actions = [x for x in range(len(botenv.actions))]

    num_episodes = 500

    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes)
    )


    for i_episode in range(num_episodes):
        botenv.reset()
        print("\rEpisode {}/{}.".format(i_episode, num_episodes), end="")
        sys.stdout.flush()

        for t in itertools.count():
            action = np.random.choice(actions)
            next_step, reward, done, _ = botenv.step(action)

            stats.episode_rewards[i_episode] += reward
            stats.episode_lengths[i_episode] = t

            if done:
                break



    plotting.plot_episode_stats(stats)