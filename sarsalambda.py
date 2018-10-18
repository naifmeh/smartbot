import gym
import itertools
from collections import defaultdict
import numpy as np
import sys
import time
from multiprocessing.pool import ThreadPool as Pool

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


def sarsa_lambda(env, num_episodes, discount=0.9, alpha=0.01, trace_decay=0.9, epsilon=0.1, type='accumulate'):

    Q = defaultdict(lambda: np.zeros(env.nA))
    E = defaultdict(lambda: np.zeros(env.nA))

    policy = make_epsilon_greedy_policy(Q, epsilon, env.nA)

    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes)
    )

    rewards = [0.]

    for i_episode in range(num_episodes):

        print("\rEpisode {}/{}. ({})".format(i_episode+1, num_episodes, rewards[-1]), end="")
        sys.stdout.flush()

        state = env.reset()
        action_probs = policy(state)
        action = np.random.choice(np.arange(len(action_probs)), p=action_probs)

        for t in itertools.count():

            next_state, reward, done, _ = env.step(action)

            next_action_probs = policy(next_state)
            next_action = np.random.choice(np.arange(len(next_action_probs)), p=next_action_probs)

            delta = reward + discount*Q[next_state][next_action] - Q[state][action]

            stats.episode_rewards[i_episode] += reward

            E[state][action] += 1

            for s, _ in Q.items():
                Q[s][:] += alpha * delta * E[s][:]
                if type == 'accumulate':
                    E[s][:] *= trace_decay * discount
                elif type == 'replace':
                    if s == state:
                        E[s][:] = 1
                    else:
                        E[s][:] *= discount * trace_decay

            if done:
                break

            state = next_state
            action = next_action
    title = "Sarsa lambda with {} discount, {} step size, {} trace decay and {} epsilon".format(discount, alpha, trace_decay, epsilon)
    return Q, stats, title


if __name__ == '__main__':
    start = time.time()
    Q, stats, title = sarsa_lambda(env, 150)
    print(stats)
    end = time.time()
    print("Algorithm took {} to execute".format(end-start))
    plotting.plot_episode_stats(stats, title=title)








