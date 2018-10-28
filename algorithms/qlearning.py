import itertools
import numpy as np
import sys

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, os.path.join(parentdir, "gym-botenv"))

from collections import defaultdict
from gym_botenv.envs.botenv_env import BotenvEnv
from algorithms.utils import plotting

env = BotenvEnv(3000)


def make_epsilon_greedy_policy(Q, epsilon, nA):

    def policy_fn(observation):
        A = np.ones(nA, dtype=float) * epsilon / nA
        best_action = np.argmax(Q[observation])
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn


def q_learning(env, num_episodes, discount_factor=1.0, alpha=0.5, epsilon=0.1):

    Q = defaultdict(lambda: np.zeros(env.nA))

    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes)
    )

    botstats = plotting.BotStats(
        blocked=np.zeros(num_episodes),
        not_blocked=np.zeros(num_episodes)
    )


    policy = make_epsilon_greedy_policy(Q, epsilon, env.nA)

    for i_episode in range(num_episodes):

        state = env.reset()

        for t in itertools.count():

            action_probs = policy(state)
            action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
            next_state, reward, done, _ = env.step(action)
            #env.render()

            stats.episode_rewards[i_episode] += reward
            stats.episode_lengths[i_episode] = t

            if env.bot_history[-1]:
                botstats.blocked[i_episode] += 1
            else:
                botstats.not_blocked[i_episode] += 1

            # TD update
            best_next_action = np.argmax(Q[next_state])
            td_target = reward + discount_factor * Q[next_state][best_next_action]
            td_delta = td_target - Q[state][action]
            Q[state][action] += alpha * td_delta

            if done:
                break

            state = next_state

            print("\rEpisode {}/{}. ({})".format(i_episode + 1, num_episodes, reward), end="")
            sys.stdout.flush()

    return Q, stats, botstats


if __name__ == '__main__':
    Q, stats, botstats = q_learning(env, 1000)
    plotting.plot_episode_stats(stats, title="QLearning")
    plotting.plot_bot_stats(botstats)



