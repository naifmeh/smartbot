import itertools
import numpy as np
import sys

if "./gym-botenv/" not in sys.path:
    sys.path.append("./gym-botenv/")

from collections import defaultdict
from gym_botenv.envs.botenv_env import BotenvEnv
from utils import plotting

env = BotenvEnv(5000)

def make_epsilon_greedy_policy(Q, epsilon, nA):

    def policy_fn(observation):
        A = np.ones(nA, dtype=float) * epsilon / nA
        best_action = np.argmax(Q[observation])
        A[best_action] += (1.0 - epsilon)
        return A
    return policy_fn


def nstep_sarsa(env, num_episodes, discount_factor=0.7, alpha=0.5, epsilon=0.1, n=10):

    Q = defaultdict(lambda: np.zeros(env.nA))



    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes)
    )

    policy = make_epsilon_greedy_policy(Q, epsilon, env.nA)
    list_returns = [0]

    for i_episode in range(num_episodes):

        print("\rEpisode {}/{}. Sum returns {}".format(i_episode + 1, num_episodes, list_returns[-1]), end="")
        sys.stdout.flush()

        state = env.reset()

        rewards = [0]
        states = [state]

        action_probs = policy(state)
        action = np.random.choice(np.arange(len(action_probs)), p=action_probs)

        actions = [action]
        n_steps = 10000000
        for t in itertools.count():

            if t < n_steps:
                next_state, reward, done, _ = env.step(action)

                states.append(next_state)
                rewards.append(reward)
                stats.episode_rewards[i_episode] += reward

                if done:
                    n_steps = t+1
                else:
                    next_action_probs = policy(state)
                    next_action = np.random.choice(np.arange(len(next_action_probs)), p=next_action_probs)
                    actions.append(next_action)
            pi = t - n + 1

            if pi >= 0:
                returns = 0.

                for x in range(pi+1, min(pi+n, n_steps) +1):
                    returns += pow(discount_factor, x-pi-1) * rewards[x]

                if pi + n < n_steps:
                    returns += (discount_factor**n) * Q[states[pi+n]][actions[pi+n]]

                Q[states[pi]][actions[pi]] += alpha * (returns - Q[states[pi]][actions[pi]])


                list_returns.append(returns)


            if pi == n_steps - 1:
                break

            state = next_state
            action = next_action

    return Q, stats

if __name__ == '__main__':
    Q, stats = nstep_sarsa(env, 500)
    plotting.plot_episode_stats(stats)