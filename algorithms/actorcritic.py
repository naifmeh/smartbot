import itertools
import numpy as np
import sys
import tensorflow as tf
import collections

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, os.path.join(parentdir, "gym-botenv"))

from gym_botenv.envs.botenv_env import BotenvEnv
from algorithms.utils import plotting

env = BotenvEnv(1000)

class PolicyEstimator():

    def __init__(self, learning_rate=0.01, scope="policy_estimator"):
        with tf.variable_scope(scope):
            self.state = tf.placeholder(tf.int32, [], "state")
            self.action = tf.placeholder(dtype=tf.int32, name="action")
            self.target = tf.placeholder(dtype=tf.float32, name="target")

            state_one_hot = tf.one_hot(self.state, env.nStates)
            self.output_layer = tf.contrib.layers.fully_connected(
                inputs=tf.expand_dims(state_one_hot, 0),
                num_outputs=env.nA,
                activation_fn=None,
                weights_initializer=tf.zeros_initializer
            )

            self.action_probs = tf.squeeze(tf.nn.softmax(self.output_layer))
            self.picked_action_prob = tf.gather(self.action_probs, self.action)

            self.loss = -tf.log(self.picked_action_prob) * self.target

            self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            self.train_op = self.optimizer.minimize(
                self.loss, global_step=tf.contrib.framework.get_global_step())

    def predict(self, state, sess=None):
         sess = sess or tf.get_default_session()
         return sess.run(self.action_probs, {self.state: state})

    def update(self, state, target, action, sess=None):
         sess = sess or tf.get_default_session()
         feed_dict = { self.state: state, self.target: target, self.action: action}
         _, loss = sess.run([self.train_op, self.loss], feed_dict)
         return loss


class ValueEstimator():
    """
    Value Function approximator.
    """

    def __init__(self, learning_rate=0.1, scope="value_estimator"):
        with tf.variable_scope(scope):
            self.state = tf.placeholder(tf.int32, [], "state")
            self.target = tf.placeholder(dtype=tf.float32, name="target")

            # This is just table lookup estimator
            state_one_hot = tf.one_hot(self.state, int(env.nStates))
            self.output_layer = tf.contrib.layers.fully_connected(
                inputs=tf.expand_dims(state_one_hot, 0),
                num_outputs=1,
                activation_fn=None,
                weights_initializer=tf.zeros_initializer)

            self.value_estimate = tf.squeeze(self.output_layer)
            self.loss = tf.squared_difference(self.value_estimate, self.target)

            self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            self.train_op = self.optimizer.minimize(
                self.loss, global_step=tf.contrib.framework.get_global_step())

    def predict(self, state, sess=None):
        sess = sess or tf.get_default_session()
        return sess.run(self.value_estimate, {self.state: state})

    def update(self, state, target, sess=None):
        sess = sess or tf.get_default_session()
        feed_dict = {self.state: state, self.target: target}
        _, loss = sess.run([self.train_op, self.loss], feed_dict)
        return loss


def actor_critic(env, estimator_policy, estimator_value, num_episodes, discount_factor=1.0):

    stats = plotting.EpisodeStats(
        episode_rewards=np.zeros(num_episodes),
        episode_lengths=np.zeros(num_episodes)
    )
    botstats = plotting.BotStats(
        blocked=np.zeros(num_episodes),
        not_blocked=np.zeros(num_episodes)
    )

    Transition = collections.namedtuple("Transition", ["state", "action", "reward", "next_state", "done"])
    states_map = env.states_map

    for i_episode in range(num_episodes):

        state = env.reset()

        episode = []

        for t in itertools.count():

            action_probs = estimator_policy.predict(states_map[state])
            action = np.random.choice(np.arange(len(action_probs)), p=action_probs)
            next_state, reward, done, _ = env.step(action)
            #env.render(mode='blocked')

            episode.append(Transition(
                state=state, action=action, reward=reward, next_state=next_state, done=done
            ))

            # Update statistics
            stats.episode_rewards[i_episode] += reward
            stats.episode_lengths[i_episode] = t
            if reward <= -1:
                botstats.blocked[i_episode] += 1
            elif reward >= 1:
                botstats.not_blocked[i_episode] += 1

            # Calculate TD Target
            value_next = estimator_value.predict(states_map[next_state])
            td_target = reward + discount_factor * value_next
            td_error = td_target - estimator_value.predict(states_map[state])

            # Update the value estimator
            estimator_value.update(states_map[state], td_target)

            # Update the policy estimator
            # using the td error as our advantage estimate
            estimator_policy.update(states_map[state], td_error, action)

            # Print out which step we're on, useful for debugging.
            print("\rStep {} @ Episode {}/{} ({}).".format(
                t, i_episode + 1, num_episodes, stats.episode_rewards[i_episode - 1]), end="")
            sys.stdout.flush()

            if done:
                break

            state = next_state

    return stats, botstats


if __name__== '__main__':

    tf.reset_default_graph()

    global_step = tf.Variable(0, name="global_step", trainable=False)
    policy_estimator = PolicyEstimator()
    value_estimator = ValueEstimator()

    with tf.Session() as sess:
        sess.run(tf.initialize_all_variables())
        # Note, due to randomness in the policy the number of episodes you need to learn a good
        # policy may vary.
        stats, botstats = actor_critic(env, policy_estimator, value_estimator, 100)

    plotting.plot_episode_stats(stats, smoothing_window=1, title="Actor Critic")
    plotting.plot_bot_stats(botstats)