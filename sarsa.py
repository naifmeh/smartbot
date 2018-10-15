import gym
import itertools
import matplotlib
import numpy as np
import sys

if "./gym-botenv/" not in sys.path:
    sys.path.append("./gym-botenv/")

from collections import defaultdict
from gym_botenv.envs.botenv_env import BotenvEnv
from utils import plotting

env = BotenvEnv(1000)


def make_epsilon_greedy_policy(Q, epsilon, nA):

    def policy_fn(observation):
        A = np.ones(nA, dtype=float) * epsilon / nA
        best_action = np.argmax(Q[observation])
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn


def sarsa(env, num_episodes, discount_factor=1.0, alpha=0.5, epsilon=0.1):
    Q = defaultdict(lambda: np.zeros(env.nA))

    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes)
    )

    policy = make_epsilon_greedy_policy(Q, epsilon, env.nA)

    for i_episode in range(num_episodes):

        print("\rEpisode {}/{}".format(i_episode + 1, num_episodes), end="")
        sys.stdout.flush()

        state = env.reset()

        action_probs = policy(state)
        action = np.random.choice(np.arange(len(action_probs)), p=action_probs)

        for t in itertools.count():

            next_state, reward, done, _ = env.step(action)

            next_action_probs = policy(next_state)
            next_action = np.random.choice(np.arange(len(next_action_probs)), p=next_action_probs)

            stats.episode_rewards[i_episode] += reward

            # TD Update
            td_target = reward + discount_factor * Q[next_state][next_action]
            td_delta = td_target - Q[state][action]
            Q[state][action] += alpha * td_delta

            if done:
                break

            action = next_action
            state = next_state


    return Q, stats

if __name__ == '__main__':
    Q, stats = sarsa(env, 1000)
    plotting.plot_episode_stats(stats, title="Sarsa")